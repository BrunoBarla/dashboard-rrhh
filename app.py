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

# ============================================================================
# CONFIGURACIÓN
# ============================================================================

st.set_page_config(
    page_title="Dashboard RRHH - Grupo Raval",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado
st.markdown("""
    <style>
        .metric-card {
            background-color: #f0f2f6;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            margin: 10px 0;
        }
        .metric-value {
            font-size: 28px;
            font-weight: bold;
            color: #1f77b4;
        }
        .metric-label {
            font-size: 12px;
            color: #666;
            margin-top: 5px;
        }
    </style>
""", unsafe_allow_html=True)

# ============================================================================
# CARGAR DATOS
# ============================================================================

@st.cache_data
def cargar_datos():
    """Carga los datos del JSON"""
    try:
        # Intenta cargar desde el directorio actual (para pruebas locales)
        if Path('indicadores_rrhh.json').exists():
            with open('indicadores_rrhh.json', 'r', encoding='utf-8') as f:
                return json.load(f)

        # Si no existe localmente, retorna datos de ejemplo
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

# ============================================================================
# FUNCIONES AUXILIARES
# ============================================================================

def formatear_moneda(valor):
    """Formatea un valor como moneda uruguaya"""
    if valor is None:
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
        return list(datos['acumulados']['empresas'].keys())
    return []

def obtener_areas(datos, empresa):
    """Obtiene áreas de una empresa"""
    if datos and 'acumulados' in datos and 'areas' in datos['acumulados']:
        areas = datos['acumulados']['areas']
        if empresa == "Todas":
            return list(areas.keys())
        # Filtrar áreas por empresa
        return [a for a in areas.keys() if areas[a].get('empresa') == empresa]
    return []

def obtener_periodos(datos):
    """Obtiene lista de períodos"""
    if datos and 'por_periodo' in datos:
        periodos = list(datos['por_periodo'].keys())
        return sorted(periodos, reverse=True)
    return []

# ============================================================================
# INTERFAZ PRINCIPAL
# ============================================================================

st.title("📊 Dashboard RRHH - Grupo Raval")
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
        st.header("🔍 Filtros")

        # Empresa
        empresas = obtener_empresas(datos)
        empresa_sel = st.selectbox(
            "Empresa",
            ["Todas"] + empresas,
            key="empresa"
        )

        # Área
        areas = obtener_areas(datos, empresa_sel)
        area_sel = st.selectbox(
            "Área",
            ["Todas"] + areas,
            key="area"
        )

        # Período
        periodos = obtener_periodos(datos)
        periodo_sel = st.selectbox(
            "Período",
            ["Acumulado"] + periodos,
            key="periodo"
        )

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
        st.header("Costos Nominales")

        acumulados = datos.get('acumulados', {})

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "💵 Costo Total",
                formatear_moneda(acumulados.get('costos_nominales', 0))
            )

        with col2:
            num_empresas = len(acumulados.get('empresas', {}))
            st.metric("🏢 Empresas", f"{num_empresas}")

        with col3:
            num_personas = len(acumulados.get('personas', {}))
            st.metric("👥 Personas", f"{num_personas}")

        st.markdown("---")

        # Gráfico de empresas
        empresas_data = acumulados.get('empresas', {})
        if empresas_data:
            df_empresas = pd.DataFrame([
                {'Empresa': emp, 'Costo': datos_emp.get('costos_nominales', 0)}
                for emp, datos_emp in empresas_data.items()
            ])

            fig = px.bar(
                df_empresas,
                x='Empresa',
                y='Costo',
                title='Costos por Empresa',
                color='Empresa',
                text='Costo'
            )
            fig.update_traces(texttemplate='$%{text:,.0f}', textposition='outside')
            st.plotly_chart(fig, use_container_width=True)

    # ========================================================================
    # TAB 2: HORAS EXTRAS
    # ========================================================================

    with tab2:
        st.header("Horas Extras")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "💵 Costo Total",
                formatear_moneda(acumulados.get('costos_horas_extras', 0))
            )

        with col2:
            st.metric(
                "📅 Total Días",
                formatear_numero(acumulados.get('total_horas_extras_dias', 0))
            )

        with col3:
            costo_total = acumulados.get('costos_horas_extras', 0)
            dias_total = acumulados.get('total_horas_extras_dias', 0)
            costo_promedio = costo_total / dias_total if dias_total > 0 else 0
            st.metric("💸 Costo Promedio por Día", formatear_moneda(costo_promedio))

        with col4:
            st.metric("⚠️ Estado", "Activo")

        st.markdown("---")
        st.info("📌 Vista dual: Costos ($) y Días trabajados")

    # ========================================================================
    # TAB 3: LICENCIAS
    # ========================================================================

    with tab3:
        st.header("Licencias")

        st.info("🚧 Módulo en desarrollo")
        st.markdown("""
        Este módulo mostrará:
        - Licencias utilizadas
        - Días disponibles
        - Por empleado
        - Proyección anual
        """)

    # ========================================================================
    # TAB 4: ADELANTOS Y PRÉSTAMOS
    # ========================================================================

    with tab4:
        st.header("Adelantos y Préstamos")

        col1, col2 = st.columns(2)

        with col1:
            st.metric(
                "💰 Adelantos",
                formatear_moneda(acumulados.get('costos_adelantos', 0))
            )

        with col2:
            st.metric(
                "🏦 Préstamos",
                formatear_moneda(acumulados.get('costos_prestamos', 0))
            )

        st.markdown("---")

        col1, col2 = st.columns(2)

        with col1:
            total_adelantos = acumulados.get('costos_adelantos', 0)
            total_prestamos = acumulados.get('costos_prestamos', 0)
            total_pasivos = total_adelantos + total_prestamos

            fig = go.Figure(data=[
                go.Pie(
                    labels=['Adelantos', 'Préstamos'],
                    values=[total_adelantos, total_prestamos],
                    hole=0.3
                )
            ])
            fig.update_layout(title='Proporción Adelantos vs Préstamos')
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.metric("📊 Total Pasivos", formatear_moneda(total_pasivos))
            st.markdown(f"""
            - **Adelantos:** {formatear_moneda(total_adelantos)}
            - **Préstamos:** {formatear_moneda(total_prestamos)}
            - **Total:** {formatear_moneda(total_pasivos)}
            """)

    # ========================================================================
    # FOOTER
    # ========================================================================

    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; font-size: 12px;'>
    Dashboard RRHH - Grupo Raval | Datos actualizados diariamente |
    <a href='#' style='color: #1f77b4;'>API de Datos</a>
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
