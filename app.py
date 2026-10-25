import streamlit as st
import pandas as pd
import json
import csv
import io
import sys
from utils.wifi_utils import get_all_wifi_data, get_os

# Configuración inicial de la página
st.set_page_config(
    page_title="WiFi Password Viewer",
    page_icon="📶",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS personalizados para diseño moderno oscuro
st.markdown("""
<style>
    .main {
        background-color: #0e1117;
    }
    .stMetric {
        background-color: #1e1e1e;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #2d2d2d;
    }
    .stDataFrame {
        border-radius: 10px;
        overflow: hidden;
    }
    h1 {
        color: #4f9deb;
    }
    .info-box {
        padding: 15px;
        background-color: #1e3a5f;
        border-radius: 10px;
        border-left: 4px solid #4f9deb;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# Cabecera
st.title("📶 WiFi Password Viewer")
st.markdown("**Aplicación multiplataforma para visualizar perfiles Wi-Fi guardados y sus contraseñas**")
st.markdown("---")

# Detección del sistema operativo
os_type = get_os()
os_name = {
    "windows": "Windows",
    "linux": "Linux",
    "macos": "macOS",
    "unknown": "Desconocido"
}.get(os_type, "Desconocido")

# Información del sistema
st.markdown(f"<div class='info-box'>🖥️ <b>Sistema Operativo detectado:</b> {os_name} ({sys.platform})</div>", unsafe_allow_html=True)

# Validación por plataforma
if os_type == "unknown":
    st.error("⚠️ Sistema operativo no soportado. Esta aplicación funciona en Windows, Linux (NetworkManager) y macOS.")
    st.stop()

if os_type == "windows":
    st.info("💡 Recomendado: Ejecutar Streamlit como **Administrador** para asegurar la recuperación completa de las contraseñas.")
elif os_type == "linux":
    st.info("💡 En Linux con NetworkManager, puede requerirse permisos de **root/sudo** para leer archivos en `/etc/NetworkManager/system-connections/`.")
elif os_type == "macos":
    st.info("💡 En macOS, es posible que se solicite acceso al **Llavero** al ejecutar el comando.")

# Obtener datos
with st.spinner(f"🔍 Escaneando perfiles Wi-Fi guardados en {os_name}..."):
    wifi_data, detected_os = get_all_wifi_data()

if not wifi_data:
    st.warning(f"⚠️ No se encontraron perfiles Wi-Fi guardados en este sistema {os_name}.")
    if os_type == "linux":
        st.markdown("Asegúrate de tener **NetworkManager** instalado y permisos adecuados.")
    elif os_type == "macos":
        st.markdown("Verifica que tengas redes guardadas en tu lista de Wi-Fi preferidas.")
    st.stop()

# Crear DataFrame
df = pd.DataFrame(wifi_data)

# Calcular métricas
total_profiles = len(df)
successful_passwords = len(df[~df['Contraseña'].isin(['N/A', 'Sin Contraseña', 'Requiere permisos root/sudo'])])
success_rate = round((successful_passwords / total_profiles * 100) if total_profiles > 0 else 0, 2)

# Mostrar métricas
col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="📡 Total de Redes Encontradas", value=total_profiles)
with col2:
    st.metric(label="🔑 Contraseñas Recuperadas", value=successful_passwords)
with col3:
    st.metric(label="✅ Tasa de Éxito", value=f"{success_rate}%")

st.markdown("---")

# Filtros y opciones
col_search, col_toggle = st.columns([3, 1])
with col_search:
    search_term = st.text_input("🔍 Buscar red por nombre", placeholder="Escribe el nombre de la red...")
with col_toggle:
    show_passwords = st.checkbox("Mostrar contraseñas en texto plano", value=False)

# Filtrar datos
if search_term:
    filtered_df = df[df['Perfil'].str.contains(search_term, case=False, na=False)]
else:
    filtered_df = df.copy()

# Preparar vista
display_df = filtered_df.copy()
if not show_passwords:
    display_df['Contraseña'] = display_df['Contraseña'].apply(
        lambda x: '••••••••' if x not in ['N/A', 'Sin Contraseña', 'Requiere permisos root/sudo'] else x
    )

# Mostrar tabla
st.subheader("📋 Listado de Perfiles Wi-Fi")
st.dataframe(
    display_df,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Perfil": st.column_config.TextColumn("Nombre de Red", width="medium"),
        "Contraseña": st.column_config.TextColumn("Contraseña", width="medium"),
    }
)

st.markdown(f"*Mostrando {len(display_df)} de {total_profiles} perfiles*")
st.markdown("---")

# Exportación de datos
st.subheader("📥 Exportar Reporte")
col_csv, col_json = st.columns(2)

# Exportar CSV (con contraseñas visibles para el archivo)
export_df = filtered_df.copy()

with col_csv:
    csv_buffer = io.StringIO()
    export_df.to_csv(csv_buffer, index=False, encoding='utf-8-sig')
    csv_data = csv_buffer.getvalue()
    st.download_button(
        label="Descargar como CSV",
        data=csv_data,
        file_name=f"wifi_passwords_{detected_os}_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv",
        use_container_width=True
    )

with col_json:
    json_data = json.dumps(export_df.to_dict(orient='records'), indent=4, ensure_ascii=False)
    st.download_button(
        label="Descargar como JSON",
        data=json_data,
        file_name=f"wifi_passwords_{detected_os}_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.json",
        mime="application/json",
        use_container_width=True
    )

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #6c757d;'>
    <small>WiFi Password Viewer | Multiplataforma | Uso responsable - Solo para redes propias guardadas</small>
</div>
""", unsafe_allow_html=True)
