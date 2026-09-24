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

# CSS personalizado con mejoras para descriptions
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
        .metric-description {
            font-size: 11px;
            color: #999;
            margin-top: 10px;
            padding: 8px;
            background-color: #ffffff;
            border-radius: 5px;
            border-left: 3px solid #1f77b4;
            text-align: left;
            line-height: 1.4;
        }
        .formula-label {
            font-weight: bold;
            color: #1f77b4;
            font-size: 10px;
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

def obtener_datos_filtrados(datos: Dict, empresa: str, area: str, periodo: str) -> Dict:
    """
    Filtra los datos según empresa, área y período seleccionados.
    Retorna un diccionario con los datos filtrados.
    """
    if not datos or 'acumulados' not in datos:
        return {}

    # Si el período es "Acumulado", usar acumulados; si no, usar datos del período específico
    if periodo == "Acumulado":
        base_data = datos.get('acumulados', {})
    else:
        base_data = datos.get('por_periodo', {}).get(periodo, {})

    if not base_data:
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

    # Filtrar por empresa
    if empresa != "Todas":
        empresas_data = base_data.get('empresas', {})
        if empresa in empresas_data:
            emp_data = empresas_data[empresa]
            resultado['costos_nominales'] = emp_data.get('costos_nominales', 0)
            resultado['costos_horas_extras'] = emp_data.get('costos_horas_extras', 0)
            resultado['total_horas_extras_dias'] = emp_data.get('total_horas_extras_dias', 0)
            resultado['costos_adelantos'] = emp_data.get('costos_adelantos', 0)
            resultado['costos_prestamos'] = emp_data.get('costos_prestamos', 0)

            # Si se seleccionó una área específica, filtrar áreas
            if area != "Todas":
                areas_data = base_data.get('areas', {})
                if area in areas_data and areas_data[area].get('empresa') == empresa:
                    area_data = areas_data[area]
                    resultado['costos_nominales'] = area_data.get('costos_nominales', 0)
                    resultado['costos_horas_extras'] = area_data.get('costos_horas_extras', 0)
                    resultado['total_horas_extras_dias'] = area_data.get('total_horas_extras_dias', 0)
                    resultado['costos_adelantos'] = area_data.get('costos_adelantos', 0)
                    resultado['costos_prestamos'] = area_data.get('costos_prestamos', 0)
            else:
                # Si no se selecciona área específica, agregar todas las áreas de la empresa
                areas_data = base_data.get('areas', {})
                for area_name, area_info in areas_data.items():
                    if area_info.get('empresa') == empresa:
                        resultado['areas'][area_name] = area_info
    else:
        # Si es "Todas" las empresas, usar datos acumulados
        resultado = base_data.copy()

    return resultado

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
            key="empresa_filter"
        )

        # Área - Cascada según empresa seleccionada
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
        st.info("💡 Los filtros se aplican en cascada. Selecciona Empresa primero para ver sus Áreas.")

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
        st.header("💰 Costos Nominales")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "💵 Costo Total",
                formatear_moneda(acumulados.get('costos_nominales', 0))
            )
            st.markdown("""
            <div class="metric-description">
                <span class="formula-label">📐 Fórmula:</span> Suma de todos los costos de salario y beneficios nominales<br>
                <span class="formula-label">📊 Componentes:</span> Sueldo base, antigüedad, comisiones, asignaciones familiares
            </div>
            """, unsafe_allow_html=True)

        with col2:
            # Contar empresas del filtro
            if empresa_sel == "Todas":
                num_empresas = len(datos.get('acumulados', {}).get('empresas', {}))
            else:
                num_empresas = 1
            st.metric("🏢 Empresas", f"{num_empresas}")
            st.markdown("""
            <div class="metric-description">
                <span class="formula-label">📐 Fórmula:</span> Cantidad de empresas en la selección<br>
                <span class="formula-label">📊 Componentes:</span> Grupo Raval (3 empresas totales)
            </div>
            """, unsafe_allow_html=True)

        with col3:
            # Contar personas del filtro
            if empresa_sel == "Todas":
                num_personas = len(datos.get('acumulados', {}).get('personas', {}))
            else:
                # Contar personas de la empresa seleccionada
                num_personas = len(datos.get('acumulados', {}).get('personas', {}))  # TODO: filtrar por empresa
            st.metric("👥 Personas", f"{num_personas}")
            st.markdown("""
            <div class="metric-description">
                <span class="formula-label">📐 Fórmula:</span> Cantidad de empleados activos<br>
                <span class="formula-label">📊 Componentes:</span> Base de datos ADP - estado activo
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")

        # Gráfico de empresas
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
                color_discrete_sequence=['#1f77b4', '#ff7f0e', '#2ca02c']
            )
            fig.update_traces(texttemplate='$%{text:,.0f}', textposition='outside')
            fig.update_layout(
                showlegend=False,
                yaxis_title="Costo ($)",
                xaxis_title="Empresa",
                hovermode='x unified'
            )
            st.plotly_chart(fig, use_container_width=True)

    # ========================================================================
    # TAB 2: HORAS EXTRAS
    # ========================================================================

    with tab2:
        st.header("⏰ Horas Extras")

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
            pct_costo = (costo_he / acumulados.get('costos_nominales', 1) * 100) if acumulados.get('costos_nominales', 0) > 0 else 0
            st.metric("📊 % de Nómina", f"{pct_costo:.1f}%")
            st.markdown("""
            <div class="metric-description">
                <span class="formula-label">📐 Fórmula:</span> (Costo HE ÷ Costo Nominal) × 100<br>
                <span class="formula-label">📊 Componentes:</span> Impacto en nómina total
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")
        st.info("📌 **Vista Dual:** Costo ($) + Días trabajados en horas extras")

    # ========================================================================
    # TAB 3: LICENCIAS
    # ========================================================================

    with tab3:
        st.header("🏖️ Licencias")

        st.warning("🚧 **Módulo en Desarrollo**")
        st.markdown("""
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
        st.header("📋 Adelantos y Préstamos")

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
            pct_pasivos = (total_pasivos / acumulados.get('costos_nominales', 1) * 100) if acumulados.get('costos_nominales', 0) > 0 else 0
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
                        marker=dict(colors=['#1f77b4', '#ff7f0e'])
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
            total_pasivos = total_adelantos + total_prestamos
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
        st.markdown("""
        <div style='text-align: center; font-size: 11px; color: #999;'>
        <strong>📍 Filtros Activos</strong><br>
        Empresa | Área | Período
        </div>
        """, unsafe_allow_html=True)

    with col_footer3:
        st.markdown("""
        <div style='text-align: center; font-size: 11px; color: #999;'>
        <strong>🔄 Actualización</strong><br>
        Diaria a las 9:30 AM (UY)
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div style='text-align: center; color: #ccc; font-size: 11px; margin-top: 20px;'>
    Dashboard RRHH - Grupo Raval | Datos automáticos desde Excel |
    <a href='https://github.com/brunobarla' style='color: #1f77b4;' target='_blank'>GitHub</a>
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
