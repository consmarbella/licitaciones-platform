import requests
import json

print("Probando API ChileCompra...")

headers = {'User-Agent': 'Mozilla/5.0', 'Accept': 'application/json'}

# API publica
urls = [
    "https://api.mercadopublico.cl/servicios/v2/publico/licitaciones.json?estado=Publicada&tamano=3",
    "https://api.mercadopublico.cl/servicios/v1/publico/licitaciones.json?pagina=1&tamano=3",
]

for url in urls:
    try:
        r = requests.get(url, headers=headers, timeout=15)
        print(f"\nURL: {url}")
        print(f"Status: {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            count = len(data.get('Listado', data.get('listado', [])))
            print(f"Items: {count}")
            items = data.get('Listado', data.get('listado', []))
            for item in items[:3]:
                codigo = item.get('Codigo', item.get('codigo', '?'))
                nombre = item.get('Nombre', item.get('nombre', '?'))
                print(f"  - {codigo}: {nombre[:60]}")
        else:
            print(f"Respuesta: {r.text[:200]}")
    except Exception as e:
        print(f"Error: {e}")

# Probar scraping del sitio web
print("\n\nProbando acceso a mercadopublico.cl...")
try:
    r = requests.get("https://www.mercadopublico.cl/", headers=headers, timeout=15)
    print(f"Status: {r.status_code}")
    print(f"Size: {len(r.content)} bytes")
    if "mercadopublico" in r.text.lower():
        print("Sitio accesible!")
except Exception as e:
    print(f"Error: {e}")
