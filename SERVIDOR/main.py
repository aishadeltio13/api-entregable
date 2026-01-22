# http://localhost:8001/docs

import os, json, time, secrets
from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel

# 1. Iniciar API
app = FastAPI(title="Aisha Strava API - Paso 1")
security = HTTPBasic()

DB_PATH = "/data/drafts.json"

# 2. Modelo
class Draft(BaseModel):
    id: Optional[int] = None
    title: str
    content: str
    status: str = "draft"
    
# 3. Funciones base de datos
def load_db():
    if not os.path.exists(DB_PATH):
        return []
    try:
        with open(DB_PATH, "r") as f:
            return json.load(f)
    except:
        # Si el archivo vacío, devolvemos lista vacía
        return []

def save_db(data):
    # Creamos la carpeta /data si no existiera 
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    with open(DB_PATH, "w") as f:
        json.dump(data, f, indent=4)

# 4. Endpoint
@app.get("/")
def read_root():
    return {"mensaje": "Servidor de Aisha funcionando"}

@app.get("/drafts", response_model=List[Draft])
def list_drafts(skip: int = 0, limit: int = 10):
    data = load_db()
    return data[skip : skip + limit] # esto es para la paginacion (ahora tenemos pocos entrenamientos, pero en un futuro tendremos muchos y será necesario)

@app.post("/drafts", status_code=201)
def create_draft(draft: Draft):
    data = load_db()
    draft.id = int(time.time())
    data.append(draft.dict())
    save_db(data)
    return draft

@app.put("/drafts/{draft_id}", response_model=Draft)
def update_draft(draft_id: int, updated_content: Draft):
    data = load_db()
    for i, d in enumerate(data):
        if d["id"] == draft_id:
            # Truco: se mantiene el id original pero se cambia lo que hayamos cambiado
            updated_content.id = draft_id
            data[i] = updated_content.dict()
            save_db(data)
            return updated_content
    
    # Si no encontramos el id (error 404)
    raise HTTPException(status_code=404, detail="Borrador no encontrado")


@app.delete("/drafts/{draft_id}")
def delete_draft(draft_id: int):
    data = load_db()
    # Nueva lista sin el elemento que queremos borrar
    nueva_lista = [d for d in data if d["id"] != draft_id]
    # Si la lista mide lo mismo, es que no hemos borrado nada y no se encontró el id
    if len(nueva_lista) == len(data):
        raise HTTPException(status_code=404, detail="No se pudo eliminar: ID no encontrado")
    save_db(nueva_lista)
    return {"mensaje": f"Borrador {draft_id} eliminado correctamente"}