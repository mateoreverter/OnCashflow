from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"status": "API activa en Render"}

@app.get("/api/precios")
def obtener_precios_byma():
    try:
        url_ons = "https://open.bymadata.com.ar/vanoms-be-core/rest/api/bymadata/free/corporate-bonds"
        url_pub = "https://open.bymadata.com.ar/vanoms-be-core/rest/api/bymadata/free/public-bonds"
        
        # Disfrazamos la conexión para saltar la seguridad de BYMA
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "es-AR,es;q=0.9,en-US;q=0.8",
            "Content-Type": "application/json",
            "Origin": "https://open.bymadata.com.ar",
            "Referer": "https://open.bymadata.com.ar/"
        }
        
        # Pedimos liquidación T0 (Contado Inmediato)
        payload = {
            "excludeZeroPxAndQty": False,
            "T1": False,
            "T0": True,
            "T2": False
        }
        
        datos_totales = []
        
        # Buscamos ONs
        res_ons = requests.post(url_ons, headers=headers, json=payload, timeout=15)
        if res_ons.status_code == 200:
            datos_totales.extend(res_ons.json())
            
        # Buscamos Bonos Públicos
        res_pub = requests.post(url_pub, headers=headers, json=payload, timeout=15)
        if res_pub.status_code == 200:
            datos_totales.extend(res_pub.json())

        # Filtramos solo lo que el HTML necesita
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
            return {"status": "error", "message": f"Error HTTP de BYMA: {res_ons.status_code}"}

    except Exception as e:
        return {"status": "error", "message": str(e)}
