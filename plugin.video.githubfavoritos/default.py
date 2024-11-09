import sys
import os


# Añadir la carpeta `resources/lib` al path de Python para que pueda encontrar las librerías necesarias
addon_path = os.path.dirname(__file__)
lib_path = os.path.join(addon_path, 'resources', 'lib')
sys.path.append(lib_path)

import base64
import xbmc
import xbmcgui
import xbmcaddon
import xbmcvfs
import requests
import json

# Inicializar el addon
ADDON = xbmcaddon.Addon()
GITHUB_TOKEN = ADDON.getSetting('github_token')
GITHUB_REPO = ADDON.getSetting('github_repo')
addon_profile = xbmcvfs.translatePath(ADDON.getAddonInfo('profile'))
favoritos_path = os.path.join(addon_profile, 'favoritos.json')

# Crear el directorio de perfil si no existe
if not xbmcvfs.exists(addon_profile):
    xbmcvfs.mkdir(addon_profile)

# Función para guardar el elemento seleccionado en favoritos.json
def guardar_favorito():
    # Obtener información del elemento seleccionado
    item = xbmc.getInfoLabel('ListItem.Label')
    path = xbmc.getInfoLabel('ListItem.FileNameAndPath')

    if not item or not path:
        xbmcgui.Dialog().notification('Error', 'No se pudo obtener la información del elemento.', xbmcgui.NOTIFICATION_ERROR, 5000)
        return

    # Crear un diccionario con la información
    favorito = {
        'title': item,
        'path': path
    }

    # Leer el archivo favoritos.json si existe
    if xbmcvfs.exists(favoritos_path):
        with xbmcvfs.File(favoritos_path, 'r') as f:
            try:
                favoritos = json.load(f)
            except json.JSONDecodeError:
                favoritos = []
    else:
        favoritos = []

    # Añadir el nuevo favorito
    favoritos.append(favorito)

    # Guardar en favoritos.json
    with xbmcvfs.File(favoritos_path, 'w') as f:
        f.write(json.dumps(favoritos, ensure_ascii=False, indent=4))

    xbmcgui.Dialog().notification('Favorito Guardado', f'{item} ha sido añadido a favoritos.', xbmcgui.NOTIFICATION_INFO, 5000)

    # Subir el archivo a GitHub
    subir_a_github(favoritos_path, "favoritos")

def subir_a_github(file_path, title):
    # Leer el archivo y codificar su contenido en base64
    try:
        with xbmcvfs.File(file_path, 'r') as f:
            file_content = f.read()
        encoded_content = base64.b64encode(file_content.encode('utf-8')).decode('utf-8')
    except Exception as e:
        xbmc.log(f"Error al leer y codificar el archivo: {str(e)}", level=xbmc.LOGERROR)
        xbmcgui.Dialog().notification('Error', 'No se pudo codificar el archivo para subirlo.', xbmcgui.NOTIFICATION_ERROR, 5000)
        return

    # Preparar la solicitud para la API de GitHub
    filename = f"{title.replace(' ', '_')}.json"
    url = f'https://api.github.com/repos/{GITHUB_REPO}/contents/{filename}'
    headers = {
        'Authorization': f'token {GITHUB_TOKEN}',
        'Accept': 'application/vnd.github.v3+json'
    }

    # Verificar si el archivo ya existe en el repositorio para obtener su SHA
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        sha = response.json().get('sha')
        payload = {
            'message': 'Actualizando acceso directo',
            'content': encoded_content,
            'sha': sha
        }
    else:
        payload = {
            'message': 'Creando acceso directo',
            'content': encoded_content
        }

    # Realizar la solicitud PUT para crear o actualizar el archivo en el repositorio
    try:
        response = requests.put(url, headers=headers, data=json.dumps(payload))
    except requests.exceptions.RequestException as e:
        xbmc.log(f"Error en la solicitud HTTP: {str(e)}", level=xbmc.LOGERROR)
        xbmcgui.Dialog().notification('Error', 'Hubo un problema al intentar conectar con GitHub.', xbmcgui.NOTIFICATION_ERROR, 5000)
        return

    # Notificar al usuario sobre el resultado
    if response.status_code in [200, 201]:
        xbmcgui.Dialog().notification('Acceso Directo a GitHub', 'Acceso directo guardado exitosamente en GitHub.', xbmcgui.NOTIFICATION_INFO, 5000)
    elif response.status_code == 401:
        xbmcgui.Dialog().notification('Error de Autenticación', 'Error de autenticación en GitHub. Revisa el token.', xbmcgui.NOTIFICATION_ERROR, 5000)
    else:
        xbmc.log(f"Error al subir archivo a GitHub: {response.status_code} - {response.content.decode('utf-8')}", level=xbmc.LOGERROR)
        xbmcgui.Dialog().notification('Error', f'No se pudo guardar en GitHub: {response.content.decode("utf-8")}', xbmcgui.NOTIFICATION_ERROR, 5000)

# Punto de entrada del script
if __name__ == '__main__':
    guardar_favorito()
