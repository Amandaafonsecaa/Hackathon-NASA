"""
Mock para osmnx - mantém a interface original mas sem dependências externas
"""
import networkx as nx
from typing import Dict, Any, Tuple, List
import numpy as np

class MockOSMnx:
    """Mock do OSMnx que mantém a interface original"""
    
    @staticmethod
    def graph_from_point(center_point: Tuple[float, float], 
                        dist: int = 1000, 
                        network_type: str = "drive") -> nx.MultiDiGraph:
        """Cria um grafo mock para testes"""
        G = nx.MultiDiGraph()
        
        # Adiciona alguns nós mock
        for i in range(10):
            lat = center_point[0] + (i - 5) * 0.01
            lon = center_point[1] + (i - 5) * 0.01
            G.add_node(i, x=lon, y=lat, osmid=i)
        
        # Adiciona algumas arestas mock
        for i in range(9):
            G.add_edge(i, i+1, length=100, osmid=f"{i}-{i+1}")
        
        return G
    
    @staticmethod
    def add_edge_lengths(G: nx.MultiDiGraph) -> nx.MultiDiGraph:
        """Adiciona comprimentos mock às arestas"""
        for u, v, key, data in G.edges(keys=True, data=True):
            if 'length' not in data:
                data['length'] = 100.0
        return G
    
    @staticmethod
    def add_edge_speeds(G: nx.MultiDiGraph) -> nx.MultiDiGraph:
        """Adiciona velocidades mock às arestas"""
        for u, v, key, data in G.edges(keys=True, data=True):
            data['speed_kph'] = 50.0
        return G
    
    @staticmethod
    def add_edge_travel_times(G: nx.MultiDiGraph) -> nx.MultiDiGraph:
        """Adiciona tempos de viagem mock às arestas"""
        for u, v, key, data in G.edges(keys=True, data=True):
            if 'length' in data and 'speed_kph' in data:
                data['travel_time'] = data['length'] / data['speed_kph'] * 3.6
            else:
                data['travel_time'] = 10.0
        return G
    
    @staticmethod
    def shortest_path(G: nx.MultiDiGraph, 
                     orig: int, 
                     dest: int, 
                     weight: str = "length") -> List[int]:
        """Calcula caminho mais curto mock"""
        if orig == dest:
            return [orig]
        
        # Algoritmo simples de caminho mais curto
        try:
            return nx.shortest_path(G, orig, dest, weight=weight)
        except:
            return [orig, dest]
    
    @staticmethod
    def shortest_path_length(G: nx.MultiDiGraph, 
                           orig: int, 
                           dest: int, 
                           weight: str = "length") -> float:
        """Calcula comprimento do caminho mais curto mock"""
        if orig == dest:
            return 0.0
        
        try:
            return nx.shortest_path_length(G, orig, dest, weight=weight)
        except:
            return 1000.0

# Criar instância mock
ox = MockOSMnx()
