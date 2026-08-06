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

# Tu API Key de ScraperAPI integrada
SCRAPER_API_KEY = "487ee67cecc56b1c7913c493219c6413"

@app.get("/")
def home():
    return {"status": "API activa en Render con ScraperAPI"}

@app.get("/api/precios")
def obtener_precios_byma():
    try:
        url_ons = "https://open.bymadata.com.ar/vanoms-be-core/rest/api/bymadata/free/corporate-bonds"
        url_pub = "https://open.bymadata.com.ar/vanoms-be-core/rest/api/bymadata/free/public-bonds"
        
        # Petición a través del Proxy Residencial de ScraperAPI
        proxy_ons = f"http://api.scraperapi.com?api_key={SCRAPER_API_KEY}&url={url_ons}"
        proxy_pub = f"http://api.scraperapi.com?api_key={SCRAPER_API_KEY}&url={url_pub}"

        payload = {
            "excludeZeroPxAndQty": False,
            "T1": False,
            "T0": True,
            "T2": False
        }
        
        datos_totales = []
        
        # Petición 1: Obligaciones Negociables
        res_ons = requests.post(proxy_ons, json=payload, timeout=30)
        if res_ons.status_code == 200:
            datos_totales.extend(res_ons.json())
            
        # Petición 2: Bonos Públicos
        res_pub = requests.post(proxy_pub, json=payload, timeout=30)
        if res_pub.status_code == 200:
            datos_totales.extend(res_pub.json())

        # Mapeo y formateo de datos para el frontend
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
