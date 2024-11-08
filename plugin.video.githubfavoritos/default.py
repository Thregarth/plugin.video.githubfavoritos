import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin
import requests
import json
import sys
import os

# Inicializar el addon
ADDON = xbmcaddon.Addon()
# Obtener el token de GitHub y el repositorio de las configuraciones del addon
GITHUB_TOKEN = ADDON.getSetting('github_token')
GITHUB_REPO = ADDON.getSetting('github_repo')

# Función para guardar los favoritos en GitHub
def guardar_favoritos():
    # Obtener los favoritos de Kodi usando JSON-RPC
    favoritos = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "Favourites.GetFavourites", "id": 1}')
    favoritos = json.loads(favoritos)
    
    # Verificar si hay favoritos disponibles
    if "result" in favoritos and "favourites" in favoritos["result"]:
        favoritos = favoritos["result"]["favourites"]
        # Convertir los favoritos a formato JSON con una indentación para mayor legibilidad
        data = json.dumps(favoritos, indent=4)
        # Subir los favoritos al repositorio de GitHub
        subir_a_github(data)
    else:
        # Mostrar notificación si no hay favoritos
        xbmcgui.Dialog().notification('Favoritos a GitHub', 'No hay favoritos para guardar', xbmcgui.NOTIFICATION_INFO, 5000)

# Función para subir datos a GitHub
def subir_a_github(data):
    # URL del archivo en el repositorio de GitHub
    url = f'https://api.github.com/repos/{GITHUB_REPO}/contents/favoritos.json'
    headers = {
        'Authorization': f'token {GITHUB_TOKEN}',
        'Accept': 'application/vnd.github.v3+json'
    }

    # Verificar si el archivo ya existe en el repositorio para obtener su SHA
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        # Si el archivo ya existe, obtener el SHA para actualizarlo
        sha = response.json().get('sha')
        payload = {
            'message': 'Actualizando favoritos',
            'content': data.encode('utf-8').decode('ascii'),
            'sha': sha
        }
    else:
        # Si el archivo no existe, crearlo
        payload = {
            'message': 'Creando archivo de favoritos',
            'content': data.encode('utf-8').decode('ascii')
        }

    # Realizar la solicitud PUT para crear o actualizar el archivo en el repositorio
    response = requests.put(url, headers=headers, data=json.dumps(payload))

    # Notificar al usuario sobre el resultado
    if response.status_code in [200, 201]:
        xbmcgui.Dialog().notification('Favoritos a GitHub', 'Favoritos guardados exitosamente', xbmcgui.NOTIFICATION_INFO, 5000)
    else:
        xbmcgui.Dialog().notification('Favoritos a GitHub', f'Error al guardar favoritos: {response.content}', xbmcgui.NOTIFICATION_ERROR, 5000)

# Función para integrar la lógica del menú de Kodi
def run():
    # Crear una entrada en el menú del addon
    url = sys.argv[0] + "?action=guardar"
    li = xbmcgui.ListItem("Guardar Favoritos en GitHub")
    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=li, isFolder=False)
    xbmcplugin.endOfDirectory(int(sys.argv[1]))

# Punto de entrada del script
if __name__ == '__main__':
    # Obtener los parámetros que se pasan al script
    params = dict(arg.split("=") for arg in sys.argv[2][1:].split("&") if len(arg.split("=")) == 2)
    action = params.get("action")
    
    if action == "guardar":
        # Ejecutar la función para guardar favoritos si se selecciona esa acción
        guardar_favoritos()
    else:
        # De lo contrario, mostrar el menú del addon
        run()
