import sys
import os
import json
import xbmcplugin
import xbmcgui
import xbmcvfs
import xbmcaddon

# Inicializar el addon y las rutas
ADDON = xbmcaddon.Addon()
addon_profile = xbmcvfs.translatePath(ADDON.getAddonInfo('profile'))
favoritos_path = os.path.join(addon_profile, 'favoritos.json')
handle = int(sys.argv[1])

def listar_favoritos():
    """Lista los elementos en favoritos.json."""
    if not xbmcvfs.exists(favoritos_path):
        xbmcgui.Dialog().notification('Error', 'No se encontraron favoritos.', xbmcgui.NOTIFICATION_ERROR, 5000)
        return

    # Leer favoritos.json
    with xbmcvfs.File(favoritos_path, 'r') as f:
        try:
            favoritos = json.load(f)
        except json.JSONDecodeError:
            xbmcgui.Dialog().notification('Error', 'No se pudo cargar favoritos.', xbmcgui.NOTIFICATION_ERROR, 5000)
            return

    # Crear una entrada para cada favorito en el listado
    for item in favoritos:
        list_item = xbmcgui.ListItem(label=item['ListItem.OriginalTitle'])
        list_item.setInfo('video', {
            'title': item['ListItem.OriginalTitle'],
            'genre': item['ListItem.Genre'],
            'year': item['ListItem.Year'],
            'director': item['ListItem.Director'],
            'plot': item['ListItem.Plot'],
            'rating': item['ListItem.Rating'],
            'tagline': item['ListItem.Tagline'],

        })
        list_item.setArt({'icon': item['ListItem.Icon'], 'fanart': item['ListItem.Art(fanart)']})
        xbmcplugin.addDirectoryItem(handle, item['ListItem.FilenameAndPath'], list_item, isFolder=False)

    xbmcplugin.endOfDirectory(handle)

# Ejecutar listar_favoritos si este archivo se invoca directamente
if __name__ == '__main__':
    listar_favoritos()
