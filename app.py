#!/usr/bin/env python3
"""
Dashboard RRHH Grupo Raval - Streamlit Version
Tablero interactivo con datos de Recursos Humanos - v3.0 FILTROS FUNCIONANDO
"""

import streamlit as st
import pandas as pd
import json
from pathlib import Path
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from typing import Dict, List, Any, Tuple

# ============================================================================
# CONFIGURACIÓN
# ============================================================================

st.set_page_config(
    page_title="Dashboard RRHH - Grupo Raval",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Colores institucionales Grupo Raval
MARRÓN_CLARO = "#87746C"
MARRÓN_OSCURO = "#403230"
BLANCO = "#FFFFFF"
GRIS_CLARO = "#F5F5F5"

st.markdown(f"""
    <style>
        .metric-card {{
            background-color: {GRIS_CLARO};
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            margin: 10px 0;
            border-left: 5px solid {MARRÓN_CLARO};
        }}
        .metric-value {{
            font-size: 28px;
            font-weight: bold;
            color: {MARRÓN_OSCURO};
        }}
        .metric-description {{
            font-size: 11px;
            color: #999;
            margin-top: 10px;
            padding: 8px;
            background-color: {BLANCO};
            border-radius: 5px;
            border-left: 3px solid {MARRÓN_CLARO};
            text-align: left;
            line-height: 1.4;
        }}
        .formula-label {{
            font-weight: bold;
            color: {MARRÓN_CLARO};
            font-size: 10px;
        }}
        .logo-header {{
            text-align: center;
            padding: 20px 0;
            border-bottom: 3px solid {MARRÓN_CLARO};
            margin-bottom: 20px;
        }}
    </style>
""", unsafe_allow_html=True)

# ============================================================================
# CARGAR DATOS
# ============================================================================

@st.cache_data
def cargar_datos():
    """Carga los datos del JSON"""
    try:
        if Path('indicadores_rrhh.json').exists():
            with open('indicadores_rrhh.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        return None
    except Exception as e:
        st.error(f"Error cargando datos: {e}")
        return None

def normalizar_area(area_name: str) -> str:
    """
    Convierte "EMPRESA - AREA" en "AREA"
    Normaliza variaciones (ADMINISTRACION, ADMINISTRACIÓN)
    """
    # Remover prefijo empresa
    clean_name = area_name
    for empresa in ['VILADOS - ', 'PLADES - ', 'REMIPLAT - ']:
        if clean_name.startswith(empresa):
            clean_name = clean_name.replace(empresa, '')
            break

    # Normalizar variaciones comunes
    clean_name = clean_name.upper()
    clean_name = clean_name.replace('Á', 'A').replace('É', 'E').replace('Í', 'I').replace('Ó', 'O').replace('Ú', 'U')

    return clean_name.strip()

def obtener_datos_filtrados(datos: Dict, empresa: str, area: str, periodo: str) -> Tuple[Dict, Dict]:
    """
    Filtra los datos según combinación de filtros.
    Maneja 8 casos: (Todas/Específica Empresa) x (Todas/Específica Área) x (Acumulado/Período)
    """
    if not datos:
        return {}, {}

    resultado = {
        'costos_nominales': 0,
        'costos_horas_extras': 0,
        'total_horas_extras_dias': 0,
        'costos_adelantos': 0,
        'costos_prestamos': 0,
        'empresas': {},
        'areas': {},
        'personas_por_empresa': {}
    }

    personas_por_emp = datos.get('acumulados', {}).get('personas_por_empresa', {})

    # ========================================================================
    # PERÍODO ACUMULADO
    # ========================================================================
    if periodo == "Acumulado":
        acumulados = datos.get('acumulados', {})
        areas_data = acumulados.get('areas', {})

        # 1. TODAS empresas + TODAS áreas
        if empresa == "Todas" and area == "Todas":
            resultado['costos_nominales'] = acumulados.get('costos_nominales', 0)
            resultado['costos_horas_extras'] = acumulados.get('costos_horas_extras', 0)
            resultado['total_horas_extras_dias'] = acumulados.get('total_horas_extras_dias', 0)
            resultado['costos_adelantos'] = acumulados.get('costos_adelantos', 0)
            resultado['costos_prestamos'] = acumulados.get('costos_prestamos', 0)
            resultado['personas_por_empresa'] = personas_por_emp

        # 2. TODAS empresas + Área ESPECÍFICA
        elif empresa == "Todas" and area != "Todas":
            for area_key, area_info in areas_data.items():
                if normalizar_area(area_key) == normalizar_area(area):
                    resultado['costos_nominales'] += area_info.get('costos_nominales', 0)
                    resultado['costos_horas_extras'] += area_info.get('costos_horas_extras', 0)
                    resultado['total_horas_extras_dias'] += area_info.get('total_horas_extras_dias', 0)
                    resultado['costos_adelantos'] += area_info.get('costos_adelantos', 0)
                    resultado['costos_prestamos'] += area_info.get('costos_prestamos', 0)
            resultado['personas_por_empresa'] = personas_por_emp

        # 3. Empresa ESPECÍFICA + TODAS áreas
        elif empresa != "Todas" and area == "Todas":
            for area_key, area_info in areas_data.items():
                if area_info.get('empresa') == empresa:
                    resultado['costos_nominales'] += area_info.get('costos_nominales', 0)
                    resultado['costos_horas_extras'] += area_info.get('costos_horas_extras', 0)
                    resultado['total_horas_extras_dias'] += area_info.get('total_horas_extras_dias', 0)
                    resultado['costos_adelantos'] += area_info.get('costos_adelantos', 0)
                    resultado['costos_prestamos'] += area_info.get('costos_prestamos', 0)
                    resultado['areas'][normalizar_area(area_key)] = area_info
            resultado['personas_por_empresa'] = {empresa: personas_por_emp.get(empresa, 0)}

        # 4. Empresa ESPECÍFICA + Área ESPECÍFICA
        else:
            for area_key, area_info in areas_data.items():
                if (area_info.get('empresa') == empresa and normalizar_area(area_key) == normalizar_area(area)):
                    resultado['costos_nominales'] = area_info.get('costos_nominales', 0)
                    resultado['costos_horas_extras'] = area_info.get('costos_horas_extras', 0)
                    resultado['total_horas_extras_dias'] = area_info.get('total_horas_extras_dias', 0)
                    resultado['costos_adelantos'] = area_info.get('costos_adelantos', 0)
                    resultado['costos_prestamos'] = area_info.get('costos_prestamos', 0)
                    break
            resultado['personas_por_empresa'] = {empresa: personas_por_emp.get(empresa, 0)}

    # ========================================================================
    # PERÍODO ESPECÍFICO
    # ========================================================================
    else:
        por_periodo = datos.get('por_periodo', {}).get(periodo, {})

        # 5. TODAS empresas + TODAS áreas EN ESE PERÍODO
        if empresa == "Todas" and area == "Todas":
            for emp_name, emp_data in por_periodo.items():
                if isinstance(emp_data, dict):
                    for area_name, area_info in emp_data.items():
                        if isinstance(area_info, dict):
                            resultado['costos_nominales'] += area_info.get('costos_nominales', 0)
                            resultado['costos_horas_extras'] += area_info.get('costos_horas_extras', 0)
                            resultado['total_horas_extras_dias'] += area_info.get('total_horas_extras_dias', 0)
                            resultado['costos_adelantos'] += area_info.get('costos_adelantos', 0)
                            resultado['costos_prestamos'] += area_info.get('costos_prestamos', 0)
            resultado['personas_por_empresa'] = personas_por_emp

        # 6. TODAS empresas + Área ESPECÍFICA EN ESE PERÍODO
        elif empresa == "Todas" and area != "Todas":
            for emp_name, emp_data in por_periodo.items():
                if isinstance(emp_data, dict):
                    for area_name, area_info in emp_data.items():
                        if isinstance(area_info, dict) and normalizar_area(area_name) == normalizar_area(area):
                            resultado['costos_nominales'] += area_info.get('costos_nominales', 0)
                            resultado['costos_horas_extras'] += area_info.get('costos_horas_extras', 0)
                            resultado['total_horas_extras_dias'] += area_info.get('total_horas_extras_dias', 0)
                            resultado['costos_adelantos'] += area_info.get('costos_adelantos', 0)
                            resultado['costos_prestamos'] += area_info.get('costos_prestamos', 0)
            resultado['personas_por_empresa'] = personas_por_emp

        # 7. Empresa ESPECÍFICA + TODAS áreas EN ESE PERÍODO
        elif empresa != "Todas" and area == "Todas":
            if empresa in por_periodo:
                emp_data = por_periodo[empresa]
                for area_name, area_info in emp_data.items():
                    if isinstance(area_info, dict):
                        resultado['costos_nominales'] += area_info.get('costos_nominales', 0)
                        resultado['costos_horas_extras'] += area_info.get('costos_horas_extras', 0)
                        resultado['total_horas_extras_dias'] += area_info.get('total_horas_extras_dias', 0)
                        resultado['costos_adelantos'] += area_info.get('costos_adelantos', 0)
                        resultado['costos_prestamos'] += area_info.get('costos_prestamos', 0)
            resultado['personas_por_empresa'] = {empresa: personas_por_emp.get(empresa, 0)}

        # 8. Empresa ESPECÍFICA + Área ESPECÍFICA EN ESE PERÍODO
        else:
            if empresa in por_periodo:
                emp_data = por_periodo[empresa]
                for area_name, area_info in emp_data.items():
                    if isinstance(area_info, dict) and normalizar_area(area_name) == normalizar_area(area):
                        resultado['costos_nominales'] = area_info.get('costos_nominales', 0)
                        resultado['costos_horas_extras'] = area_info.get('costos_horas_extras', 0)
                        resultado['total_horas_extras_dias'] = area_info.get('total_horas_extras_dias', 0)
                        resultado['costos_adelantos'] = area_info.get('costos_adelantos', 0)
                        resultado['costos_prestamos'] = area_info.get('costos_prestamos', 0)
                        break
            resultado['personas_por_empresa'] = {empresa: personas_por_emp.get(empresa, 0)}

    return resultado, resultado.get('personas_por_empresa', {})

def obtener_empresas(datos):
    """Obtiene lista de empresas"""
    if datos and 'acumulados' in datos:
        return sorted(list(datos['acumulados'].get('empresas', {}).keys()))
    return []

def obtener_areas_unicas(datos, empresa):
    """
    Obtiene ÁREAS ÚNICAS consolidadas (sin discriminar por empresa en el nombre).
    Si empresa es "Todas": retorna todas las áreas únicas.
    Si empresa es específica: retorna áreas de esa empresa.
    """
    if not datos or 'acumulados' not in datos:
        return []

    areas_dict = datos['acumulados'].get('areas', {})
    areas_unicas = set()

    if empresa == "Todas":
        # Todas las áreas únicas (sin prefijo empresa)
        for area_name in areas_dict.keys():
            clean_area = normalizar_area(area_name)
            areas_unicas.add(clean_area)
    else:
        # Solo áreas de la empresa especificada
        for area_name, area_info in areas_dict.items():
            if area_info.get('empresa') == empresa:
                clean_area = normalizar_area(area_name)
                areas_unicas.add(clean_area)

    return sorted(list(areas_unicas))

def obtener_periodos(datos):
    """Obtiene lista de períodos"""
    if datos and 'por_periodo' in datos:
        periodos = list(datos['por_periodo'].keys())
        return sorted(periodos, reverse=True)
    return []

def formatear_moneda(valor):
    if valor is None or valor == 0:
        return "$0"
    return f"${valor:,.0f}"

def formatear_numero(valor):
    if valor is None:
        return "0"
    return f"{valor:,.0f}"

# ============================================================================
# INTERFAZ PRINCIPAL
# ============================================================================

st.markdown(f"""
    <div class="logo-header">
        <h1 style="color: {MARRÓN_OSCURO}; margin: 0;">GRUPO RAVAL</h1>
        <h2 style="color: {MARRÓN_CLARO}; margin: 5px 0 0 0;">📊 Dashboard RRHH</h2>
    </div>
""", unsafe_allow_html=True)

st.markdown("Indicadores de Recursos Humanos - Información en tiempo real")

datos = cargar_datos()

if datos:
    fecha_proc = datos.get('fecha_procesamiento', 'N/A')
    st.markdown(f"**Última actualización:** {fecha_proc}")

    # ========================================================================
    # SIDEBAR - FILTROS
    # ========================================================================

    with st.sidebar:
        st.markdown(f"<h2 style='color: {MARRÓN_CLARO};'>🔍 FILTROS</h2>", unsafe_allow_html=True)

        # Empresa
        empresas = obtener_empresas(datos)
        empresa_sel = st.selectbox("Empresa", ["Todas"] + empresas, key="empresa")

        # Área - Consolidada
        areas = obtener_areas_unicas(datos, empresa_sel)
        area_sel = st.selectbox("Área", ["Todas"] + areas, key="area")

        # Período
        periodos = obtener_periodos(datos)
        periodo_sel = st.selectbox("Período", ["Acumulado"] + periodos, key="periodo")

        st.markdown("---")
        st.success("✅ TODOS los filtros IMPACTAN en TODOS los números y gráficas")

    # ========================================================================
    # OBTENER DATOS FILTRADOS
    # ========================================================================

    datos_filtrados, personas_por_empresa = obtener_datos_filtrados(datos, empresa_sel, area_sel, periodo_sel)

    # Contar personas según filtro
    if empresa_sel == "Todas":
        personas_por_emp = datos.get('acumulados', {}).get('personas_por_empresa', {})
        num_personas = sum(personas_por_emp.values())
    else:
        personas_por_emp = datos.get('acumulados', {}).get('personas_por_empresa', {})
        num_personas = personas_por_emp.get(empresa_sel, 0)

    # ========================================================================
    # TABS
    # ========================================================================

    tab1, tab2, tab3, tab4 = st.tabs([
        "💰 Costos Nominales",
        "⏰ Horas Extras",
        "🏖️ Licencias",
        "📋 Adelantos/Préstamos"
    ])

    # ========================================================================
    # TAB 1: COSTOS NOMINALES
    # ========================================================================

    with tab1:
        st.markdown(f"<h2 style='color: {MARRÓN_OSCURO};'>💰 Costos Nominales</h2>", unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)

        with col1:
            costo_total = datos_filtrados.get('costos_nominales', 0)
            st.metric("💵 Costo Total", formatear_moneda(costo_total))
            st.markdown("""
            <div class="metric-description">
                <span class="formula-label">📐 Fórmula:</span> Suma de salarios y beneficios<br>
                <span class="formula-label">📊 Componentes:</span> Sueldo, antigüedad, comisiones
            </div>
            """, unsafe_allow_html=True)

        with col2:
            if empresa_sel == "Todas":
                num_empresas = len(empresas)
            else:
                num_empresas = 1
            st.metric("🏢 Empresas", f"{num_empresas}")
            st.markdown("""
            <div class="metric-description">
                <span class="formula-label">📐 Fórmula:</span> Cantidad de empresas<br>
                <span class="formula-label">📊 Componentes:</span> Vilados, Plades, Remiplat
            </div>
            """, unsafe_allow_html=True)

        with col3:
            st.metric("👥 Personas", f"{num_personas}")
            st.markdown("""
            <div class="metric-description">
                <span class="formula-label">📐 Fórmula:</span> Total empleados<br>
                <span class="formula-label">📊 Componentes:</span> Base ADP activos
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")

        # GRÁFICAS DINÁMICAS
        col_g1, col_g2 = st.columns(2)

        with col_g1:
            if empresa_sel == "Todas":
                # Gráfico de 3 empresas
                empresas_data = {}
                for emp in empresas:
                    costo_emp = 0
                    if periodo_sel == "Acumulado":
                        costo_emp = datos.get('acumulados', {}).get('empresas', {}).get(emp, {}).get('costos_nominales', 0)
                    else:
                        periodo_data = datos.get('por_periodo', {}).get(periodo_sel, {}).get(emp, {})
                        for area_data in periodo_data.values():
                            if isinstance(area_data, dict):
                                costo_emp += area_data.get('costos_nominales', 0)
                    empresas_data[emp] = costo_emp

                if empresas_data:
                    df = pd.DataFrame([
                        {'Empresa': emp, 'Costo': costo}
                        for emp, costo in empresas_data.items()
                    ])
                    fig = px.bar(df, x='Empresa', y='Costo', title='Costos por Empresa',
                                color_discrete_sequence=[MARRÓN_CLARO])
                    fig.update_layout(showlegend=False)
                    st.plotly_chart(fig, use_container_width=True)
            else:
                # Gráfico de áreas de la empresa seleccionada
                areas_data = datos_filtrados.get('areas', {})
                if areas_data:
                    df = pd.DataFrame([
                        {'Área': area, 'Costo': area_data.get('costos_nominales', 0)}
                        for area, area_data in areas_data.items()
                    ]).sort_values('Costo', ascending=True)
                    fig = px.barh(df, x='Costo', y='Área', title=f'Costos - {empresa_sel}',
                                 color_discrete_sequence=[MARRÓN_CLARO])
                    fig.update_layout(showlegend=False)
                    st.plotly_chart(fig, use_container_width=True)

        with col_g2:
            st.markdown(f"<h4 style='color: {MARRÓN_CLARO};'>📊 Filtros Activos</h4>", unsafe_allow_html=True)
            st.markdown(f"""
            - 🏢 Empresa: **{empresa_sel}**
            - 📂 Área: **{area_sel}**
            - 📅 Período: **{periodo_sel}**

            ---

            **Resumen:**
            - Costo Total: {formatear_moneda(datos_filtrados.get('costos_nominales', 0))}
            - Personas: {num_personas}
            - Costo/Persona: {formatear_moneda(datos_filtrados.get('costos_nominales', 0) / num_personas if num_personas > 0 else 0)}
            """)

    # ========================================================================
    # TAB 2: HORAS EXTRAS
    # ========================================================================

    with tab2:
        st.markdown(f"<h2 style='color: {MARRÓN_OSCURO};'>⏰ Horas Extras</h2>", unsafe_allow_html=True)

        col1, col2, col3, col4 = st.columns(4)

        costo_he = datos_filtrados.get('costos_horas_extras', 0)
        dias_he = datos_filtrados.get('total_horas_extras_dias', 0)
        costo_nominal = datos_filtrados.get('costos_nominales', 0)
        pct_he = (costo_he / costo_nominal * 100) if costo_nominal > 0 else 0

        with col1:
            st.metric("💵 Costo Total HE", formatear_moneda(costo_he))
            st.markdown("""
            <div class="metric-description">
                <span class="formula-label">📐 Fórmula:</span> Suma costos HE<br>
                <span class="formula-label">📊 Componentes:</span> 50%, 100%, Feriados
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.metric("📅 Total Días HE", f"{dias_he:,.0f}")
            st.markdown("""
            <div class="metric-description">
                <span class="formula-label">📐 Fórmula:</span> Cantidad días<br>
                <span class="formula-label">📊 Componentes:</span> Horario extendido
            </div>
            """, unsafe_allow_html=True)

        with col3:
            promedio = (costo_he / dias_he) if dias_he > 0 else 0
            st.metric("💸 Promedio/Día", formatear_moneda(promedio))
            st.markdown("""
            <div class="metric-description">
                <span class="formula-label">📐 Fórmula:</span> Costo HE ÷ Días<br>
                <span class="formula-label">📊 Componentes:</span> Distribución uniforme
            </div>
            """, unsafe_allow_html=True)

        with col4:
            st.metric("📊 % de Nómina", f"{pct_he:.1f}%")
            st.markdown("""
            <div class="metric-description">
                <span class="formula-label">📐 Fórmula:</span> (HE ÷ Nominal) × 100<br>
                <span class="formula-label">📊 Componentes:</span> Impacto en nómina
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")

        col_g1, col_g2 = st.columns(2)

        with col_g1:
            if costo_he > 0:
                fig = go.Figure(data=[go.Bar(x=['Costo HE'], y=[costo_he], marker_color=MARRÓN_CLARO)])
                fig.update_layout(title='Costo Horas Extras', showlegend=False)
                st.plotly_chart(fig, use_container_width=True)

        with col_g2:
            if dias_he > 0:
                fig = go.Figure(data=[go.Bar(x=['Días HE'], y=[dias_he], marker_color=MARRÓN_CLARO)])
                fig.update_layout(title='Días con Horas Extras', showlegend=False)
                st.plotly_chart(fig, use_container_width=True)

    # ========================================================================
    # TAB 3: LICENCIAS
    # ========================================================================

    with tab3:
        st.markdown(f"<h2 style='color: {MARRÓN_OSCURO};'>🏖️ Licencias</h2>", unsafe_allow_html=True)
        st.info("📋 Módulo en desarrollo - Próximamente disponible")
        st.markdown("""
        Se mostrará:
        - Días utilizados
        - Días disponibles
        - Proyección anual
        - Por empleado
        """)

    # ========================================================================
    # TAB 4: ADELANTOS Y PRÉSTAMOS
    # ========================================================================

    with tab4:
        st.markdown(f"<h2 style='color: {MARRÓN_OSCURO};'>📋 Adelantos/Préstamos</h2>", unsafe_allow_html=True)

        col1, col2, col3, col4 = st.columns(4)

        adelantos = datos_filtrados.get('costos_adelantos', 0)
        prestamos = datos_filtrados.get('costos_prestamos', 0)
        total_pasivos = adelantos + prestamos
        costo_nominal = datos_filtrados.get('costos_nominales', 0)
        pct_pasivos = (total_pasivos / costo_nominal * 100) if costo_nominal > 0 else 0

        with col1:
            st.metric("💰 Adelantos", formatear_moneda(adelantos))
            st.markdown("""
            <div class="metric-description">
                <span class="formula-label">📐 Fórmula:</span> Suma adelantos<br>
                <span class="formula-label">📊 Componentes:</span> Simples + Cuotas
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.metric("🏦 Préstamos", formatear_moneda(prestamos))
            st.markdown("""
            <div class="metric-description">
                <span class="formula-label">📐 Fórmula:</span> Suma préstamos<br>
                <span class="formula-label">📊 Componentes:</span> Personales + Emergencias
            </div>
            """, unsafe_allow_html=True)

        with col3:
            st.metric("💼 Total Pasivos", formatear_moneda(total_pasivos))
            st.markdown("""
            <div class="metric-description">
                <span class="formula-label">📐 Fórmula:</span> Adelantos + Préstamos<br>
                <span class="formula-label">📊 Componentes:</span> Suma total
            </div>
            """, unsafe_allow_html=True)

        with col4:
            st.metric("📊 % de Nómina", f"{pct_pasivos:.1f}%")
            st.markdown("""
            <div class="metric-description">
                <span class="formula-label">📐 Fórmula:</span> (Pasivos ÷ Nominal) × 100<br>
                <span class="formula-label">📊 Componentes:</span> Impacto en nómina
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")

        col_g1, col_g2 = st.columns(2)

        with col_g1:
            if total_pasivos > 0:
                fig = go.Figure(data=[
                    go.Bar(x=['Adelantos'], y=[adelantos], marker_color=MARRÓN_CLARO, name='Adelantos'),
                    go.Bar(x=['Adelantos'], y=[prestamos], marker_color=MARRÓN_OSCURO, name='Préstamos')
                ])
                fig.update_layout(title='Adelantos vs Préstamos', barmode='stack', showlegend=True)
                st.plotly_chart(fig, use_container_width=True)

        with col_g2:
            if total_pasivos > 0:
                labels = ['Adelantos', 'Préstamos']
                valores = [adelantos, prestamos]
                fig = px.pie(values=valores, names=labels, title='Proporción Pasivos',
                            color_discrete_sequence=[MARRÓN_CLARO, MARRÓN_OSCURO])
                st.plotly_chart(fig, use_container_width=True)

    # ========================================================================
    # FOOTER
    # ========================================================================

    st.markdown("---")
    col_f1, col_f2, col_f3 = st.columns(3)

    with col_f1:
        st.markdown(f"""
        <div style='text-align: center; font-size: 11px; color: #999;'>
        <strong>📊 Actualización</strong><br>
        {fecha_proc}
        </div>
        """, unsafe_allow_html=True)

    with col_f2:
        st.markdown(f"""
        <div style='text-align: center; font-size: 11px; color: #999;'>
        <strong>📍 Filtros</strong><br>
        {empresa_sel} | {area_sel} | {periodo_sel}
        </div>
        """, unsafe_allow_html=True)

    with col_f3:
        st.markdown("""
        <div style='text-align: center; font-size: 11px; color: #999;'>
        <strong>🔄 Frecuencia</strong><br>
        Diaria 9:30 AM (UY)
        </div>
        """, unsafe_allow_html=True)

else:
    st.error("❌ No se pudieron cargar los datos")
