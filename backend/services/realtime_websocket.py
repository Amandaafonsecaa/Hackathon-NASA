"""
Serviço WebSocket para atualizações em tempo real do sistema de evacuação.
Implementa comunicação bidirecional para telemetria e controle.
"""

import asyncio
import json
import time
from typing import Dict, List, Set, Optional, Any

try:
    from fastapi import WebSocket, WebSocketDisconnect
except ImportError:
    # Mock para FastAPI WebSocket
    class WebSocket:
        def __init__(self): pass
        async def accept(self): pass
        async def send_text(self, text): pass
        async def receive_text(self): return "{}"
        async def close(self): pass
    class WebSocketDisconnect(Exception): pass

from dataclasses import dataclass, asdict
from enum import Enum
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MessageType(Enum):
    """Tipos de mensagens WebSocket."""
    TRAFFIC_UPDATE = "traffic_update"
    EVACUATION_STATUS = "evacuation_status"
    ROUTE_UPDATE = "route_update"
    INCIDENT_ALERT = "incident_alert"
    BOTTLENECK_WARNING = "bottleneck_warning"
    SYSTEM_STATUS = "system_status"
    COMMAND = "command"
    HEARTBEAT = "heartbeat"

@dataclass
class WebSocketMessage:
    """Estrutura de mensagem WebSocket."""
    message_type: str
    timestamp: float
    data: Dict[str, Any]
    source: str = "traffic_ai_system"
    priority: str = "normal"  # low, normal, high, critical

class ConnectionManager:
    """Gerenciador de conexões WebSocket."""
    
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
        self.subscriptions: Dict[WebSocket, Set[str]] = {}
        self.last_heartbeat: Dict[WebSocket, float] = {}
        
    async def connect(self, websocket: WebSocket, client_id: str = None):
        """Conecta novo cliente WebSocket."""
        await websocket.accept()
        self.active_connections.add(websocket)
        self.subscriptions[websocket] = set()
        self.last_heartbeat[websocket] = time.time()
        
        logger.info(f"Cliente conectado: {client_id or 'anônimo'}")
        
        # Enviar mensagem de boas-vindas
        welcome_msg = WebSocketMessage(
            message_type=MessageType.SYSTEM_STATUS.value,
            timestamp=time.time(),
            data={
                "status": "connected",
                "client_id": client_id,
                "available_subscriptions": [
                    "traffic_updates",
                    "evacuation_status", 
                    "route_updates",
                    "incidents",
                    "bottlenecks"
                ]
            }
        )
        await self.send_personal_message(websocket, welcome_msg)
    
    def disconnect(self, websocket: WebSocket):
        """Desconecta cliente WebSocket."""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        if websocket in self.subscriptions:
            del self.subscriptions[websocket]
        if websocket in self.last_heartbeat:
            del self.last_heartbeat[websocket]
        
        logger.info("Cliente desconectado")
    
    async def send_personal_message(self, websocket: WebSocket, message: WebSocketMessage):
        """Envia mensagem para cliente específico."""
        try:
            await websocket.send_text(json.dumps(asdict(message)))
        except Exception as e:
            logger.error(f"Erro ao enviar mensagem: {e}")
            self.disconnect(websocket)
    
    async def broadcast(self, message: WebSocketMessage, subscription_type: str = None):
        """Envia mensagem para todos os clientes conectados."""
        disconnected = []
        
        for websocket in self.active_connections:
            try:
                # Verificar se cliente está inscrito no tipo de mensagem
                if subscription_type and websocket in self.subscriptions:
                    if subscription_type not in self.subscriptions[websocket]:
                        continue
                
                await websocket.send_text(json.dumps(asdict(message)))
            except Exception as e:
                logger.error(f"Erro ao enviar broadcast: {e}")
                disconnected.append(websocket)
        
        # Remover conexões com erro
        for websocket in disconnected:
            self.disconnect(websocket)
    
    def subscribe(self, websocket: WebSocket, subscription_type: str):
        """Inscreve cliente em tipo específico de mensagens."""
        if websocket in self.subscriptions:
            self.subscriptions[websocket].add(subscription_type)
            logger.info(f"Cliente inscrito em: {subscription_type}")
    
    def unsubscribe(self, websocket: WebSocket, subscription_type: str):
        """Desinscreve cliente de tipo específico de mensagens."""
        if websocket in self.subscriptions:
            self.subscriptions[websocket].discard(subscription_type)
            logger.info(f"Cliente desinscrito de: {subscription_type}")
    
    def update_heartbeat(self, websocket: WebSocket):
        """Atualiza heartbeat do cliente."""
        self.last_heartbeat[websocket] = time.time()
    
    async def cleanup_stale_connections(self, timeout_seconds: int = 300):
        """Remove conexões inativas."""
        current_time = time.time()
        stale_connections = []
        
        for websocket, last_heartbeat in self.last_heartbeat.items():
            if current_time - last_heartbeat > timeout_seconds:
                stale_connections.append(websocket)
        
        for websocket in stale_connections:
            logger.info("Removendo conexão inativa")
            self.disconnect(websocket)

class RealtimeTrafficService:
    """Serviço de atualizações em tempo real para tráfego."""
    
    def __init__(self):
        self.manager = ConnectionManager()
        self.traffic_data = {}
        self.evacuation_status = {}
        self.active_incidents = []
        self.bottlenecks = []
        self.update_interval = 5.0  # segundos
        self.is_running = False
        
    async def start_broadcast_loop(self):
        """Inicia loop de broadcast de atualizações."""
        self.is_running = True
        
        while self.is_running:
            try:
                # Atualizar dados de tráfego
                await self._update_traffic_data()
                
                # Broadcast de atualizações
                await self._broadcast_updates()
                
                # Limpeza de conexões inativas
                await self.manager.cleanup_stale_connections()
                
                await asyncio.sleep(self.update_interval)
                
            except Exception as e:
                logger.error(f"Erro no loop de broadcast: {e}")
                await asyncio.sleep(1)
    
    async def stop_broadcast_loop(self):
        """Para loop de broadcast."""
        self.is_running = False
    
    async def _update_traffic_data(self):
        """Atualiza dados de tráfego (simulado)."""
        current_time = time.time()
        
        # Simular dados de tráfego
        self.traffic_data = {
            "timestamp": current_time,
            "total_vehicles": 1250 + int(100 * (time.time() % 100)),
            "average_speed_kmh": 45 + int(10 * (time.time() % 50) / 50),
            "congestion_level": "medium",
            "active_incidents": len(self.active_incidents),
            "bottlenecks": len(self.bottlenecks)
        }
        
        # Simular status de evacuação
        self.evacuation_status = {
            "timestamp": current_time,
            "evacuation_active": True,
            "evacuated_population": 4500 + int(50 * (time.time() % 60)),
            "remaining_population": 1500 - int(30 * (time.time() % 60)),
            "evacuation_progress": 75.5,
            "estimated_completion_time": "2h 15min"
        }
        
        # Simular incidentes ocasionais
        if current_time % 300 < self.update_interval:  # A cada 5 minutos
            await self._simulate_incident()
        
        # Simular gargalos
        if current_time % 180 < self.update_interval:  # A cada 3 minutos
            await self._simulate_bottleneck()
    
    async def _simulate_incident(self):
        """Simula incidente de trânsito."""
        incident_types = ["acidente", "bloqueio", "obras", "incêndio"]
        incident_type = incident_types[int(time.time()) % len(incident_types)]
        
        incident = {
            "id": f"incident_{int(time.time())}",
            "type": incident_type,
            "location": {
                "latitude": -23.5505 + (time.time() % 100) / 10000,
                "longitude": -46.6333 + (time.time() % 100) / 10000
            },
            "severity": "medium",
            "timestamp": time.time(),
            "estimated_resolution": "45min"
        }
        
        self.active_incidents.append(incident)
        
        # Broadcast de alerta de incidente
        alert_msg = WebSocketMessage(
            message_type=MessageType.INCIDENT_ALERT.value,
            timestamp=time.time(),
            data=incident,
            priority="high"
        )
        await self.manager.broadcast(alert_msg, "incidents")
        
        logger.info(f"Novo incidente detectado: {incident_type}")
    
    async def _simulate_bottleneck(self):
        """Simula gargalo de trânsito."""
        bottleneck = {
            "id": f"bottleneck_{int(time.time())}",
            "location": {
                "latitude": -23.5505 + (time.time() % 200) / 10000,
                "longitude": -46.6333 + (time.time() % 200) / 10000
            },
            "utilization": 0.85 + (time.time() % 20) / 100,
            "queue_length_km": 2.5 + (time.time() % 50) / 20,
            "estimated_delay_minutes": 15 + int(time.time() % 30),
            "timestamp": time.time()
        }
        
        self.bottlenecks.append(bottleneck)
        
        # Broadcast de alerta de gargalo
        warning_msg = WebSocketMessage(
            message_type=MessageType.BOTTLENECK_WARNING.value,
            timestamp=time.time(),
            data=bottleneck,
            priority="normal"
        )
        await self.manager.broadcast(warning_msg, "bottlenecks")
        
        logger.info(f"Gargalo detectado: utilização {bottleneck['utilization']:.2%}")
    
    async def _broadcast_updates(self):
        """Faz broadcast de atualizações para clientes inscritos."""
        # Atualização de tráfego
        traffic_msg = WebSocketMessage(
            message_type=MessageType.TRAFFIC_UPDATE.value,
            timestamp=time.time(),
            data=self.traffic_data
        )
        await self.manager.broadcast(traffic_msg, "traffic_updates")
        
        # Atualização de status de evacuação
        evacuation_msg = WebSocketMessage(
            message_type=MessageType.EVACUATION_STATUS.value,
            timestamp=time.time(),
            data=self.evacuation_status
        )
        await self.manager.broadcast(evacuation_msg, "evacuation_status")
    
    async def handle_client_message(self, websocket: WebSocket, message_data: Dict):
        """Processa mensagem recebida do cliente."""
        try:
            message_type = message_data.get("type")
            data = message_data.get("data", {})
            
            if message_type == "subscribe":
                subscription_type = data.get("subscription_type")
                if subscription_type:
                    self.manager.subscribe(websocket, subscription_type)
                    
                    # Enviar confirmação
                    confirm_msg = WebSocketMessage(
                        message_type=MessageType.SYSTEM_STATUS.value,
                        timestamp=time.time(),
                        data={
                            "status": "subscribed",
                            "subscription_type": subscription_type
                        }
                    )
                    await self.manager.send_personal_message(websocket, confirm_msg)
            
            elif message_type == "unsubscribe":
                subscription_type = data.get("subscription_type")
                if subscription_type:
                    self.manager.unsubscribe(websocket, subscription_type)
            
            elif message_type == "heartbeat":
                self.manager.update_heartbeat(websocket)
                
                # Responder com heartbeat
                heartbeat_msg = WebSocketMessage(
                    message_type=MessageType.HEARTBEAT.value,
                    timestamp=time.time(),
                    data={"status": "alive"}
                )
                await self.manager.send_personal_message(websocket, heartbeat_msg)
            
            elif message_type == "command":
                await self._handle_command(websocket, data)
            
        except Exception as e:
            logger.error(f"Erro ao processar mensagem do cliente: {e}")
    
    async def _handle_command(self, websocket: WebSocket, command_data: Dict):
        """Processa comandos do cliente."""
        command = command_data.get("command")
        
        if command == "get_status":
            status_msg = WebSocketMessage(
                message_type=MessageType.SYSTEM_STATUS.value,
                timestamp=time.time(),
                data={
                    "traffic_data": self.traffic_data,
                    "evacuation_status": self.evacuation_status,
                    "active_incidents": self.active_incidents,
                    "bottlenecks": self.bottlenecks,
                    "active_connections": len(self.manager.active_connections)
                }
            )
            await self.manager.send_personal_message(websocket, status_msg)
        
        elif command == "clear_incidents":
            self.active_incidents.clear()
            
            clear_msg = WebSocketMessage(
                message_type=MessageType.SYSTEM_STATUS.value,
                timestamp=time.time(),
                data={"message": "Incidentes limpos", "incidents_cleared": True}
            )
            await self.manager.send_personal_message(websocket, clear_msg)
        
        elif command == "update_interval":
            new_interval = command_data.get("interval", 5.0)
            self.update_interval = max(1.0, min(60.0, new_interval))
            
            interval_msg = WebSocketMessage(
                message_type=MessageType.SYSTEM_STATUS.value,
                timestamp=time.time(),
                data={
                    "message": f"Intervalo atualizado para {new_interval}s",
                    "new_interval": self.update_interval
                }
            )
            await self.manager.send_personal_message(websocket, interval_msg)
    
    async def send_route_update(self, route_data: Dict):
        """Envia atualização de rota específica."""
        route_msg = WebSocketMessage(
            message_type=MessageType.ROUTE_UPDATE.value,
            timestamp=time.time(),
            data=route_data,
            priority="high"
        )
        await self.manager.broadcast(route_msg, "route_updates")
    
    async def send_emergency_alert(self, alert_data: Dict):
        """Envia alerta de emergência."""
        alert_msg = WebSocketMessage(
            message_type=MessageType.INCIDENT_ALERT.value,
            timestamp=time.time(),
            data=alert_data,
            priority="critical"
        )
        await self.manager.broadcast(alert_msg)
    
    def get_connection_stats(self) -> Dict:
        """Retorna estatísticas de conexões."""
        return {
            "active_connections": len(self.manager.active_connections),
            "total_subscriptions": sum(len(subs) for subs in self.manager.subscriptions.values()),
            "update_interval": self.update_interval,
            "is_broadcasting": self.is_running,
            "active_incidents": len(self.active_incidents),
            "bottlenecks": len(self.bottlenecks)
        }

# Instância global do serviço
realtime_service = RealtimeTrafficService()
