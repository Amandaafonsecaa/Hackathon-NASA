"""
Controlador RL para sinais semafóricos e otimização de tráfego em tempo real.
Implementa DQN para controle adaptativo de semáforos.
"""

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
import random
from collections import deque
from typing import Dict, List, Tuple, Optional
import math
from dataclasses import dataclass
import json
import time

@dataclass
class IntersectionState:
    """Estado de uma interseção para RL."""
    queue_lengths: List[float]  # Comprimento das filas por direção
    flow_rates: List[float]     # Taxa de fluxo por direção
    waiting_times: List[float]  # Tempos de espera médios
    phase_duration: float       # Duração da fase atual
    time_of_day: float         # Hora do dia (0-24)
    weather_condition: int     # Condição meteorológica (0-3)

@dataclass
class TrafficLightAction:
    """Ação de controle do semáforo."""
    phase: int                 # Fase do semáforo (0-3)
    duration: float           # Duração da fase em segundos
    offset: float             # Offset em relação ao ciclo base

class DQN(nn.Module):
    """Rede neural Deep Q-Network para controle de semáforos."""
    
    def __init__(self, input_size: int, hidden_size: int = 128, output_size: int = 4):
        super(DQN, self).__init__()
        
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.fc2 = nn.Linear(hidden_size, hidden_size)
        self.fc3 = nn.Linear(hidden_size, hidden_size)
        self.fc4 = nn.Linear(hidden_size, output_size)
        
        self.dropout = nn.Dropout(0.2)
        self.relu = nn.ReLU()
        
    def forward(self, x):
        x = self.relu(self.fc1(x))
        x = self.dropout(x)
        x = self.relu(self.fc2(x))
        x = self.dropout(x)
        x = self.relu(self.fc3(x))
        x = self.fc4(x)
        return x

class TrafficRLController:
    """Controlador RL para otimização de semáforos."""
    
    def __init__(self, intersection_id: str, num_directions: int = 4):
        self.intersection_id = intersection_id
        self.num_directions = num_directions
        
        # Parâmetros DQN
        self.input_size = num_directions * 3 + 3  # filas + fluxos + tempos + hora + tempo_fase + clima
        self.output_size = num_directions  # fases possíveis
        self.hidden_size = 128
        
        # Redes neurais
        self.q_network = DQN(self.input_size, self.hidden_size, self.output_size)
        self.target_network = DQN(self.input_size, self.hidden_size, self.output_size)
        self.optimizer = optim.Adam(self.q_network.parameters(), lr=0.001)
        
        # Parâmetros de treinamento
        self.learning_rate = 0.001
        self.gamma = 0.95  # Fator de desconto
        self.epsilon = 1.0  # Exploração inicial
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995
        self.batch_size = 32
        self.memory_size = 10000
        
        # Memória de replay
        self.memory = deque(maxlen=self.memory_size)
        
        # Estado atual
        self.current_state = None
        self.current_action = 0
        self.last_reward = 0
        
        # Estatísticas
        self.episode_rewards = []
        self.loss_history = []
        
    def get_state_vector(self, state: IntersectionState) -> np.ndarray:
        """Converte estado da interseção em vetor para a rede neural."""
        # Normalizar dados
        normalized_queues = [q / 50.0 for q in state.queue_lengths]  # Assumir max 50 veículos
        normalized_flows = [f / 100.0 for f in state.flow_rates]     # Assumir max 100 veículos/min
        normalized_waiting = [w / 120.0 for w in state.waiting_times] # Assumir max 2 minutos
        
        # Features adicionais
        time_of_day = state.time_of_day / 24.0
        phase_duration = min(state.phase_duration / 60.0, 1.0)  # Normalizar para 1 minuto
        weather = state.weather_condition / 3.0
        
        # Concatenar todas as features
        state_vector = (
            normalized_queues + 
            normalized_flows + 
            normalized_waiting + 
            [time_of_day, phase_duration, weather]
        )
        
        return np.array(state_vector, dtype=np.float32)
    
    def select_action(self, state: IntersectionState, training: bool = True) -> int:
        """Seleciona ação usando epsilon-greedy."""
        state_vector = self.get_state_vector(state)
        
        if training and random.random() < self.epsilon:
            # Exploração aleatória
            action = random.randint(0, self.output_size - 1)
        else:
            # Exploração baseada na rede neural
            with torch.no_grad():
                state_tensor = torch.FloatTensor(state_vector).unsqueeze(0)
                q_values = self.q_network(state_tensor)
                action = q_values.argmax().item()
        
        return action
    
    def calculate_reward(self, 
                        current_state: IntersectionState, 
                        next_state: IntersectionState, 
                        action: int) -> float:
        """
        Calcula recompensa baseada em múltiplos fatores.
        
        Recompensa negativa para:
        - Filas longas
        - Tempos de espera altos
        - Overflow (capacidade excedida)
        
        Recompensa positiva para:
        - Fluxo eficiente
        - Filas reduzidas
        - Tempos de espera baixos
        """
        reward = 0.0
        
        # Penalidade por filas longas
        queue_penalty = -sum(current_state.queue_lengths) / 10.0
        
        # Penalidade por tempos de espera altos
        waiting_penalty = -sum(current_state.waiting_times) / 60.0
        
        # Recompensa por fluxo eficiente
        flow_reward = sum(current_state.flow_rates) / 100.0
        
        # Penalidade por mudança de fase desnecessária
        phase_change_penalty = -0.1 if action != self.current_action else 0.0
        
        # Recompensa por redução de filas
        queue_reduction = sum(current_state.queue_lengths) - sum(next_state.queue_lengths)
        queue_reduction_reward = queue_reduction / 10.0
        
        # Recompensa total
        reward = (
            queue_penalty + 
            waiting_penalty + 
            flow_reward + 
            phase_change_penalty + 
            queue_reduction_reward
        )
        
        return reward
    
    def remember(self, state: IntersectionState, action: int, reward: float, 
                 next_state: IntersectionState, done: bool):
        """Armazena experiência na memória de replay."""
        state_vector = self.get_state_vector(state)
        next_state_vector = self.get_state_vector(next_state)
        
        self.memory.append((
            state_vector, action, reward, next_state_vector, done
        ))
    
    def replay(self):
        """Treina a rede neural usando experiências armazenadas."""
        if len(self.memory) < self.batch_size:
            return
        
        # Amostrar batch aleatório
        batch = random.sample(self.memory, self.batch_size)
        
        states = torch.FloatTensor([e[0] for e in batch])
        actions = torch.LongTensor([e[1] for e in batch])
        rewards = torch.FloatTensor([e[2] for e in batch])
        next_states = torch.FloatTensor([e[3] for e in batch])
        dones = torch.BoolTensor([e[4] for e in batch])
        
        # Q-values atuais
        current_q_values = self.q_network(states).gather(1, actions.unsqueeze(1))
        
        # Q-values do próximo estado (target network)
        with torch.no_grad():
            next_q_values = self.target_network(next_states).max(1)[0]
            target_q_values = rewards + (self.gamma * next_q_values * ~dones)
        
        # Calcular perda
        loss = nn.MSELoss()(current_q_values.squeeze(), target_q_values)
        
        # Backpropagation
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
        
        # Decaimento do epsilon
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
        
        # Atualizar target network periodicamente
        if len(self.loss_history) % 100 == 0:
            self.target_network.load_state_dict(self.q_network.state_dict())
        
        self.loss_history.append(loss.item())
    
    def update_state(self, new_state: IntersectionState):
        """Atualiza estado atual e treina se necessário."""
        if self.current_state is not None:
            # Calcular recompensa
            reward = self.calculate_reward(self.current_state, new_state, self.current_action)
            
            # Armazenar experiência
            self.remember(self.current_state, self.current_action, reward, new_state, False)
            
            # Treinar
            self.replay()
        
        self.current_state = new_state
    
    def get_optimal_action(self, state: IntersectionState) -> TrafficLightAction:
        """Retorna ação otimizada para o estado atual."""
        action = self.select_action(state, training=True)
        self.current_action = action
        
        # Mapear ação para configuração do semáforo
        phase_duration = self._calculate_phase_duration(state, action)
        offset = self._calculate_offset(state, action)
        
        return TrafficLightAction(
            phase=action,
            duration=phase_duration,
            offset=offset
        )
    
    def _calculate_phase_duration(self, state: IntersectionState, action: int) -> float:
        """Calcula duração otimizada da fase."""
        base_duration = 30.0  # segundos
        
        # Ajustar baseado no comprimento das filas
        queue_factor = 1.0 + (state.queue_lengths[action] / 20.0)
        
        # Ajustar baseado no tempo de espera
        waiting_factor = 1.0 + (state.waiting_times[action] / 30.0)
        
        # Duração final
        duration = base_duration * queue_factor * waiting_factor
        
        # Limitar entre 15 e 90 segundos
        return max(15.0, min(90.0, duration))
    
    def _calculate_offset(self, state: IntersectionState, action: int) -> float:
        """Calcula offset para sincronização com semáforos vizinhos."""
        # Simplificado: offset baseado na hora do dia
        time_factor = math.sin(2 * math.pi * state.time_of_day / 24.0)
        offset = time_factor * 10.0  # ±10 segundos
        
        return offset
    
    def save_model(self, filepath: str):
        """Salva modelo treinado."""
        torch.save({
            'q_network_state_dict': self.q_network.state_dict(),
            'target_network_state_dict': self.target_network.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'epsilon': self.epsilon,
            'loss_history': self.loss_history,
            'episode_rewards': self.episode_rewards
        }, filepath)
    
    def load_model(self, filepath: str):
        """Carrega modelo treinado."""
        checkpoint = torch.load(filepath)
        self.q_network.load_state_dict(checkpoint['q_network_state_dict'])
        self.target_network.load_state_dict(checkpoint['target_network_state_dict'])
        self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        self.epsilon = checkpoint['epsilon']
        self.loss_history = checkpoint['loss_history']
        self.episode_rewards = checkpoint['episode_rewards']

class TrafficCoordinationSystem:
    """Sistema de coordenação entre múltiplos semáforos."""
    
    def __init__(self):
        self.intersections = {}
        self.coordination_network = None  # Grafo de coordenação entre semáforos
        
    def add_intersection(self, intersection_id: str, position: Tuple[float, float]):
        """Adiciona nova interseção ao sistema."""
        self.intersections[intersection_id] = TrafficRLController(intersection_id)
        
        # TODO: Atualizar rede de coordenação
        
    def update_intersection_state(self, intersection_id: str, state: IntersectionState):
        """Atualiza estado de uma interseção."""
        if intersection_id in self.intersections:
            self.intersections[intersection_id].update_state(state)
    
    def get_coordinated_actions(self, intersection_id: str, state: IntersectionState) -> TrafficLightAction:
        """Retorna ação coordenada considerando semáforos vizinhos."""
        if intersection_id not in self.intersections:
            return TrafficLightAction(phase=0, duration=30.0, offset=0.0)
        
        controller = self.intersections[intersection_id]
        action = controller.get_optimal_action(state)
        
        # Ajustar offset baseado em semáforos vizinhos
        action.offset = self._calculate_coordinated_offset(intersection_id, action.offset)
        
        return action
    
    def _calculate_coordinated_offset(self, intersection_id: str, base_offset: float) -> float:
        """Calcula offset coordenado com semáforos vizinhos."""
        # Simplificado: offset baseado na posição na rede
        # TODO: Implementar algoritmo de coordenação mais sofisticado
        
        return base_offset
    
    def simulate_traffic_scenario(self, duration_minutes: int = 60) -> Dict:
        """Simula cenário de tráfego para treinamento."""
        simulation_results = {}
        
        for intersection_id, controller in self.intersections.items():
            # Simular estado inicial
            initial_state = IntersectionState(
                queue_lengths=[10, 8, 12, 6],
                flow_rates=[20, 18, 25, 15],
                waiting_times=[30, 25, 35, 20],
                phase_duration=0,
                time_of_day=8.0,  # 8h da manhã
                weather_condition=0  # bom tempo
            )
            
            controller.current_state = initial_state
            episode_reward = 0
            
            for step in range(duration_minutes):
                # Simular mudanças no tráfego
                state = self._simulate_traffic_dynamics(initial_state, step)
                
                # Obter ação
                action = controller.get_optimal_action(state)
                
                # Simular próximo estado
                next_state = self._apply_action(state, action)
                
                # Calcular recompensa
                reward = controller.calculate_reward(state, next_state, action.phase)
                episode_reward += reward
                
                # Atualizar estado
                controller.current_state = next_state
            
            simulation_results[intersection_id] = {
                "episode_reward": episode_reward,
                "final_epsilon": controller.epsilon,
                "loss_history_length": len(controller.loss_history)
            }
        
        return simulation_results
    
    def _simulate_traffic_dynamics(self, base_state: IntersectionState, step: int) -> IntersectionState:
        """Simula dinâmica de tráfego ao longo do tempo."""
        # Variação baseada na hora do dia
        time_variation = 1.0 + 0.3 * math.sin(2 * math.pi * (step / 60.0 + 8) / 24)
        
        # Ruído aleatório
        noise = np.random.normal(1.0, 0.1, 4)
        
        new_queue_lengths = [q * time_variation * n for q, n in zip(base_state.queue_lengths, noise)]
        new_flow_rates = [f * time_variation * n for f, n in zip(base_state.flow_rates, noise)]
        new_waiting_times = [w * time_variation * n for w, n in zip(base_state.waiting_times, noise)]
        
        return IntersectionState(
            queue_lengths=new_queue_lengths,
            flow_rates=new_flow_rates,
            waiting_times=new_waiting_times,
            phase_duration=base_state.phase_duration + 1,
            time_of_day=(8.0 + step / 60.0) % 24.0,
            weather_condition=base_state.weather_condition
        )
    
    def _apply_action(self, state: IntersectionState, action: TrafficLightAction) -> IntersectionState:
        """Simula efeito de uma ação no tráfego."""
        # Simplificado: reduz filas na direção da fase ativa
        new_queue_lengths = state.queue_lengths.copy()
        new_waiting_times = state.waiting_times.copy()
        
        # Reduzir fila na direção ativa
        if new_queue_lengths[action.phase] > 0:
            reduction = min(5, new_queue_lengths[action.phase])
            new_queue_lengths[action.phase] -= reduction
            new_waiting_times[action.phase] = max(0, new_waiting_times[action.phase] - 10)
        
        # Aumentar filas em outras direções
        for i, (queue, waiting) in enumerate(zip(new_queue_lengths, new_waiting_times)):
            if i != action.phase:
                new_queue_lengths[i] += np.random.poisson(2)
                new_waiting_times[i] += 5
        
        return IntersectionState(
            queue_lengths=new_queue_lengths,
            flow_rates=state.flow_rates,
            waiting_times=new_waiting_times,
            phase_duration=action.duration,
            time_of_day=state.time_of_day,
            weather_condition=state.weather_condition
        )

# Instância global do sistema de coordenação
traffic_coordination = TrafficCoordinationSystem()
