"""
Router para WebSocket de atualizações em tempo real.
Implementa endpoints WebSocket para telemetria e controle em tempo real.
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, HTTPException
from typing import Dict, List, Optional
import json
import asyncio
import logging
from services.realtime_websocket import realtime_service, WebSocketMessage, MessageType

logger = logging.getLogger(__name__)
router = APIRouter()

@router.websocket("/ws/traffic")
async def websocket_traffic_updates(websocket: WebSocket, client_id: str = Query(None)):
    """
    WebSocket para atualizações de tráfego em tempo real.
    
    Tipos de mensagens suportados:
    - traffic_updates: Dados gerais de tráfego
    - evacuation_status: Status da evacuação
    - route_updates: Atualizações de rotas
    - incidents: Alertas de incidentes
    - bottlenecks: Avisos de gargalos
    - system_status: Status do sistema
    
    Comandos do cliente:
    - subscribe: Inscrever em tipo específico
    - unsubscribe: Desinscrever de tipo específico
    - heartbeat: Manter conexão ativa
    - command: Executar comando do sistema
    """
    await realtime_service.manager.connect(websocket, client_id)
    
    try:
        while True:
            # Receber mensagem do cliente
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Processar mensagem
            await realtime_service.handle_client_message(websocket, message_data)
            
    except WebSocketDisconnect:
        realtime_service.manager.disconnect(websocket)
        logger.info(f"Cliente {client_id or 'anônimo'} desconectado")
    except Exception as e:
        logger.error(f"Erro na conexão WebSocket: {e}")
        realtime_service.manager.disconnect(websocket)

@router.websocket("/ws/evacuation")
async def websocket_evacuation_updates(websocket: WebSocket, client_id: str = Query(None)):
    """
    WebSocket específico para atualizações de evacuação.
    
    Focado em:
    - Progresso da evacuação
    - Mudanças de rotas
    - Alertas críticos
    - Status de abrigos
    """
    await realtime_service.manager.connect(websocket, client_id)
    
    # Inscrever automaticamente em atualizações de evacuação
    realtime_service.manager.subscribe(websocket, "evacuation_status")
    realtime_service.manager.subscribe(websocket, "route_updates")
    realtime_service.manager.subscribe(websocket, "incidents")
    
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Processar mensagem
            await realtime_service.handle_client_message(websocket, message_data)
            
    except WebSocketDisconnect:
        realtime_service.manager.disconnect(websocket)
        logger.info(f"Cliente evacuação {client_id or 'anônimo'} desconectado")

@router.websocket("/ws/control")
async def websocket_control_center(websocket: WebSocket, client_id: str = Query(None)):
    """
    WebSocket para centro de controle com acesso completo.
    
    Inclui:
    - Todas as atualizações
    - Comandos de controle
    - Telemetria detalhada
    - Alertas críticos
    """
    await realtime_service.manager.connect(websocket, client_id)
    
    # Inscrever em todos os tipos
    all_subscriptions = [
        "traffic_updates",
        "evacuation_status", 
        "route_updates",
        "incidents",
        "bottlenecks"
    ]
    
    for subscription in all_subscriptions:
        realtime_service.manager.subscribe(websocket, subscription)
    
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Processar mensagem
            await realtime_service.handle_client_message(websocket, message_data)
            
    except WebSocketDisconnect:
        realtime_service.manager.disconnect(websocket)
        logger.info(f"Centro de controle {client_id or 'anônimo'} desconectado")

@router.post("/ws/broadcast", summary="Enviar mensagem para todos os clientes conectados")
async def broadcast_message(
    message_type: str,
    data: Dict,
    subscription_type: Optional[str] = None,
    priority: str = "normal"
):
    """
    Envia mensagem para todos os clientes WebSocket conectados.
    
    Args:
        message_type: Tipo da mensagem (traffic_update, incident_alert, etc.)
        data: Dados da mensagem
        subscription_type: Tipo de inscrição para filtrar clientes (opcional)
        priority: Prioridade da mensagem (low, normal, high, critical)
    """
    try:
        message = WebSocketMessage(
            message_type=message_type,
            timestamp=asyncio.get_event_loop().time(),
            data=data,
            priority=priority
        )
        
        await realtime_service.manager.broadcast(message, subscription_type)
        
        return {
            "success": True,
            "message": "Mensagem enviada com sucesso",
            "recipients": len(realtime_service.manager.active_connections),
            "message_type": message_type,
            "priority": priority
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao enviar mensagem: {str(e)}")

@router.post("/ws/route-update", summary="Enviar atualização de rota específica")
async def send_route_update(route_data: Dict):
    """
    Envia atualização de rota para clientes inscritos.
    
    Args:
        route_data: Dados da rota atualizada
    """
    try:
        await realtime_service.send_route_update(route_data)
        
        return {
            "success": True,
            "message": "Atualização de rota enviada",
            "route_id": route_data.get("route_id", "unknown")
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao enviar atualização de rota: {str(e)}")

@router.post("/ws/emergency-alert", summary="Enviar alerta de emergência")
async def send_emergency_alert(alert_data: Dict):
    """
    Envia alerta de emergência para todos os clientes.
    
    Args:
        alert_data: Dados do alerta de emergência
    """
    try:
        await realtime_service.send_emergency_alert(alert_data)
        
        return {
            "success": True,
            "message": "Alerta de emergência enviado",
            "alert_type": alert_data.get("type", "unknown"),
            "severity": alert_data.get("severity", "high")
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao enviar alerta: {str(e)}")

@router.get("/ws/connections", summary="Obter estatísticas de conexões WebSocket")
def get_connection_stats() -> Dict:
    """
    Retorna estatísticas das conexões WebSocket ativas.
    """
    try:
        stats = realtime_service.get_connection_stats()
        
        return {
            "success": True,
            "connection_stats": stats
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter estatísticas: {str(e)}")

@router.post("/ws/start-broadcast", summary="Iniciar loop de broadcast de atualizações")
async def start_broadcast_loop():
    """
    Inicia o loop de broadcast de atualizações em tempo real.
    """
    try:
        if not realtime_service.is_running:
            # Iniciar loop em background
            asyncio.create_task(realtime_service.start_broadcast_loop())
            
            return {
                "success": True,
                "message": "Loop de broadcast iniciado",
                "update_interval": realtime_service.update_interval
            }
        else:
            return {
                "success": True,
                "message": "Loop de broadcast já está rodando",
                "update_interval": realtime_service.update_interval
            }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao iniciar broadcast: {str(e)}")

@router.post("/ws/stop-broadcast", summary="Parar loop de broadcast")
async def stop_broadcast_loop():
    """
    Para o loop de broadcast de atualizações.
    """
    try:
        await realtime_service.stop_broadcast_loop()
        
        return {
            "success": True,
            "message": "Loop de broadcast parado"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao parar broadcast: {str(e)}")

@router.post("/ws/update-interval", summary="Atualizar intervalo de broadcast")
def update_broadcast_interval(interval_seconds: float = Query(..., ge=1.0, le=60.0)):
    """
    Atualiza o intervalo de broadcast de atualizações.
    
    Args:
        interval_seconds: Novo intervalo em segundos (1-60)
    """
    try:
        realtime_service.update_interval = interval_seconds
        
        return {
            "success": True,
            "message": f"Intervalo atualizado para {interval_seconds}s",
            "new_interval": interval_seconds
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar intervalo: {str(e)}")

@router.get("/ws/subscriptions", summary="Listar tipos de inscrição disponíveis")
def get_available_subscriptions() -> Dict:
    """
    Retorna lista de tipos de inscrição disponíveis para WebSocket.
    """
    subscriptions = {
        "traffic_updates": {
            "description": "Atualizações gerais de tráfego",
            "frequency": "5s",
            "data_types": ["congestion", "speed", "volume"]
        },
        "evacuation_status": {
            "description": "Status da evacuação em tempo real",
            "frequency": "10s",
            "data_types": ["progress", "population", "shelters"]
        },
        "route_updates": {
            "description": "Atualizações de rotas de evacuação",
            "frequency": "event-driven",
            "data_types": ["route_changes", "optimization", "rerouting"]
        },
        "incidents": {
            "description": "Alertas de incidentes e bloqueios",
            "frequency": "event-driven",
            "data_types": ["accidents", "blockages", "hazards"]
        },
        "bottlenecks": {
            "description": "Avisos de gargalos de tráfego",
            "frequency": "event-driven",
            "data_types": ["congestion", "queues", "delays"]
        }
    }
    
    return {
        "success": True,
        "available_subscriptions": subscriptions,
        "total_types": len(subscriptions)
    }

@router.get("/ws/client-example", summary="Exemplo de cliente WebSocket")
def get_client_example() -> Dict:
    """
    Retorna exemplo de código para cliente WebSocket.
    """
    example_code = {
        "javascript": """
// Exemplo de cliente WebSocket em JavaScript
const ws = new WebSocket('ws://localhost:8001/api/v1/ws/traffic?client_id=my_client');

ws.onopen = function() {
    console.log('Conectado ao WebSocket');
    
    // Inscrever em atualizações de tráfego
    ws.send(JSON.stringify({
        type: 'subscribe',
        data: { subscription_type: 'traffic_updates' }
    }));
    
    // Enviar heartbeat
    setInterval(() => {
        ws.send(JSON.stringify({
            type: 'heartbeat',
            data: {}
        }));
    }, 30000);
};

ws.onmessage = function(event) {
    const message = JSON.parse(event.data);
    console.log('Mensagem recebida:', message);
    
    // Processar diferentes tipos de mensagem
    switch(message.message_type) {
        case 'traffic_update':
            updateTrafficDisplay(message.data);
            break;
        case 'incident_alert':
            showIncidentAlert(message.data);
            break;
        case 'bottleneck_warning':
            showBottleneckWarning(message.data);
            break;
    }
};

ws.onclose = function() {
    console.log('Conexão WebSocket fechada');
};

ws.onerror = function(error) {
    console.error('Erro WebSocket:', error);
};
        """,
        "python": """
# Exemplo de cliente WebSocket em Python
import asyncio
import websockets
import json

async def websocket_client():
    uri = "ws://localhost:8001/api/v1/ws/traffic?client_id=python_client"
    
    async with websockets.connect(uri) as websocket:
        # Inscrever em atualizações
        await websocket.send(json.dumps({
            "type": "subscribe",
            "data": {"subscription_type": "traffic_updates"}
        }))
        
        # Enviar heartbeat
        async def heartbeat():
            while True:
                await websocket.send(json.dumps({
                    "type": "heartbeat",
                    "data": {}
                }))
                await asyncio.sleep(30)
        
        # Iniciar heartbeat em background
        heartbeat_task = asyncio.create_task(heartbeat())
        
        try:
            async for message in websocket:
                data = json.loads(message)
                print(f"Mensagem recebida: {data['message_type']}")
                
                # Processar mensagem
                if data['message_type'] == 'traffic_update':
                    print(f"Tráfego: {data['data']['total_vehicles']} veículos")
                elif data['message_type'] == 'incident_alert':
                    print(f"Incidente: {data['data']['type']}")
        
        finally:
            heartbeat_task.cancel()

# Executar cliente
asyncio.run(websocket_client())
        """
    }
    
    return {
        "success": True,
        "client_examples": example_code,
        "websocket_endpoints": [
            "/ws/traffic - Atualizações gerais de tráfego",
            "/ws/evacuation - Atualizações específicas de evacuação", 
            "/ws/control - Centro de controle com acesso completo"
        ]
    }
