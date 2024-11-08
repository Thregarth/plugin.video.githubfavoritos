import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin
import requests
import json

ADDON = xbmcaddon.Addon()
GITHUB_TOKEN = ADDON.getSetting('github_token')
GITHUB_REPO = ADDON.getSetting('github_repo')

def guardar_favoritos():
    # Obtener favoritos de Kodi
    favoritos = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "Favourites.GetFavourites", "id": 1}')
    favoritos = json.loads(favoritos)
    
    # Verificar que hay favoritos
    if "result" in favoritos and "favourites" in favoritos["result"]:
        favoritos = favoritos["result"]["favourites"]
        # Convertir los favoritos a formato JSON para guardar
        data = json.dumps(favoritos, indent=4)
        # Subir a GitHub
        subir_a_github(data)
    else:
        xbmcgui.Dialog().notification('Favoritos a GitHub', 'No hay favoritos para guardar', xbmcgui.NOTIFICATION_INFO, 5000)

def subir_a_github(data):
    # URL del archivo en GitHub
    url = f'https://api.github.com/repos/{GITHUB_REPO}/contents/favoritos.json'
    headers = {
        'Authorization': f'token {GITHUB_TOKEN}',
        'Accept': 'application/vnd.github.v3+json'
    }

    # Verificar si el archivo ya existe en el repositorio
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        sha = response.json()['sha']
        payload = {
            'message': 'Actualizando favoritos',
            'content': data.encode('utf-8').decode('ascii'),
            'sha': sha
        }
    else:
        payload = {
            'message': 'Creando archivo de favoritos',
            'content': data.encode('utf-8').decode('ascii')
        }

    # Hacer la solicitud PUT para crear o actualizar el archivo
    response = requests.put(url, headers=headers, data=json.dumps(payload))

    if response.status_code in [200, 201]:
        xbmcgui.Dialog().notification('Favoritos a GitHub', 'Favoritos guardados exitosamente', xbmcgui.NOTIFICATION_INFO, 5000)
    else:
        xbmcgui.Dialog().notification('Favoritos a GitHub', 'Error al guardar favoritos', xbmcgui.NOTIFICATION_ERROR, 5000)

def run():
    # Crear una entrada en el menú
    url = sys.argv[0] + "?action=guardar"
    li = xbmcgui.ListItem("Guardar Favoritos en GitHub")
    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=li, isFolder=False)
    xbmcplugin.endOfDirectory(int(sys.argv[1]))

if __name__ == '__main__':
    params = dict(arg.split("=") for arg in sys.argv[2][1:].split("&") if len(arg.split("=")) == 2)
    action = params.get("action")
    if action == "guardar":
        guardar_favoritos()
    else:
        run()
