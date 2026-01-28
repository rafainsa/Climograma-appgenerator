import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np

# 1. LÓGICA DE CLASIFICACIÓN KÖPPEN (Incluye todas las letras)
def clasificar_koppen_completo(temps, precs):
    t_media = sum(temps) / 12
    p_total = sum(precs)
    t_max, t_min = max(temps), min(temps)
    umbral = 20 * t_media 
    if p_total < umbral:
        clase = "BW" if p_total < umbral / 2 else "BS"
        sub = "h" if t_media >= 18 else "k"
        return f"{clase}{sub}", "Aridez detectada."
    if t_min >= 18:
        return ("Af", "Ecuatorial") if min(precs) >= 60 else ("Aw", "Tropical")
    grupo = "C" if t_min > -3 else "D"
    if min(precs[5:8]) < 30 and max(precs[0:3]) > 3 * min(precs[5:8]): sub1 = "s"
    elif min(precs[0:3]) < max(precs[5:8])/10: sub1 = "w"
    else: sub1 = "f"
    sub2 = "a" if t_max >= 22 else ("b" if len([t for t in temps if t > 10]) >= 4 else "c")
    return f"{grupo}{sub1}{sub2}", f"Clima tipo {grupo}{sub1}{sub2}"

# 2. CONFIGURACIÓN APP
st.set_page_config(page_title="Climograma Profesional", layout="wide")
st.title("📊 Generador de Climogramas (Soporte Temperaturas Negativas)")

localidad = st.text_input("📍 Localidad:", "Teruel")
meses = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']

col_t, col_p = st.columns(2)
with col_t:
    st.subheader("🌡️ Temperaturas (°C)")
    t_input = [st.number_input(f"T {m}", value=5.0, step=0.1, key=f"t_{m}") for m in meses]
with col_p:
    st.subheader("🌧️ Precipitaciones (mm)")
    p_input = [st.number_input(f"P {m}", value=30.0, step=1.0, key=f"p_{m}") for m in meses]

if st.button("🚀 Generar Climograma e Informe"):
    # Estadísticas
    t_anual, p_anual = sum(t_input)/12, sum(p_input)
    t_max, t_min = max(t_input), min(t_input)
    osc_termica = t_max - t_min
    idx_martonne = p_anual / (t_anual + 10)
    kop_cod, kop_desc = clasificar_koppen_completo(t_input, p_input)

    # GRÁFICO PROFESIONAL
    fig, ax1 = plt.subplots(figsize=(11, 8))
    ax2 = ax1.twinx()

    # Cálculo de límites proporcionales (Gaussen)
    # Buscamos el valor más alejado del cero para equilibrar
    max_val_p = max(max(p_input), max(t_input)*2, 40)
    min_val_t = min(t_min, 0)
    
    # Ajuste de límites para que el 0 coincida
    # Si t_min es -10, el eje P debe bajar a -20
    lim_inf_t = (min_val_t // 5) * 5
    lim_sup_t = (max(t_max, max_val_p/2) // 5 + 1) * 5
    
    ax2.set_ylim(lim_inf_t, lim_sup_t)
    ax1.set_ylim(lim_inf_t * 2, lim_sup_t * 2)

    # Dibujo
    ax1.bar(meses, p_input, color='blue', alpha=0.6, width=1.0, edgecolor='white', zorder=1)
    ax2.plot(meses, t_input, color='red', marker='o', linewidth=2.5, zorder=2)
    
    # Eje horizontal en el cero
    ax2.axhline(0, color='black', linewidth=1.5, zorder=3)

    # Formato de unidades y etiquetas
    ax1.set_ylabel('Precipitación (mm)', color='blue', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Temperatura (°C)', color='red', fontsize=12, fontweight='bold')
    
    # Ocultar etiquetas negativas en el eje de precipitación (físicamente no hay lluvia negativa)
    ax1.set_yticklabels([f'{int(val)}' if val >= 0 else '' for val in ax1.get_yticks()])
    
    # Cuadrícula y estética
    ax1.grid(True, which='major', axis='y', linestyle='--', alpha=0.4)
    for i in range(len(meses)):
        ax1.axvline(i + 0.5, color='gray', linewidth=0.5, alpha=0.3)

    st.pyplot(fig)

    # INFORME FINAL
    st.divider()
    st.subheader(f"📈 Análisis: {localidad}")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("T. Media Anual", f"{t_anual:.1f} °C")
        st.metric("P. Total Anual", f"{p_anual:.0f} mm")
    with c2:
        st.metric("T. Mes más Cálido", f"{t_max:.1f} °C")
        st.metric("T. Mes más Frío", f"{t_min:.1f} °C")
    with c3:
        st.metric("Oscilación Térmica", f"{osc_termica:.1f} °C")
        st.metric("Índice de Martonne", f"{idx_martonne:.1f}")

    st.success(f"**Clasificación de Köppen Completa:** {kop_cod} — {kop_desc}")
