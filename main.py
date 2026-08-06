from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import cloudscraper

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
        
        # Creamos el scraper diseñado para saltar la seguridad de Cloudflare
        scraper = cloudscraper.create_scraper(browser={'browser': 'chrome', 'platform': 'windows', 'mobile': False})
        
        payload = {
            "excludeZeroPxAndQty": False,
            "T1": False,
            "T0": True,
            "T2": False
        }
        
        datos_totales = []
        
        # Pedimos los datos usando el scraper en lugar de la librería tradicional
        res_ons = scraper.post(url_ons, json=payload, timeout=15)
        if res_ons.status_code == 200:
            datos_totales.extend(res_ons.json())
            
        res_pub = scraper.post(url_pub, json=payload, timeout=15)
        if res_pub.status_code == 200:
            datos_totales.extend(res_pub.json())

        # Filtramos y limpiamos
        resultados_procesados = []
        for item in datos_totales:
            resultados_procesados.append({
                "ticker": item.get("symbol", ""),
                "price": item.get("closingPrice", item.get("trade", 0)),
                "ytm": item.get("yield", 0),
                "parity": item.get("imputedParity", 0)
            })

        # Si tenemos datos, los devolvemos. Si BYMA nos sigue rebotando, ahora sí mostramos el código de error real.
        if len(resultados_procesados) > 0:
            return {"status": "ok", "datos": resultados_procesados}
        else:
            return {"status": "error", "message": f"Bloqueo de BYMA: HTTP {res_ons.status_code}"}

    except Exception as e:
        return {"status": "error", "message": str(e)}
