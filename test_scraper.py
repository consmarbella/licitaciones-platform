"""Test the new ChileCompra API scraper"""
from backend.scraper import fetch_licitaciones, get_categorias

print("Probando API ChileCompra con ticket...")
print()

# Get categories first
print("Categorias de bienes:")
get_categorias()
print()

# Fetch licitaciones
resultados = fetch_licitaciones(max_results=30)
print(f"\nTotal licitaciones de bienes encontradas: {len(resultados)}")
print()

for item in resultados[:10]:
    nombre = item["nombre"][:80]
    presupuesto = item["presupuesto"]
    organismo = item["organismo"][:30] if item["organismo"] else "?"
    print(f"  [{nombre}]")
    print(f"     ${presupuesto:,.0f} | {organismo} | Cierre: {item['fecha_cierre'][:10]}")
