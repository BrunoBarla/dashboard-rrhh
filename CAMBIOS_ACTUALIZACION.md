# Dashboard RRHH - Actualización v2.0

## 🎯 Cambios Realizados

### 1. **Filtros Funcionales** ✅
- ✅ Filtro **Empresa** ahora filtra correctamente los datos
- ✅ Filtro **Área** ahora **cascada automáticamente** según empresa seleccionada
- ✅ Filtro **Período** ahora filtra datos por mes (o "Acumulado")
- ✅ Los datos se actualizan en tiempo real al cambiar filtros

**Cómo funciona:**
1. Selecciona una **Empresa** → automáticamente aparecen solo las Áreas de esa empresa
2. Selecciona un **Período** → todas las métricas se actualizan a ese mes
3. Los 4 módulos muestran los datos filtrados

---

### 2. **Descriptions y Fórmulas** 📐

Cada indicador ahora muestra:
- **📐 Fórmula:** Cómo se calcula la métrica
- **📊 Componentes:** Qué variables/elementos incluye

#### **TAB 1: Costos Nominales**
- `💵 Costo Total`: Suma de salarios + beneficios
  - Componentes: Sueldo base, antigüedad, comisiones, asignaciones
  
- `🏢 Empresas`: Cantidad de empresas (1 o 3)
  - Componentes: Grupo Raval

- `👥 Personas`: Cantidad de empleados activos
  - Componentes: Base de datos ADP

#### **TAB 2: Horas Extras**
- `💵 Costo Total`: Suma de costos de HE
  - Componentes: Horas 50%, Horas 100%, Feriados
  
- `📅 Total Días`: Cantidad de días con HE
  - Componentes: Días en horario extendido

- `💸 Promedio/Día`: Costo Total ÷ Total Días
  - Componentes: Distribución uniforme

- `📊 % de Nómina`: (Costo HE ÷ Costo Nominal) × 100
  - Componentes: Impacto en nómina total

#### **TAB 3: Licencias**
- 🚧 En desarrollo (próximamente)
  - Mostrará: días utilizados, disponibles, por empleado, proyección anual

#### **TAB 4: Adelantos y Préstamos**
- `💰 Adelantos`: Suma de adelantos de salario
  - Componentes: Adelantos simples + en cuotas
  
- `🏦 Préstamos`: Suma de préstamos en nómina
  - Componentes: Préstamos personales y emergencias

- `📊 % de Nómina`: (Total Pasivos ÷ Costo Nominal) × 100
  - Componentes: Impacto en nómina

- `💼 Total Pasivos`: Suma de Adelantos + Préstamos
  - Componentes: Desglose con porcentajes

---

### 3. **Mejoras de Diseño** 🎨

- ✅ Descriptions visuales bajo cada métrica (estilo card)
- ✅ Colores destacados para fórmulas y componentes
- ✅ Footer mejorado con:
  - Última actualización
  - Filtros activos
  - Horario de actualización (9:30 AM UY)
- ✅ Gráficos con mejor legibilidad y paleta de colores consistente
- ✅ Mensaje informativo en sidebar sobre cascada de filtros

---

### 4. **Cambios Técnicos** ⚙️

#### Nueva función `obtener_datos_filtrados()`
```python
def obtener_datos_filtrados(datos, empresa, area, periodo):
    """
    Filtra datos según:
    - Empresa seleccionada
    - Área seleccionada (solo de esa empresa)
    - Período seleccionado (o "Acumulado")
    
    Retorna diccionario con métricas filtradas
    """
```

#### Mejoras de variables
- Todos los tabs usan `acumulados` (variable global)
- Variables se actualizan automáticamente con filtros
- Calculus de porcentajes dinámicos (% de Nómina)

---

## 🚀 Pasos para Usar

1. **Ve a:** https://dashboard-rrhh.streamlit.app/

2. **Abre el sidebar** (izquierda) y verás:
   ```
   🔍 FILTROS
   ├─ Empresa: [Todas] [Empresa 1] [Empresa 2] [Empresa 3]
   ├─ Área: [Todas] [Área 1] [Área 2] ... (cascada)
   └─ Período: [Acumulado] [Enero] [Febrero] ... [Diciembre]
   ```

3. **Selecciona filtros:**
   - Primero: **Empresa** (para que Área se actualice)
   - Segundo: **Área** (opcional, si quieres filtrar más)
   - Tercero: **Período** (para ver datos de un mes específico)

4. **Los 4 módulos se actualizan automáticamente:**
   - 💰 Costos Nominales
   - ⏰ Horas Extras
   - 🏖️ Licencias (en desarrollo)
   - 📋 Adelantos y Préstamos

---

## 📋 Próximos Pasos (FASE 2)

Una vez valides que los **diseño y filtros** funcionan correctamente, haremos:

1. ✅ **Validación de Cálculos:**
   - Comparar con PowerPoint de especificaciones
   - Verificar que fórmulas sean exactas

2. ✅ **Módulo de Licencias:**
   - Integrar datos de licencias
   - Mostrar: días utilizados, disponibles, proyección

3. ✅ **Dashboard "Soft":**
   - Crear segundo dashboard para:
     - Onboardings
     - Offboardings
     - Evaluaciones de desempeño
     - Beneficios

---

## 🔧 Troubleshooting

**¿Los filtros no funcionan?**
- Espera a que Streamlit recargue (~30 segundos)
- Recarga la página (F5)

**¿Falta un período?**
- El archivo `indicadores_rrhh.json` debe estar actualizado
- Ejecuta `procesar_datos_windows.py` en tu PC

**¿Los números no son correctos?**
- Revisa los datos del JSON con la especificación en PowerPoint
- Pasamos a FASE 2 para validar cálculos

---

## 📞 Contacto

Cualquier duda o issue, avísame!
