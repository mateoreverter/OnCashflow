from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests

app = FastAPI()

# Habilitamos CORS para que Netlify pueda pedirle datos a este servidor
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Podés poner la URL exacta de tu Netlify después
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"status": "API activa de Cashflows Balanz"}

@app.get("/api/precios")
def obtener_precios_byma():
    try:
        # Ejemplo de conexión a la API/Endpoint de BYMA
        url = "https://open.byma.com.ar/api/rest/v2/isec/bonds"
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json"
        }
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            # Acá podemos filtrar o procesar solo las ONs en USD
            return {"status": "ok", "datos": data}
        else:
            return {"status": "error", "message": f"Error de BYMA: {response.status_code}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}