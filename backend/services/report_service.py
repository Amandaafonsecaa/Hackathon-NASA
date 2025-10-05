"""
Serviço para geração de relatórios executivos em PDF.
"""

import io
from datetime import datetime
from typing import Dict, List, Optional
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import black, red, blue, green, orange
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.graphics.shapes import Drawing, Rect, Circle
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.piecharts import Pie
from reportlab.lib import colors

def generate_executive_report(
    impact_simulation: Dict,
    risk_zones_geojson: Dict,
    evacuation_analysis: Dict,
    asteroid_info: Optional[Dict] = None,
    impact_coordinates: Optional[List[float]] = None
) -> bytes:
    """
    Gera um relatório executivo completo em PDF.
    
    Args:
        impact_simulation: Resultados da simulação de impacto
        risk_zones_geojson: Zonas de risco em formato GeoJSON
        evacuation_analysis: Análise de evacuação
        asteroid_info: Informações do asteroide (opcional)
        impact_coordinates: Coordenadas do impacto [lon, lat] (opcional)
    
    Returns:
        Bytes do arquivo PDF gerado
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
    
    # Estilos
    styles = getSampleStyleSheet()
    
    # Estilos customizados
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        alignment=TA_CENTER,
        textColor=red
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        spaceAfter=12,
        textColor=blue
    )
    
    subheading_style = ParagraphStyle(
        'CustomSubHeading',
        parent=styles['Heading3'],
        fontSize=14,
        spaceAfter=8,
        textColor=green
    )
    
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=6,
        alignment=TA_JUSTIFY
    )
    
    # Conteúdo do relatório
    story = []
    
    # Cabeçalho
    story.append(Paragraph("RELATÓRIO EXECUTIVO DE ANÁLISE DE IMPACTO", title_style))
    story.append(Paragraph("Plataforma Governamental de Suporte à Decisão", styles['Heading2']))
    story.append(Paragraph("Gestão de Crises de Impacto de Asteroides", styles['Heading2']))
    story.append(Spacer(1, 20))
    
    # Data e hora
    current_time = datetime.now().strftime("%d/%m/%Y às %H:%M")
    story.append(Paragraph(f"<b>Data de Geração:</b> {current_time}", body_style))
    story.append(Spacer(1, 20))
    
    # Resumo Executivo
    story.append(Paragraph("RESUMO EXECUTIVO", heading_style))
    story.append(_generate_executive_summary(impact_simulation, risk_zones_geojson, evacuation_analysis, body_style))
    story.append(Spacer(1, 20))
    
    # Informações do Asteroide (se disponível)
    if asteroid_info:
        story.append(Paragraph("INFORMAÇÕES DO ASTEROIDE", heading_style))
        story.append(_generate_asteroid_info_section(asteroid_info, body_style))
        story.append(Spacer(1, 20))
    
    # Análise de Impacto
    story.append(Paragraph("ANÁLISE DE IMPACTO", heading_style))
    story.append(_generate_impact_analysis_section(impact_simulation, body_style, subheading_style))
    story.append(Spacer(1, 20))
    
    # Zonas de Risco
    story.append(Paragraph("ZONAS DE RISCO IDENTIFICADAS", heading_style))
    story.append(_generate_risk_zones_section(risk_zones_geojson, body_style, subheading_style))
    story.append(Spacer(1, 20))
    
    # Plano de Evacuação
    story.append(Paragraph("PLANO DE EVACUAÇÃO", heading_style))
    story.append(_generate_evacuation_section(evacuation_analysis, body_style, subheading_style))
    story.append(Spacer(1, 20))
    
    # Recomendações
    story.append(Paragraph("RECOMENDAÇÕES", heading_style))
    story.append(_generate_recommendations_section(impact_simulation, risk_zones_geojson, evacuation_analysis, body_style))
    story.append(Spacer(1, 20))
    
    # Anexos Técnicos
    story.append(Paragraph("ANEXOS TÉCNICOS", heading_style))
    story.append(_generate_technical_annexes(impact_simulation, body_style, subheading_style))
    
    # Construir PDF
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

def _generate_executive_summary(
    impact_simulation: Dict,
    risk_zones_geojson: Dict,
    evacuation_analysis: Dict,
    body_style: ParagraphStyle
) -> List:
    """Gera o resumo executivo do relatório."""
    story = []
    
    # Energia do impacto
    energy_megatons = impact_simulation.get("energia", {}).get("equivalente_tnt_megatons", 0)
    crater_diameter = impact_simulation.get("cratera", {}).get("diametro_final_km", 0)
    earthquake_magnitude = impact_simulation.get("terremoto", {}).get("magnitude_richter", 0)
    
    # Contagem de zonas de risco
    risk_zones_count = len(risk_zones_geojson.get("features", []))
    
    # Estatísticas de evacuação
    evacuation_stats = evacuation_analysis.get("statistics", {})
    total_routes = evacuation_stats.get("total_routes", 0)
    avg_distance = evacuation_stats.get("average_distance_km", 0)
    avg_time = evacuation_stats.get("average_time_hours", 0)
    
    summary_text = f"""
    Este relatório apresenta uma análise completa de impacto de asteroide com energia equivalente a 
    <b>{energy_megatons:.2f} megatons de TNT</b>. O impacto resultaria em uma cratera de aproximadamente 
    <b>{crater_diameter:.2f} km de diâmetro</b> e geraria um terremoto de magnitude <b>{earthquake_magnitude}</b> 
    na escala Richter.
    
    <br/><br/>
    
    Foram identificadas <b>{risk_zones_count} zonas de risco distintas</b>, incluindo cratera, ondas de choque, 
    queimaduras térmicas e efeitos sísmicos. O sistema calculou <b>{total_routes} rotas de evacuação</b> 
    com distância média de <b>{avg_distance:.1f} km</b> e tempo médio de evacuação de <b>{avg_time:.1f} horas</b>.
    
    <br/><br/>
    
    <b>Nível de Criticidade:</b> {_assess_criticality_level(energy_megatons, crater_diameter)}
    """
    
    story.append(Paragraph(summary_text, body_style))
    return story

def _generate_asteroid_info_section(asteroid_info: Dict, body_style: ParagraphStyle) -> List:
    """Gera seção com informações do asteroide."""
    story = []
    
    name = asteroid_info.get("name", "Desconhecido")
    diameter = asteroid_info.get("diameter_m", 0)
    is_hazardous = asteroid_info.get("is_potentially_hazardous", False)
    classification = asteroid_info.get("classification", {})
    
    hazardous_text = "SIM" if is_hazardous else "NÃO"
    hazardous_color = red if is_hazardous else green
    
    info_text = f"""
    <b>Nome:</b> {name}<br/>
    <b>Diâmetro:</b> {diameter:.1f} metros<br/>
    <b>Potencialmente Perigoso:</b> <font color="{hazardous_color}">{hazardous_text}</font><br/>
    <b>Classificação Orbital:</b> {classification.get('orbit_class', 'Desconhecida')}<br/>
    <b>Tipo de Objeto:</b> {classification.get('object_type', 'Desconhecido')}
    """
    
    story.append(Paragraph(info_text, body_style))
    return story

def _generate_impact_analysis_section(
    impact_simulation: Dict,
    body_style: ParagraphStyle,
    subheading_style: ParagraphStyle
) -> List:
    """Gera seção de análise de impacto."""
    story = []
    
    # Energia
    energy_data = impact_simulation.get("energia", {})
    story.append(Paragraph("Energia do Impacto", subheading_style))
    
    energy_table_data = [
        ["Parâmetro", "Valor"],
        ["Energia Total", f"{energy_data.get('energia_total_joules', 'N/A')} J"],
        ["Equivalente em TNT", f"{energy_data.get('equivalente_tnt_megatons', 0):.2f} megatons"],
        ["Equivalente em Bombas de Hiroshima", f"{energy_data.get('equivalente_bombas_hiroshima', 0)}"]
    ]
    
    energy_table = Table(energy_table_data, colWidths=[3*inch, 2*inch])
    energy_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(energy_table)
    story.append(Spacer(1, 12))
    
    # Cratera
    crater_data = impact_simulation.get("cratera", {})
    story.append(Paragraph("Formação da Cratera", subheading_style))
    
    crater_text = f"""
    <b>Diâmetro Final:</b> {crater_data.get('diametro_final_km', 0):.2f} km<br/>
    <b>Profundidade:</b> {crater_data.get('profundidade_m', 0):.1f} metros<br/>
    <b>Área Afetada:</b> {_calculate_crater_area(crater_data.get('diametro_final_km', 0)):.2f} km²
    """
    
    story.append(Paragraph(crater_text, body_style))
    story.append(Spacer(1, 12))
    
    # Efeitos Secundários
    story.append(Paragraph("Efeitos Secundários", subheading_style))
    
    # Terremoto
    earthquake_data = impact_simulation.get("terremoto", {})
    earthquake_text = f"""
    <b>Terremoto:</b> Magnitude {earthquake_data.get('magnitude_richter', 0)} na escala Richter<br/>
    <b>Distância Sentida:</b> Até {earthquake_data.get('distancia_sentida_km', 0):.0f} km do epicentro
    """
    
    story.append(Paragraph(earthquake_text, body_style))
    
    # Tsunami (se aplicável)
    tsunami_data = impact_simulation.get("tsunami", {})
    if tsunami_data.get("tsunami_generated"):
        tsunami_text = f"""
        <br/><b>Tsunami:</b> Altura inicial de {tsunami_data.get('initial_wave_height_m', 0):.1f} m<br/>
        <b>Runup Máximo:</b> {tsunami_data.get('max_runup_m', 0):.1f} m na costa
        """
        story.append(Paragraph(tsunami_text, body_style))
    
    return story

def _generate_risk_zones_section(
    risk_zones_geojson: Dict,
    body_style: ParagraphStyle,
    subheading_style: ParagraphStyle
) -> List:
    """Gera seção de zonas de risco."""
    story = []
    
    features = risk_zones_geojson.get("features", [])
    
    if not features:
        story.append(Paragraph("Nenhuma zona de risco identificada.", body_style))
        return story
    
    # Tabela de zonas de risco
    risk_table_data = [["Tipo de Zona", "Descrição", "Nível de Risco"]]
    
    for feature in features:
        properties = feature.get("properties", {})
        zone_type = properties.get("zone_type", "desconhecido")
        name = properties.get("name", "Zona sem nome")
        risk_level = properties.get("risk_level", "desconhecido")
        
        risk_table_data.append([
            zone_type.replace("_", " ").title(),
            name,
            risk_level.title()
        ])
    
    risk_table = Table(risk_table_data, colWidths=[2*inch, 3*inch, 1.5*inch])
    risk_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 9)
    ]))
    
    story.append(risk_table)
    story.append(Spacer(1, 12))
    
    # Estatísticas
    story.append(Paragraph("Estatísticas das Zonas de Risco", subheading_style))
    
    total_zones = len(features)
    critical_zones = len([f for f in features if f.get("properties", {}).get("risk_level") == "critical"])
    high_risk_zones = len([f for f in features if f.get("properties", {}).get("risk_level") == "high"])
    
    stats_text = f"""
    <b>Total de Zonas:</b> {total_zones}<br/>
    <b>Zonas Críticas:</b> {critical_zones}<br/>
    <b>Zonas de Alto Risco:</b> {high_risk_zones}<br/>
    <b>Área Total de Risco:</b> Estimativa baseada nos cálculos de impacto
    """
    
    story.append(Paragraph(stats_text, body_style))
    return story

def _generate_evacuation_section(
    evacuation_analysis: Dict,
    body_style: ParagraphStyle,
    subheading_style: ParagraphStyle
) -> List:
    """Gera seção de plano de evacuação."""
    story = []
    
    statistics = evacuation_analysis.get("statistics", {})
    routes = evacuation_analysis.get("routes", [])
    
    # Estatísticas gerais
    story.append(Paragraph("Estatísticas de Evacuação", subheading_style))
    
    stats_text = f"""
    <b>Total de Rotas Calculadas:</b> {statistics.get('total_routes', 0)}<br/>
    <b>Distância Média:</b> {statistics.get('average_distance_km', 0):.1f} km<br/>
    <b>Tempo Médio de Evacuação:</b> {statistics.get('average_time_hours', 0):.1f} horas<br/>
    <b>Score Médio de Segurança:</b> {statistics.get('average_safety_score', 0):.2f}/1.0<br/>
    <b>Zonas de Risco Evitadas:</b> {statistics.get('risk_zones_avoided', 0)}
    """
    
    story.append(Paragraph(stats_text, body_style))
    story.append(Spacer(1, 12))
    
    # Rotas recomendadas (top 3)
    if routes:
        story.append(Paragraph("Rotas Recomendadas", subheading_style))
        
        for i, route in enumerate(routes[:3], 1):
            evac_point = route.get("evacuation_point", {})
            route_data = route.get("route", {})
            
            route_text = f"""
            <b>Rota {i}:</b> {evac_point.get('name', 'Ponto sem nome')}<br/>
            <b>Distância:</b> {route_data.get('distance_km', 0):.1f} km<br/>
            <b>Tempo Estimado:</b> {route_data.get('estimated_time_hours', 0):.1f} horas<br/>
            <b>Segurança:</b> {route_data.get('safety_score', 0):.2f}/1.0<br/>
            <b>Capacidade do Destino:</b> {evac_point.get('capacity', 0)} pessoas
            """
            
            story.append(Paragraph(route_text, body_style))
            story.append(Spacer(1, 8))
    
    return story

def _generate_recommendations_section(
    impact_simulation: Dict,
    risk_zones_geojson: Dict,
    evacuation_analysis: Dict,
    body_style: ParagraphStyle
) -> List:
    """Gera seção de recomendações."""
    story = []
    
    energy_megatons = impact_simulation.get("energia", {}).get("equivalente_tnt_megatons", 0)
    crater_diameter = impact_simulation.get("cratera", {}).get("diametro_final_km", 0)
    
    # Recomendações baseadas na magnitude do impacto
    if energy_megatons > 100:  # Impacto muito grande
        urgency = "CRÍTICA"
        recommendations = [
            "Evacuação imediata obrigatória em raio de 50 km",
            "Ativação de protocolos de emergência nacional",
            "Coordenação com agências internacionais",
            "Preparação de infraestrutura médica de emergência",
            "Estabelecimento de centros de comando de crise"
        ]
    elif energy_megatons > 10:  # Impacto grande
        urgency = "ALTA"
        recommendations = [
            "Evacuação em raio de 20 km",
            "Ativação de protocolos regionais",
            "Mobilização de recursos de emergência",
            "Coordenação inter-agências",
            "Preparação de abrigos temporários"
        ]
    else:  # Impacto moderado
        urgency = "MODERADA"
        recommendations = [
            "Evacuação em raio de 10 km",
            "Ativação de protocolos locais",
            "Monitoramento contínuo",
            "Preparação de resposta médica",
            "Comunicação com comunidades afetadas"
        ]
    
    story.append(Paragraph(f"<b>Urgência das Medidas:</b> {urgency}", body_style))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("<b>Recomendações Prioritárias:</b>", body_style))
    
    for i, rec in enumerate(recommendations, 1):
        story.append(Paragraph(f"{i}. {rec}", body_style))
    
    story.append(Spacer(1, 12))
    
    # Recomendações específicas
    story.append(Paragraph("<b>Recomendações Específicas:</b>", body_style))
    
    specific_recommendations = [
        "Implementar sistema de alerta precoce com 24h de antecedência",
        "Estabelecer rotas de evacuação alternativas",
        "Preparar estoques de suprimentos de emergência",
        "Treinar equipes de resposta rápida",
        "Coordenar com autoridades de saúde pública",
        "Estabelecer protocolos de comunicação de crise",
        "Preparar planos de contingência para infraestrutura crítica"
    ]
    
    for i, rec in enumerate(specific_recommendations, 1):
        story.append(Paragraph(f"{i}. {rec}", body_style))
    
    return story

def _generate_technical_annexes(
    impact_simulation: Dict,
    body_style: ParagraphStyle,
    subheading_style: ParagraphStyle
) -> List:
    """Gera anexos técnicos."""
    story = []
    
    # Parâmetros de entrada
    story.append(Paragraph("Parâmetros de Simulação", subheading_style))
    
    inputs = impact_simulation.get("inputs", {})
    inputs_text = f"""
    <b>Diâmetro do Asteroide:</b> {inputs.get('diametro_m', 0):.1f} metros<br/>
    <b>Velocidade de Impacto:</b> {inputs.get('velocidade_kms', 0):.1f} km/s<br/>
    <b>Ângulo de Impacto:</b> {inputs.get('angulo_graus', 0):.1f}°<br/>
    <b>Tipo de Terreno:</b> {inputs.get('tipo_terreno', 'desconhecido').title()}<br/>
    <b>Densidade do Impactor:</b> {inputs.get('densidade_impactor_kgm3', 0)} kg/m³
    """
    
    story.append(Paragraph(inputs_text, body_style))
    story.append(Spacer(1, 12))
    
    # Metodologia
    story.append(Paragraph("Metodologia de Cálculo", subheading_style))
    
    methodology_text = """
    Os cálculos de impacto foram realizados utilizando modelos científicos estabelecidos:
    <br/>• <b>Formação de Cratera:</b> Fórmula de Holsapple-Schmidt
    <br/>• <b>Ondas de Choque:</b> Modelos de sobrepressão baseados em explosões
    <br/>• <b>Efeitos Térmicos:</b> Modelos de radiação térmica
    <br/>• <b>Sismos:</b> Relação energia-magnitude Richter
    <br/>• <b>Tsunamis:</b> Modelos de Ward & Asphaug
    <br/>• <b>Dispersão Atmosférica:</b> Modelos gaussianos de pluma
    """
    
    story.append(Paragraph(methodology_text, body_style))
    
    return story

def _assess_criticality_level(energy_megatons: float, crater_diameter: float) -> str:
    """Avalia o nível de criticidade do impacto."""
    if energy_megatons > 100 or crater_diameter > 10:
        return "CRÍTICO - Emergência Nacional"
    elif energy_megatons > 10 or crater_diameter > 5:
        return "ALTO - Emergência Regional"
    elif energy_megatons > 1 or crater_diameter > 1:
        return "MODERADO - Emergência Local"
    else:
        return "BAIXO - Monitoramento"

def _calculate_crater_area(diameter_km: float) -> float:
    """Calcula a área da cratera."""
    return 3.14159 * (diameter_km / 2) ** 2
