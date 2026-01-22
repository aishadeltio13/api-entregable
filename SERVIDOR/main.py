import os, json, time, secrets
from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel

# 1. Iniciar API
app = FastAPI(title="Aisha Strava API - Paso 1")
security = HTTPBasic()

DB_PATH = "/data/drafts.json"

# 2. Definimos el MODELO 
class Draft(BaseModel):
    id: Optional[int] = None
    title: str
    content: str
    status: str = "draft"

# 3. Endpoint de prueba para ver que todo funciona
@app.get("/")
def read_root():
    return {"mensaje": "Servidor de Aisha funcionando"}
