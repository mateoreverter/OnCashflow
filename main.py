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

SCRAPER_API_KEY = "487ee67cecc56b1c7913c493219c6413"

@app.get("/")
def home():
    return {"status": "API activa en Render con ScraperAPI"}

@app.get("/api/precios")
def obtener_precios_byma():
    try:
        url_ons = "https://open.bymadata.com.ar/vanoms-be-core/rest/api/bymadata/free/corporate-bonds"
        url_pub = "https://open.bymadata.com.ar/vanoms-be-core/rest/api/bymadata/free/public-bonds"
        
        # Agregamos keep_headers=true para que ScraperAPI le pase el "disfraz" a BYMA
        proxy_ons = f"http://api.scraperapi.com?api_key={SCRAPER_API_KEY}&url={url_ons}&keep_headers=true"
        proxy_pub = f"http://api.scraperapi.com?api_key={SCRAPER_API_KEY}&url={url_pub}&keep_headers=true"

        # Disfraz básico para BYMA
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        }

        payload = {
            "excludeZeroPxAndQty": False,
            "T1": False,
            "T0": True,
            "T2": False
        }
        
        datos_totales = []
        
        # Subimos el límite de paciencia a 60 segundos
        res_ons = requests.post(proxy_ons, headers=headers, json=payload, timeout=60)
        if res_ons.status_code == 200:
            datos_totales.extend(res_ons.json())
            
        res_pub = requests.post(proxy_pub, headers=headers, json=payload, timeout=60)
        if res_pub.status_code == 200:
            datos_totales.extend(res_pub.json())

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
            return {"status": "error", "message": f"Respuesta vacía. HTTP Status: {res_ons.status_code}"}

    except Exception as e:
        return {"status": "error", "message": str(e)}
