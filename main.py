import os
import time
import json
from mastodon import Mastodon
from stravalib.client import Client

# --- MIS VARIABLES ---
STRAVA_ID = os.getenv('ID_CLIENTE')
STRAVA_SECRET = os.getenv('SECRETO_CLIENTE')
STRAVA_REFRESH = os.getenv('S_TOKEN_ACTUALIZACION')
MASTODON_TOKEN = os.getenv('M_TOKEN_ACCESO')
MASTODON_URL = os.getenv('MASTODON_API') 

ARCHIVO = '/data/history.json'

def conectar_strava():
    try:
        client = Client()
        respuesta = client.refresh_access_token(
            client_id=STRAVA_ID,
            client_secret=STRAVA_SECRET,
            refresh_token=STRAVA_REFRESH
        )
        client.access_token = respuesta['access_token']
        return client
    except:
        print("Fallo al conectar con Strava")
        return None


def buscar_emoji(tipo):
    # Convierto a texto por si acaso
    actividad = str(tipo)
    
    # 1. Correr
    if "Run" in actividad: return "🏃‍♀️"
    
    # 2. Bici 
    elif "Ride" in actividad or "Bike" in actividad: return "🚴‍♀️"
    
    # 3. Nadar
    elif "Swim" in actividad: return "🏊‍♀️"
    
    # 4. Andar
    elif "Walk" in actividad: return "🚶‍♀️"
    elif "Hike" in actividad: return "🥾"
    
    # 5. GIMNASIO Y FUERZA
    elif "Weight" in actividad or "Workout" in actividad or "Crossfit" in actividad: 
        return "🏋️‍♀️"
    
    # 6. Yoga
    elif "Yoga" in actividad: return "🧘‍♀️"
    
    # Emoji por defecto si no sé qué es
    else: return "🏅"

def iniciar_bot():
    print("--- Mirando si hay cosas nuevas ---")

    cuantas = 5
    if not os.path.exists(ARCHIVO):
        print("Primera vez: Voy a bajar las ultimas 40")
        cuantas = 40

    # 1. Conexiones
    cliente_strava = conectar_strava()
    if not cliente_strava: return

    mastodon = Mastodon(access_token=MASTODON_TOKEN, api_base_url=MASTODON_URL)

    # 2. Bajo la lista
    try:
        lista = list(cliente_strava.get_activities(limit=cuantas))
    except:
        return

    # 3. Cargo historial
    subidas = []
    if os.path.exists(ARCHIVO):
        f = open(ARCHIVO, 'r')
        subidas = json.load(f)
        f.close()

    nuevas_subidas = list(subidas)
    
    lista.reverse()

    for resumen in lista:
        if resumen.id in subidas:
            continue
            
        print("Procesando: " + resumen.name)

        # Descripción completa: diferencia entre resumen y descripcion 
        try:
            actividad = cliente_strava.get_activity(resumen.id)
        except:
            actividad = resumen

        # Preparo el mensaje
        emoji = buscar_emoji(actividad.type)
        nombre_tipo = str(actividad.type)
        desc = actividad.description if actividad.description else ""
        
        mensaje = f"{emoji} {nombre_tipo}\n📝 {actividad.name}\n\n{desc}"

        # Recorte: Mastodon solo permite 500 caracteres y yo a veces pongo mucha cosa :)
        if len(mensaje) > 495:
            mensaje = mensaje[:490] + "..."

        try:
            mastodon.status_post(mensaje)
            print("Subido a Mastodon")
            nuevas_subidas.append(actividad.id)
            time.sleep(10)
        except Exception as e:
            print("Error subiendo: " + str(e))

    # Guardar
    f = open(ARCHIVO, 'w')
    json.dump(nuevas_subidas[-100:], f)
    f.close()

if __name__ == "__main__":
    print("Bot arrancado.")
    while True:
        iniciar_bot()
        time.sleep(900)