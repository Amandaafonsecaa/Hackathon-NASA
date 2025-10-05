"""
Configurações para o sistema de IA de evacuação.
Parâmetros ajustáveis para otimização de performance.
"""

from dataclasses import dataclass
from typing import Dict, List, Tuple

@dataclass
class BPRConfig:
    """Configurações da função BPR."""
    alpha: float = 0.15  # Parâmetro de sensibilidade
    beta: float = 4.0    # Expoente da função
    max_utilization: float = 1.2  # Utilização máxima permitida

@dataclass
class FrankWolfeConfig:
    """Configurações do algoritmo Frank-Wolfe."""
    max_iterations: int = 50
    convergence_threshold: float = 0.001
    line_search_method: str = "bounded"  # bounded, golden
    step_size_min: float = 0.0
    step_size_max: float = 1.0

@dataclass
class MLConfig:
    """Configurações do modelo ML."""
    model_type: str = "GradientBoostingRegressor"
    n_estimators: int = 100
    learning_rate: float = 0.1
    max_depth: int = 6
    random_state: int = 42
    train_test_split: float = 0.8
    synthetic_samples: int = 10000
    features: List[str] = None
    
    def __post_init__(self):
        if self.features is None:
            self.features = [
                "hour", "rainfall", "visibility", "wind_speed",
                "grade", "surface_type", "lanes"
            ]

@dataclass
class RLConfig:
    """Configurações do controlador RL."""
    network_type: str = "DQN"
    hidden_size: int = 128
    learning_rate: float = 0.001
    gamma: float = 0.95  # Fator de desconto
    epsilon_start: float = 1.0
    epsilon_min: float = 0.01
    epsilon_decay: float = 0.995
    batch_size: int = 32
    memory_size: int = 10000
    target_update_frequency: int = 100

@dataclass
class NetworkConfig:
    """Configurações da rede viária."""
    default_radius_km: float = 10.0
    network_type: str = "drive"  # drive, walk, bike, all
    simplify: bool = True
    cache_enabled: bool = True
    
    # Capacidades por tipo de via (veículos/hora)
    capacity_per_lane: Dict[str, int] = None
    
    # Velocidades por tipo de via (km/h)
    speed_limits: Dict[str, float] = None
    
    def __post_init__(self):
        if self.capacity_per_lane is None:
            self.capacity_per_lane = {
                'motorway': 2000,
                'trunk': 1800,
                'primary': 1500,
                'secondary': 1200,
                'tertiary': 1000,
                'residential': 800,
                'unclassified': 900
            }
        
        if self.speed_limits is None:
            self.speed_limits = {
                'motorway': 120,
                'trunk': 100,
                'primary': 80,
                'secondary': 60,
                'tertiary': 50,
                'residential': 30,
                'unclassified': 40
            }

@dataclass
class RealtimeConfig:
    """Configurações do sistema em tempo real."""
    update_interval: float = 5.0  # segundos
    heartbeat_timeout: float = 300.0  # segundos
    max_connections: int = 1000
    message_queue_size: int = 10000
    
    # Tipos de mensagem disponíveis
    message_types: List[str] = None
    
    def __post_init__(self):
        if self.message_types is None:
            self.message_types = [
                "traffic_updates",
                "evacuation_status",
                "route_updates",
                "incidents",
                "bottlenecks",
                "system_status"
            ]

@dataclass
class EvacuationConfig:
    """Configurações específicas de evacuação."""
    default_evacuation_radius_km: float = 20.0
    risk_penalty_multiplier: float = 15.0
    max_evacuation_distance_km: float = 100.0
    
    # Modos de transporte
    transport_modes: Dict[str, Dict] = None
    
    def __post_init__(self):
        if self.transport_modes is None:
            self.transport_modes = {
                "car": {
                    "speed_kmh": 60,
                    "max_distance_km": 100,
                    "route_precision": 0.5,
                    "priority_weights": {"distance": 0.4, "time": 0.4, "safety": 0.2}
                },
                "ambulance": {
                    "speed_kmh": 80,
                    "max_distance_km": 50,
                    "route_precision": 0.3,
                    "priority_weights": {"distance": 0.3, "time": 0.5, "safety": 0.2}
                },
                "pedestrian": {
                    "speed_kmh": 5,
                    "max_distance_km": 10,
                    "route_precision": 0.1,
                    "priority_weights": {"distance": 0.5, "time": 0.3, "safety": 0.2}
                }
            }

@dataclass
class AIConfig:
    """Configuração principal do sistema de IA."""
    bpr: BPRConfig = None
    frank_wolfe: FrankWolfeConfig = None
    ml: MLConfig = None
    rl: RLConfig = None
    network: NetworkConfig = None
    realtime: RealtimeConfig = None
    evacuation: EvacuationConfig = None
    
    def __post_init__(self):
        if self.bpr is None:
            self.bpr = BPRConfig()
        if self.frank_wolfe is None:
            self.frank_wolfe = FrankWolfeConfig()
        if self.ml is None:
            self.ml = MLConfig()
        if self.rl is None:
            self.rl = RLConfig()
        if self.network is None:
            self.network = NetworkConfig()
        if self.realtime is None:
            self.realtime = RealtimeConfig()
        if self.evacuation is None:
            self.evacuation = EvacuationConfig()

# Configuração padrão
DEFAULT_CONFIG = AIConfig()

# Configurações otimizadas para diferentes cenários
OPTIMIZED_CONFIGS = {
    "high_performance": AIConfig(
        frank_wolfe=FrankWolfeConfig(
            max_iterations=100,
            convergence_threshold=0.0001
        ),
        ml=MLConfig(
            n_estimators=200,
            learning_rate=0.05,
            max_depth=8
        ),
        realtime=RealtimeConfig(
            update_interval=2.0
        )
    ),
    
    "fast_execution": AIConfig(
        frank_wolfe=FrankWolfeConfig(
            max_iterations=25,
            convergence_threshold=0.01
        ),
        ml=MLConfig(
            n_estimators=50,
            learning_rate=0.2,
            max_depth=4
        ),
        realtime=RealtimeConfig(
            update_interval=10.0
        )
    ),
    
    "accuracy_focused": AIConfig(
        frank_wolfe=FrankWolfeConfig(
            max_iterations=200,
            convergence_threshold=0.00001
        ),
        ml=MLConfig(
            n_estimators=500,
            learning_rate=0.01,
            max_depth=10
        ),
        realtime=RealtimeConfig(
            update_interval=1.0
        )
    )
}

def get_config(config_name: str = "default") -> AIConfig:
    """Retorna configuração específica."""
    if config_name == "default":
        return DEFAULT_CONFIG
    elif config_name in OPTIMIZED_CONFIGS:
        return OPTIMIZED_CONFIGS[config_name]
    else:
        raise ValueError(f"Configuração '{config_name}' não encontrada")

def update_config(config: AIConfig, updates: Dict) -> AIConfig:
    """Atualiza configuração com novos valores."""
    for key, value in updates.items():
        if hasattr(config, key):
            setattr(config, key, value)
        else:
            raise ValueError(f"Configuração '{key}' não existe")
    return config
