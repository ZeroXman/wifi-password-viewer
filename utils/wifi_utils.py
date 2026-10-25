import subprocess
import re
import sys
import os

def get_os():
    """Detecta el sistema operativo actual."""
    plat = sys.platform
    if plat.startswith('win'):
        return 'windows'
    elif plat == 'darwin':
        return 'macos'
    elif plat.startswith('linux'):
        return 'linux'
    return 'unknown'

def get_wifi_profiles():
    """Extrae los perfiles de Wi-Fi guardados según el sistema operativo."""
    os_type = get_os()
    profiles = []

    if os_type == 'windows':
        try:
            output = subprocess.check_output(
                ["netsh", "wlan", "show", "profiles"],
                shell=True,
                text=True,
                encoding='cp437',
                errors='ignore'
            )
            for line in output.splitlines():
                if "All User Profile" in line or "Perfil de todos los usuarios" in line:
                    profile = line.split(":")[-1].strip()
                    if profile:
                        profiles.append(profile)
        except subprocess.CalledProcessError as e:
            print(f"Error al obtener perfiles Wi-Fi: {e}")
        except Exception as e:
            print(f"Error inesperado: {e}")
        return profiles

    elif os_type == 'linux':
        try:
            output = subprocess.check_output(
                ["nmcli", "-t", "-f", "NAME,TYPE", "connection", "show"],
                text=True,
                errors='ignore'
            )
            for line in output.splitlines():
                if ':802-11-wireless' in line or ':wifi' in line:
                    profile = line.split(':')[0].strip()
                    if profile and profile not in profiles:
                        profiles.append(profile)
            return profiles
        except Exception as e:
            print(f"Error al obtener perfiles con nmcli: {e}")
            return []

    elif os_type == 'macos':
        try:
            output = subprocess.check_output(
                ["networksetup", "-listpreferredwirelessnetworks", "en0"],
                text=True,
                errors='ignore'
            )
            for line in output.splitlines():
                line = line.strip()
                if line and not line.startswith('Preferred'):
                    profiles.append(line)
            return profiles
        except Exception as e:
            print(f"Error al obtener redes en macOS: {e}")
            return []

    return profiles

def get_wifi_password(profile_name):
    """Obtiene la contraseña del perfil Wi-Fi según el sistema operativo."""
    os_type = get_os()

    if os_type == 'windows':
        try:
            output = subprocess.check_output(
                ["netsh", "wlan", "show", "profile", f'name="{profile_name}"', "key=clear"],
                shell=True,
                text=True,
                encoding='cp437',
                errors='ignore'
            )
            for line in output.splitlines():
                if "Key Content" in line or "Contenido de la clave" in line:
                    password = line.split(":")[-1].strip()
                    return password if password else "Sin Contraseña"
            return "Sin Contraseña"
        except subprocess.CalledProcessError:
            return "N/A"
        except Exception:
            return "N/A"

    elif os_type == 'linux':
        try:
            path_nm = f"/etc/NetworkManager/system-connections/{profile_name}.nmconnection"
            if os.path.exists(path_nm):
                try:
                    with open(path_nm, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    match = re.search(r'psk=(.+)', content)
                    if match:
                        return match.group(1).strip()
                    return "Sin Contraseña"
                except PermissionError:
                    return "Requiere permisos root/sudo"
            else:
                try:
                    output = subprocess.check_output(
                        ["nmcli", "-s", "-g", "802-11-wireless-security.psk", "connection", "show", profile_name],
                        text=True,
                        errors='ignore'
                    )
                    pwd = output.strip()
                    return pwd if pwd and pwd != "--" else "Sin Contraseña"
                except Exception:
                    return "N/A"
        except Exception:
            return "N/A"

    elif os_type == 'macos':
        try:
            output = subprocess.check_output(
                ["security", "find-generic-password", "-D", "AirPort network password", "-a", profile_name, "-w"],
                stderr=subprocess.STDOUT,
                text=True,
                errors='ignore'
            )
            pwd = output.strip()
            return pwd if pwd else "Sin Contraseña"
        except subprocess.CalledProcessError:
            return "N/A"
        except Exception:
            return "N/A"

    return "N/A"

def get_all_wifi_data():
    """Obtiene todos los datos de Wi-Fi guardados."""
    os_type = get_os()
    profiles = get_wifi_profiles()
    data = []
    for profile in profiles:
        password = get_wifi_password(profile)
        data.append({
            "Perfil": profile,
            "Contraseña": password
        })
    return data, os_type
