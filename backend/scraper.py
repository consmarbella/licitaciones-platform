"""ChileCompra API Scraper - Dropshipping al Estado"""
import requests
import time

API_TICKET = "56BB22C0-F3CC-4F2A-B992-84ACDD42A0A1"
API_BASE = "https://api.mercadopublico.cl/servicios/v1/publico"

def fetch_licitaciones(keywords="adquisicion compra suministro", estado="Publicada", max_results=50):
    """Busca licitaciones por keywords. Solo bienes, no servicios."""
    resultados = []
    headers = {"User-Agent": "Mozilla/5.0", "Accept": "application/json"}
    tamano = min(50, max_results + 20)

    url = f"{API_BASE}/licitaciones?ticket={API_TICKET}&tamano={tamano}&estado={estado}"
    
    try:
        r = requests.get(url, headers=headers, timeout=30)
        if r.status_code == 200:
            data = r.json()
            items = data.get("Listado", [])
            
            for item in items:
                nombre = (item.get("Nombre", "") or "").lower()
                obj = (item.get("Objeto", "") or "").lower()
                texto = nombre + " " + obj
                
                # Solo si contiene las keywords de compra
                kw_list = [k.strip().lower() for k in keywords.split()]
                if any(kw in texto for kw in kw_list):
                    resultados.append({
                        "id": str(item.get("CodigoExterno", "")),
                        "numero": str(item.get("Codigo", "")),
                        "nombre": item.get("Nombre", ""),
                        "organismo": item.get("Organismo", ""),
                        "estado": item.get("Estado", ""),
                        "fecha_cierre": item.get("FechaCierre", ""),
                        "link": f"https://www.mercadopublico.cl/Procurement/Modules/RFP/PlanPurchasing/DetailPlanPurchasing.aspx?CodigoLicitacion={item.get('Codigo', '')}",
                    })
        else:
            print(f"API Error: HTTP {r.status_code}")
    except Exception as e:
        print(f"Error: {e}")

    return resultados[:max_results]

def get_detalle(codigo):
    """Obtiene detalle completo de una licitacion (presupuesto, items, adjuntos)"""
    url = f"{API_BASE}/licitacion?ticket={API_TICKET}&codigo={codigo}"
    try:
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=20)
        if r.status_code == 200:
            return r.json()
    except:
        pass
    return None

def search_por_query(query, max_results=20):
    """Busqueda directa por texto"""
    url = f"{API_BASE}/licitaciones?ticket={API_TICKET}&tamano={max_results}&estado=Publicada&texto={query}"
    try:
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=20)
        if r.status_code == 200:
            return r.json().get("Listado", [])
    except:
        pass
    return []

if __name__ == "__main__":
    r = fetch_licitaciones(max_results=10)
    print(f"Licitaciones encontradas: {len(r)}")
    for item in r:
        print(f"  - {item['nombre'][:70]}")
