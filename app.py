#!/usr/bin/env python3
"""
Dashboard RRHH Grupo Raval - Streamlit Version
Tablero interactivo con datos de Recursos Humanos
"""

import streamlit as st
import pandas as pd
import json
from pathlib import Path
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from typing import Dict, List, Any

# ============================================================================
# CONFIGURACIÓN
# ============================================================================

st.set_page_config(
    page_title="Dashboard RRHH - Grupo Raval",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado con colores institucionales Grupo Raval
MARRÓN_CLARO = "#87746C"  # Color primario Grupo Raval
MARRÓN_OSCURO = "#403230"  # Color secundario Grupo Raval
BLANCO = "#FFFFFF"
GRIS_CLARO = "#F5F5F5"

st.markdown(f"""
    <style>
        :root {{
            --color-primary: {MARRÓN_CLARO};
            --color-secondary: {MARRÓN_OSCURO};
        }}

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
        .metric-label {{
            font-size: 12px;
            color: #666;
            margin-top: 5px;
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
        .tab-title {{
            color: {MARRÓN_OSCURO};
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

        return {
            'fecha_procesamiento': datetime.now().isoformat(),
            'acumulados': {
                'costos_nominales': 0,
                'costos_horas_extras': 0,
                'total_horas_extras_dias': 0,
                'costos_adelantos': 0,
                'costos_prestamos': 0,
                'empresas': {},
                'areas': {},
                'personas': {}
            },
            'por_periodo': {}
        }
    except Exception as e:
        st.error(f"Error cargando datos: {e}")
        return None

def agregar_datos(data1, data2):
    """Suma dos diccionarios de datos"""
    resultado = data1.copy()
    for key in ['costos_nominales', 'costos_horas_extras', 'total_horas_extras_dias',
                'costos_adelantos', 'costos_prestamos']:
        resultado[key] = resultado.get(key, 0) + data2.get(key, 0)
    return resultado

def obtener_datos_filtrados(datos: Dict, empresa: str, area: str, periodo: str) -> Dict:
    """
    Filtra los datos según empresa, área y período seleccionados.
    Maneja ambas estructuras: acumulados y por_periodo
    """
    if not datos:
        return {}

    resultado = {
        'costos_nominales': 0,
        'costos_horas_extras': 0,
        'total_horas_extras_dias': 0,
        'costos_adelantos': 0,
        'costos_prestamos': 0,
        'empresas': {},
        'areas': {},
        'personas': {}
    }

    # Determinar si usar acumulados o período específico
    if periodo == "Acumulado":
        base_data = datos.get('acumulados', {})
        is_accumulated = True
    else:
        base_data = datos.get('por_periodo', {}).get(periodo, {})
        is_accumulated = False

    if not base_data:
        return resultado

    # Si es estructura acumulada (tiene costos_nominales directamente)
    if is_accumulated and 'costos_nominales' in base_data:
        if empresa == "Todas":
            # Todas las empresas y áreas
            resultado = base_data.copy()
        else:
            # Filtrar por empresa
            if empresa in base_data.get('empresas', {}):
                emp_data = base_data['empresas'][empresa]
                resultado['costos_nominales'] = emp_data.get('costos_nominales', 0)
                resultado['costos_horas_extras'] = emp_data.get('costos_horas_extras', 0)
                resultado['total_horas_extras_dias'] = emp_data.get('total_horas_extras_dias', 0)
                resultado['costos_adelantos'] = emp_data.get('costos_adelantos', 0)
                resultado['costos_prestamos'] = emp_data.get('costos_prestamos', 0)

                if area != "Todas":
                    # Filtrar por área específica
                    areas_data = base_data.get('areas', {})
                    if area in areas_data:
                        area_data = areas_data[area]
                        resultado['costos_nominales'] = area_data.get('costos_nominales', 0)
                        resultado['costos_horas_extras'] = area_data.get('costos_horas_extras', 0)
                        resultado['total_horas_extras_dias'] = area_data.get('total_horas_extras_dias', 0)
                        resultado['costos_adelantos'] = area_data.get('costos_adelantos', 0)
                        resultado['costos_prestamos'] = area_data.get('costos_prestamos', 0)
                else:
                    # Agregar todas las áreas de la empresa
                    areas_data = base_data.get('areas', {})
                    for area_name, area_info in areas_data.items():
                        if area_info.get('empresa') == empresa:
                            resultado['areas'][area_name] = area_info

    else:
        # Estructura por_periodo: empresa -> área -> datos
        # base_data tiene estructura: {EMPRESA: {AREA: {...}}}

        if empresa == "Todas":
            # Agregar datos de todas las empresas
            for emp_name, emp_data in base_data.items():
                if isinstance(emp_data, dict):
                    for area_name, area_data in emp_data.items():
                        if isinstance(area_data, dict):
                            resultado = agregar_datos(resultado, area_data)
                            resultado['areas'][area_name] = area_data
        else:
            # Filtrar por empresa
            if empresa in base_data:
                emp_data = base_data[empresa]
                if area == "Todas":
                    # Todas las áreas de la empresa
                    for area_name, area_info in emp_data.items():
                        if isinstance(area_info, dict):
                            resultado = agregar_datos(resultado, area_info)
                            resultado['areas'][area_name] = area_info
                else:
                    # Área específica de empresa específica
                    if area in emp_data:
                        area_data = emp_data[area]
                        resultado = agregar_datos(resultado, area_data)

    return resultado

# ============================================================================
# FUNCIONES AUXILIARES
# ============================================================================

def formatear_moneda(valor):
    """Formatea un valor como moneda uruguaya"""
    if valor is None or valor == 0:
        return "$0"
    return f"${valor:,.0f}"

def formatear_numero(valor):
    """Formatea un número"""
    if valor is None:
        return "0"
    return f"{valor:,.0f}"

def obtener_empresas(datos):
    """Obtiene lista de empresas"""
    if datos and 'acumulados' in datos and 'empresas' in datos['acumulados']:
        return sorted(list(datos['acumulados']['empresas'].keys()))
    return []

def obtener_areas(datos, empresa):
    """
    Obtiene áreas SIN discriminar por empresa.
    Si empresa es "Todas", retorna todas las áreas.
    Si empresa es específica, retorna áreas de esa empresa.
    """
    if not datos or 'acumulados' not in datos or 'areas' not in datos['acumulados']:
        return []

    areas = datos['acumulados']['areas']

    if empresa == "Todas":
        # Retornar todas las áreas únicas
        return sorted(list(areas.keys()))
    else:
        # Retornar áreas de la empresa específica
        areas_filtradas = [a for a in areas.keys() if areas[a].get('empresa') == empresa]
        return sorted(areas_filtradas)

def obtener_periodos(datos):
    """Obtiene lista de períodos"""
    if datos and 'por_periodo' in datos:
        periodos = list(datos['por_periodo'].keys())
        return sorted(periodos, reverse=True)
    return []

# ============================================================================
# INTERFAZ PRINCIPAL
# ============================================================================

# Header con logo
st.markdown(f"""
    <div class="logo-header">
        <h1 style="color: {MARRÓN_OSCURO}; margin: 0;">GRUPO RAVAL</h1>
        <h2 style="color: {MARRÓN_CLARO}; margin: 5px 0 0 0;">📊 Dashboard RRHH</h2>
    </div>
""", unsafe_allow_html=True)

st.markdown("Indicadores de Recursos Humanos - Información en tiempo real")

# Cargar datos
datos = cargar_datos()

if datos:
    # Mostrar fecha de actualización
    fecha_proc = datos.get('fecha_procesamiento', 'N/A')
    st.markdown(f"**Última actualización:** {fecha_proc}")

    # ========================================================================
    # SIDEBAR - FILTROS
    # ========================================================================

    with st.sidebar:
        st.markdown(f"<h2 style='color: {MARRÓN_CLARO};'>🔍 Filtros</h2>", unsafe_allow_html=True)

        # Empresa
        empresas = obtener_empresas(datos)
        empresa_sel = st.selectbox(
            "Empresa",
            ["Todas"] + empresas,
            key="empresa_filter"
        )

        # Área - Sin discriminar por empresa (pero PUEDE filtrar por empresa si quiere)
        areas = obtener_areas(datos, empresa_sel)
        area_sel = st.selectbox(
            "Área",
            ["Todas"] + areas,
            key="area_filter"
        )

        # Período
        periodos = obtener_periodos(datos)
        periodo_sel = st.selectbox(
            "Período",
            ["Acumulado"] + periodos,
            key="periodo_filter"
        )

        st.markdown("---")
        st.info("💡 **Filtros en cascada:**\n- Empresa A + Área X = Solo datos de X en empresa A\n- Todas empresas + Área X = Datos de X en las 3 empresas")

    # Obtener datos filtrados
    datos_filtrados = obtener_datos_filtrados(datos, empresa_sel, area_sel, periodo_sel)

    # Usar datos filtrados si existen, sino usar acumulados
    acumulados = datos_filtrados if datos_filtrados else datos.get('acumulados', {})

    # ========================================================================
    # TABS PRINCIPALES
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
            costo_total = acumulados.get('costos_nominales', 0)
            st.metric(
                "💵 Costo Total",
                formatear_moneda(costo_total)
            )
            st.markdown("""
            <div class="metric-description">
                <span class="formula-label">📐 Fórmula:</span> Suma de todos los costos de salario y beneficios nominales<br>
                <span class="formula-label">📊 Componentes:</span> Sueldo base, antigüedad, comisiones, asignaciones familiares
            </div>
            """, unsafe_allow_html=True)

        with col2:
            if empresa_sel == "Todas":
                num_empresas = len(obtener_empresas(datos))
            else:
                num_empresas = 1
            st.metric("🏢 Empresas", f"{num_empresas}")
            st.markdown("""
            <div class="metric-description">
                <span class="formula-label">📐 Fórmula:</span> Cantidad de empresas en la selección<br>
                <span class="formula-label">📊 Componentes:</span> Vilados, Plades, Remiplat
            </div>
            """, unsafe_allow_html=True)

        with col3:
            num_personas = len(datos.get('acumulados', {}).get('personas', {}))
            st.metric("👥 Personas", f"{num_personas}")
            st.markdown("""
            <div class="metric-description">
                <span class="formula-label">📐 Fórmula:</span> Cantidad de empleados activos<br>
                <span class="formula-label">📊 Componentes:</span> Base de datos ADP - estado activo
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")

        # Gráfico de empresas - DINÁMICO según filtros
        col_chart1, col_chart2 = st.columns(2)

        with col_chart1:
            if empresa_sel == "Todas":
                # Mostrar todas las empresas
                empresas_data = datos.get('acumulados', {}).get('empresas', {})
                if empresas_data:
                    df_empresas = pd.DataFrame([
                        {'Empresa': emp, 'Costo': datos_emp.get('costos_nominales', 0)}
                        for emp, datos_emp in empresas_data.items()
                    ])

                    fig = px.bar(
                        df_empresas,
                        x='Empresa',
                        y='Costo',
                        title='Costos Nominales por Empresa',
                        color='Empresa',
                        text='Costo',
                        color_discrete_sequence=[MARRÓN_CLARO, MARRÓN_OSCURO, '#A38A7D']
                    )
                    fig.update_traces(texttemplate='$%{text:,.0f}', textposition='outside')
                    fig.update_layout(
                        showlegend=False,
                        yaxis_title="Costo ($)",
                        xaxis_title="Empresa",
                        hovermode='x unified'
                    )
                    st.plotly_chart(fig, use_container_width=True)
            else:
                # Mostrar áreas de la empresa seleccionada
                areas_data = acumulados.get('areas', {})
                if areas_data:
                    df_areas = pd.DataFrame([
                        {'Área': area, 'Costo': area_data.get('costos_nominales', 0)}
                        for area, area_data in areas_data.items()
                    ])
                    df_areas = df_areas.sort_values('Costo', ascending=True)

                    fig = px.barh(
                        df_areas,
                        x='Costo',
                        y='Área',
                        title=f'Costos Nominales - {empresa_sel}',
                        color='Costo',
                        color_continuous_scale=[MARRÓN_CLARO, MARRÓN_OSCURO],
                        text='Costo'
                    )
                    fig.update_traces(texttemplate='$%{text:,.0f}', textposition='outside')
                    fig.update_layout(
                        yaxis_title="Área",
                        xaxis_title="Costo ($)",
                        hovermode='y unified',
                        showlegend=False
                    )
                    st.plotly_chart(fig, use_container_width=True)

        with col_chart2:
            # Desglose de beneficios (ejemplo)
            st.markdown(f"<h4 style='color: {MARRÓN_CLARO};'>📊 Resumen Actual</h4>", unsafe_allow_html=True)

            filtros_text = f"""
            **Filtros aplicados:**
            - 🏢 Empresa: {empresa_sel}
            - 📂 Área: {area_sel}
            - 📅 Período: {periodo_sel}

            **Métrica:**
            - Costo Total: {formatear_moneda(acumulados.get('costos_nominales', 0))}
            - Empleados: {num_personas}
            - Costo/Empleado: {formatear_moneda(acumulados.get('costos_nominales', 0) / num_personas if num_personas > 0 else 0)}
            """
            st.markdown(filtros_text)

    # ========================================================================
    # TAB 2: HORAS EXTRAS
    # ========================================================================

    with tab2:
        st.markdown(f"<h2 style='color: {MARRÓN_OSCURO};'>⏰ Horas Extras</h2>", unsafe_allow_html=True)

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            costo_he = acumulados.get('costos_horas_extras', 0)
            st.metric(
                "💵 Costo Total",
                formatear_moneda(costo_he)
            )
            st.markdown("""
            <div class="metric-description">
                <span class="formula-label">📐 Fórmula:</span> Suma de todos los costos de horas extras<br>
                <span class="formula-label">📊 Componentes:</span> Horas 50%, Horas 100%, Feriados
            </div>
            """, unsafe_allow_html=True)

        with col2:
            dias_he = acumulados.get('total_horas_extras_dias', 0)
            st.metric(
                "📅 Total Días",
                formatear_numero(dias_he)
            )
            st.markdown("""
            <div class="metric-description">
                <span class="formula-label">📐 Fórmula:</span> Cantidad total de días con horas extras<br>
                <span class="formula-label">📊 Componentes:</span> Días trabajados en horario extendido
            </div>
            """, unsafe_allow_html=True)

        with col3:
            costo_promedio = costo_he / dias_he if dias_he > 0 else 0
            st.metric("💸 Promedio/Día", formatear_moneda(costo_promedio))
            st.markdown("""
            <div class="metric-description">
                <span class="formula-label">📐 Fórmula:</span> Costo Total ÷ Total Días<br>
                <span class="formula-label">📊 Componentes:</span> Distribución uniforme
            </div>
            """, unsafe_allow_html=True)

        with col4:
            costo_nominal = acumulados.get('costos_nominales', 0)
            pct_costo = (costo_he / costo_nominal * 100) if costo_nominal > 0 else 0
            st.metric("📊 % de Nómina", f"{pct_costo:.1f}%")
            st.markdown("""
            <div class="metric-description">
                <span class="formula-label">📐 Fórmula:</span> (Costo HE ÷ Costo Nominal) × 100<br>
                <span class="formula-label">📊 Componentes:</span> Impacto en nómina total
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")
        st.info("📌 **Vista Dual:** Costo ($) + Días trabajados en horas extras")

        # Gráficos dinámicos
        col_he1, col_he2 = st.columns(2)

        with col_he1:
            if empresa_sel == "Todas":
                # Empresas
                empresas_data = datos.get('acumulados', {}).get('empresas', {})
                if empresas_data:
                    df_he_emp = pd.DataFrame([
                        {'Empresa': emp, 'Costo HE': datos_emp.get('costos_horas_extras', 0)}
                        for emp, datos_emp in empresas_data.items()
                    ])
                    fig = px.bar(df_he_emp, x='Empresa', y='Costo HE', title='Costo HE por Empresa',
                                color_discrete_sequence=[MARRÓN_CLARO])
                    fig.update_layout(showlegend=False)
                    st.plotly_chart(fig, use_container_width=True)
            else:
                # Áreas de empresa
                areas_data = acumulados.get('areas', {})
                if areas_data:
                    df_he_area = pd.DataFrame([
                        {'Área': area, 'Costo HE': area_data.get('costos_horas_extras', 0)}
                        for area, area_data in areas_data.items()
                    ]).sort_values('Costo HE', ascending=True)
                    fig = px.barh(df_he_area, x='Costo HE', y='Área', title='Costo HE por Área',
                                 color_discrete_sequence=[MARRÓN_CLARO])
                    fig.update_layout(showlegend=False)
                    st.plotly_chart(fig, use_container_width=True)

        with col_he2:
            if empresa_sel == "Todas":
                # Días por empresa
                empresas_data = datos.get('acumulados', {}).get('empresas', {})
                if empresas_data:
                    df_dias_emp = pd.DataFrame([
                        {'Empresa': emp, 'Días HE': datos_emp.get('total_horas_extras_dias', 0)}
                        for emp, datos_emp in empresas_data.items()
                    ])
                    fig = px.bar(df_dias_emp, x='Empresa', y='Días HE', title='Días HE por Empresa',
                                color_discrete_sequence=[MARRÓN_OSCURO])
                    fig.update_layout(showlegend=False)
                    st.plotly_chart(fig, use_container_width=True)
            else:
                # Días por área
                areas_data = acumulados.get('areas', {})
                if areas_data:
                    df_dias_area = pd.DataFrame([
                        {'Área': area, 'Días HE': area_data.get('total_horas_extras_dias', 0)}
                        for area, area_data in areas_data.items()
                    ]).sort_values('Días HE', ascending=True)
                    fig = px.barh(df_dias_area, x='Días HE', y='Área', title='Días HE por Área',
                                 color_discrete_sequence=[MARRÓN_OSCURO])
                    fig.update_layout(showlegend=False)
                    st.plotly_chart(fig, use_container_width=True)

    # ========================================================================
    # TAB 3: LICENCIAS
    # ========================================================================

    with tab3:
        st.markdown(f"<h2 style='color: {MARRÓN_OSCURO};'>🏖️ Licencias</h2>", unsafe_allow_html=True)

        st.warning("🚧 **Módulo en Desarrollo**")
        st.markdown(f"""
        ### Contenido próximamente disponible:

        **Indicadores a mostrar:**
        - 📅 Licencias utilizadas (total de días)
        - 🎯 Días disponibles por empleado
        - 👤 Desglose por empleado
        - 📊 Proyección anual

        **Componentes:**
        - Licencias anuales
        - Licencias patológicas
        - Licencias sin goce
        - Permisos especiales

        **Status:** Pendiente integración de datos desde la fuente RRHH.
        """)

    # ========================================================================
    # TAB 4: ADELANTOS Y PRÉSTAMOS
    # ========================================================================

    with tab4:
        st.markdown(f"<h2 style='color: {MARRÓN_OSCURO};'>📋 Adelantos y Préstamos</h2>", unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)

        with col1:
            total_adelantos = acumulados.get('costos_adelantos', 0)
            st.metric(
                "💰 Adelantos",
                formatear_moneda(total_adelantos)
            )
            st.markdown("""
            <div class="metric-description">
                <span class="formula-label">📐 Fórmula:</span> Suma de adelantos de salario descontados<br>
                <span class="formula-label">📊 Componentes:</span> Adelantos simples y adelantos en cuotas
            </div>
            """, unsafe_allow_html=True)

        with col2:
            total_prestamos = acumulados.get('costos_prestamos', 0)
            st.metric(
                "🏦 Préstamos",
                formatear_moneda(total_prestamos)
            )
            st.markdown("""
            <div class="metric-description">
                <span class="formula-label">📐 Fórmula:</span> Suma de préstamos descontados en nómina<br>
                <span class="formula-label">📊 Componentes:</span> Préstamos personales y emergencias
            </div>
            """, unsafe_allow_html=True)

        with col3:
            total_pasivos = total_adelantos + total_prestamos
            costo_nominal = acumulados.get('costos_nominales', 0)
            pct_pasivos = (total_pasivos / costo_nominal * 100) if costo_nominal > 0 else 0
            st.metric("📊 % de Nómina", f"{pct_pasivos:.1f}%")
            st.markdown("""
            <div class="metric-description">
                <span class="formula-label">📐 Fórmula:</span> (Total Pasivos ÷ Costo Nominal) × 100<br>
                <span class="formula-label">📊 Componentes:</span> Impacto en nómina
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")

        col1, col2 = st.columns(2)

        with col1:
            if total_adelantos > 0 or total_prestamos > 0:
                fig = go.Figure(data=[
                    go.Pie(
                        labels=['Adelantos', 'Préstamos'],
                        values=[total_adelantos, total_prestamos],
                        hole=0.3,
                        marker=dict(colors=[MARRÓN_CLARO, MARRÓN_OSCURO])
                    )
                ])
                fig.update_layout(
                    title='Proporción: Adelantos vs Préstamos',
                    showlegend=True,
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Sin datos de adelantos o préstamos para mostrar.")

        with col2:
            # Gráfico de empresas/áreas
            if empresa_sel == "Todas":
                empresas_data = datos.get('acumulados', {}).get('empresas', {})
                if empresas_data:
                    df_pasivos = pd.DataFrame([
                        {'Empresa': emp, 'Pasivos': datos_emp.get('costos_adelantos', 0) + datos_emp.get('costos_prestamos', 0)}
                        for emp, datos_emp in empresas_data.items()
                    ])
                    fig = px.bar(df_pasivos, x='Empresa', y='Pasivos', title='Total Pasivos por Empresa',
                               color_discrete_sequence=[MARRÓN_CLARO])
                    st.plotly_chart(fig, use_container_width=True)
            else:
                areas_data = acumulados.get('areas', {})
                if areas_data:
                    df_pasivos_area = pd.DataFrame([
                        {'Área': area, 'Pasivos': area_data.get('costos_adelantos', 0) + area_data.get('costos_prestamos', 0)}
                        for area, area_data in areas_data.items()
                    ]).sort_values('Pasivos', ascending=True)
                    fig = px.barh(df_pasivos_area, x='Pasivos', y='Área', title='Total Pasivos por Área',
                                 color_discrete_sequence=[MARRÓN_CLARO])
                    st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")
        st.metric("💼 Total Pasivos", formatear_moneda(total_pasivos))

        st.markdown(f"""
        **Composición:**
        - 💰 Adelantos: {formatear_moneda(total_adelantos)} ({(total_adelantos/total_pasivos*100) if total_pasivos > 0 else 0:.1f}%)
        - 🏦 Préstamos: {formatear_moneda(total_prestamos)} ({(total_prestamos/total_pasivos*100) if total_pasivos > 0 else 0:.1f}%)
        - 📊 **Total:** {formatear_moneda(total_pasivos)}
        """)

    # ========================================================================
    # FOOTER
    # ========================================================================

    st.markdown("---")
    col_footer1, col_footer2, col_footer3 = st.columns(3)

    with col_footer1:
        st.markdown(f"""
        <div style='text-align: center; font-size: 11px; color: #999;'>
        <strong>📊 Última Actualización</strong><br>
        {fecha_proc}
        </div>
        """, unsafe_allow_html=True)

    with col_footer2:
        st.markdown(f"""
        <div style='text-align: center; font-size: 11px; color: #999;'>
        <strong>📍 Filtros Activos</strong><br>
        {empresa_sel} | {area_sel} | {periodo_sel}
        </div>
        """, unsafe_allow_html=True)

    with col_footer3:
        st.markdown("""
        <div style='text-align: center; font-size: 11px; color: #999;'>
        <strong>🔄 Actualización</strong><br>
        Diaria a las 9:30 AM (UY)
        </div>
        """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style='text-align: center; color: #ccc; font-size: 11px; margin-top: 20px; border-top: 1px solid {MARRÓN_CLARO}; padding-top: 20px;'>
    Dashboard RRHH - Grupo Raval | Datos automáticos desde Excel |
    <a href='https://github.com/brunobarla' style='color: {MARRÓN_CLARO};' target='_blank'>GitHub</a>
    </div>
    """, unsafe_allow_html=True)

else:
    st.error("❌ No se pudieron cargar los datos. Verifica que indicadores_rrhh.json exista.")
    st.markdown("""
    ### Pasos para resolver:
    1. Ejecuta el script `procesar_datos_windows.py`
    2. Verifica que se genere `indicadores_rrhh.json`
    3. Recarga esta página
    """)
