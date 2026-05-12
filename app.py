"""
Licitaciones Platform - Web Dashboard
Interfaz para revisar licitaciones, ver análisis de precios y decidir
"""

import os
import sys
sys.path.append(os.path.dirname(__file__))

from flask import Flask, render_template, request, jsonify, redirect, url_for
from backend.database import (
    get_all_licitaciones, get_licitacion, get_productos,
    save_licitacion, update_decision
)
from backend.scraper import fetch_licitaciones, get_detalle
from backend.price_comparator import PriceComparator

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Cargar credenciales
USERNAME = os.environ.get('MERCADO_PUBLICO_USERNAME') or '138290123'
PASSWORD = os.environ.get('MERCADO_PUBLICO_PASSWORD') or 'Ale2401-'

scraper = {"username": USERNAME, "password": PASSWORD}
comparator = PriceComparator()


@app.route('/')
def index():
    licitaciones = get_all_licitaciones()
    return render_template('index.html', licitaciones=licitaciones)


@app.route('/licitacion/<licitacion_id>')
def licitacion_detail(licitacion_id):
    data = get_licitacion(licitacion_id)
    productos = get_productos(licitacion_id)
    return render_template('detail.html', licitacion=data, productos=productos)


@app.route('/buscar', methods=['GET', 'POST'])
def buscar():
    resultados = []
    if request.method == 'POST':
        query = request.form.get('query', '')
        max_results = int(request.form.get('max_results', 30))
        
        print(f"🔍 Buscando licitaciones: {query}")
        resultados = scraper.buscar_por_api(max_results=max_results)
        
        # Guardar en BD
        for r in resultados:
            save_licitacion(r)
        
        print(f"✅ {len(resultados)} licitaciones guardadas")
    
    return render_template('buscar.html', resultados=resultados)


@app.route('/analizar/<licitacion_id>', methods=['POST'])
def analizar(licitacion_id):
    data = get_licitacion(licitacion_id)
    if not data:
        return jsonify({'error': 'No encontrada'}), 404
    
    # Extraer posibles productos del nombre/descripción
    nombre = data[3] if len(data) > 3 else ''
    descripcion = data[4] if len(data) > 4 else ''
    presupuesto = float(data[11] or 0) if len(data) > 11 else 0
    
    # Buscar precios
    productos = []
    texto = f"{nombre} {descripcion}"
    
    # Extraer items (simplificado - mejorable con NLP)
    lines = texto.split('\n')
    for line in lines[:3]:
        if len(line) > 10:
            precios = comparator.search_product(line, max_results=3)
            
            if precios:
                mejor = precios[0]
                ganancia = comparator.calculate_profit(presupuesto, mejor['precio'])
                
                from backend.database import save_producto
                save_producto(licitacion_id, {
                    'nombre': line[:100],
                    'cantidad': 1,
                    'unidad': 'unidad',
                    'precio_unitario_estimado': presupuesto,
                    'precio_google': mejor['precio'],
                    'tienda': mejor['tienda'],
                    'url_producto': mejor['url'],
                    'imagen_url': mejor.get('imagen_url', ''),
                })
                
                productos.append({
                    'nombre': line[:100],
                    'mejor_precio': mejor['precio'],
                    'tienda': mejor['tienda'],
                    'ganancia': ganancia,
                    'imagen': mejor.get('imagen_url', ''),
                })
    
    return jsonify({'productos': productos})


@app.route('/decision/<licitacion_id>', methods=['POST'])
def tomar_decision(licitacion_id):
    decision = request.form.get('decision', 'pendiente')
    notas = request.form.get('notas', '')
    update_decision(licitacion_id, decision, notas)
    return redirect(url_for('index'))


@app.route('/configurar-clave', methods=['POST'])
def configurar_clave():
    """Guarda credenciales para adjuntos protegidos"""
    clave = request.form.get('clave', '')
    scraper.password = clave
    return jsonify({'ok': True})


if __name__ == '__main__':
    # Crear carpeta downloads si no existe
    os.makedirs('downloads', exist_ok=True)
    os.makedirs('templates', exist_ok=True)
    
    print("[START] Licitaciones Platform iniciando...")
    print("   http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
