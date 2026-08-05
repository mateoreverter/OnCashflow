from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests

app = FastAPI()

# Habilitamos CORS para que Netlify pueda pedirle datos a este servidor
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
        # Endpoints reales de BYMA Data Abierta
        url_ons = "https://open.bymadata.com.ar/vanoms-be-core/rest/api/bymadata/free/corporate-bonds"
        url_pub = "https://open.bymadata.com.ar/vanoms-be-core/rest/api/bymadata/free/public-bonds"
        
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Content-Type": "application/json"
        }
        
        # BYMA requiere un método POST con este "payload" para devolver la data de Contado Inmediato (T0)
        payload = {
            "excludeZeroPxAndQty": False,
            "T1": False,
            "T0": True,
            "T2": False
        }
        
        datos_totales = []
        
        # 1. Buscamos primero las ONs (Corporate Bonds)
        res_ons = requests.post(url_ons, headers=headers, json=payload, timeout=10)
        if res_ons.status_code == 200:
            datos_totales.extend(res_ons.json())
            
        # 2. Sumamos también Bonos Públicos por si hay cruce de activos
        res_pub = requests.post(url_pub, headers=headers, json=payload, timeout=10)
        if res_pub.status_code == 200:
            datos_totales.extend(res_pub.json())

        # 3. Filtramos y limpiamos la data para que el HTML la lea perfecto
        resultados_procesados = []
        for item in datos_totales:
            resultados_procesados.append({
                "ticker": item.get("symbol", ""),
                "price": item.get("closingPrice", item.get("trade", 0)),
                "ytm": item.get("yield", 0),
                "parity": item.get("imputedParity", 0)
            })

        if len(resultados_procesados) > 0:
            return {"status": "ok", "datos": resultados_procesados}
        else:
            return {"status": "error", "message": "No se encontraron datos en BYMA."}

    except Exception as e:
        return {"status": "error", "message": str(e)}