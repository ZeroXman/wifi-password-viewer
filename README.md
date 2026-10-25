# WiFi Password Viewer

Aplicación web interactiva multiplataforma para visualizar perfiles Wi-Fi guardados y sus contraseñas.

## Características

- **Multiplataforma**: Detecta automáticamente Windows, Linux (NetworkManager) o macOS
- **Extracción nativa**: Usa comandos nativos del sistema (`netsh`, `nmcli`, `security`)
- **Dashboard con métricas**: Total de redes, contraseñas recuperadas, tasa de éxito
- **Búsqueda en tiempo real**: Filtra perfiles por nombre de red
- **Mostrar/Ocultar contraseñas**: Por privacidad, las contraseñas vienen enmascaradas por defecto
- **Exportación**: Descarga reporte en formato CSV o JSON
- **Interfaz moderna**: Diseño oscuro con layout wide

## Instalación

```bash
pip install -r requirements.txt
```

## Uso

```bash
streamlit run app.py
```

## Requisitos por Sistema

| SO | Método | Notas |
|---|---|---|
| **Windows** | `netsh wlan` | Recomendado ejecutar como Administrador |
| **Linux** | `nmcli` / NetworkManager | Puede requerir `sudo` para archivos de conexión |
| **macOS** | `security` (Keychain) | Puede solicitar autorización del Llavero |

## Advertencia

Esta herramienta está diseñada únicamente para recuperar **tus propias redes Wi-Fi guardadas**. Úsala de forma responsable y ética.

## Licencia

MIT
