from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from curl_cffi import requests

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
    return {"status": "API activa en Render con ByPass de Cloudflare"}

@app.get("/api/precios")
def obtener_precios_byma():
    try:
        url_ons = "https://open.bymadata.com.ar/vanoms-be-core/rest/api/bymadata/free/corporate-bonds"
        url_pub = "https://open.bymadata.com.ar/vanoms-be-core/rest/api/bymadata/free/public-bonds"
        
        payload = {
            "excludeZeroPxAndQty": False,
            "T1": False,
            "T0": True,
            "T2": False
        }
        
        datos_totales = []
        
        # LA MAGIA: impersonate="chrome120" engaña a Cloudflare haciéndole creer que somos un navegador Chrome 100% real
        res_ons = requests.post(url_ons, json=payload, impersonate="chrome120", timeout=30)
        if res_ons.status_code == 200:
            datos_totales.extend(res_ons.json())
            
        res_pub = requests.post(url_pub, json=payload, impersonate="chrome120", timeout=30)
        if res_pub.status_code == 200:
            datos_totales.extend(res_pub.json())

        # Procesamos la información para mandarla limpita a tu HTML
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
            return {"status": "error", "message": f"Fallo al obtener datos. HTTP Status ONS: {res_ons.status_code}"}

    except Exception as e:
        return {"status": "error", "message": str(e)}
