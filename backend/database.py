import sqlite3
import json
from datetime import datetime

DB_PATH = 'licitaciones.db'

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS licitaciones (
            id TEXT PRIMARY KEY,
            numero TEXT,
            nombre TEXT,
            descripcion TEXT,
            organismo TEXT,
            categoria TEXT,
            estado TEXT,
            fecha_publicacion TEXT,
            fecha_cierre TEXT,
            moneda TEXT,
            presupuesto REAL,
            link TEXT,
            json_raw TEXT,
            fecha_analisis TEXT,
            ganancia_estimada REAL,
            precio_referencia REAL,
            mejor_precio REAL,
            decision TEXT,
            notas TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS adjuntos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            licitacion_id TEXT,
            filename TEXT,
            url TEXT,
            descargado INTEGER DEFAULT 0,
            requiere_clave INTEGER DEFAULT 0,
            FOREIGN KEY (licitacion_id) REFERENCES licitaciones(id)
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            licitacion_id TEXT,
            nombre TEXT,
            cantidad INTEGER,
            unidad TEXT,
            precio_unitario_estimado REAL,
            precio_google REAL,
            tienda TEXT,
            url_producto TEXT,
            imagen_url TEXT,
            FOREIGN KEY (licitacion_id) REFERENCES licitaciones(id)
        )
    ''')
    conn.commit()
    conn.close()

def save_licitacion(data):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        INSERT OR REPLACE INTO licitaciones 
        (id, numero, nombre, descripcion, organismo, categoria, estado, 
         fecha_publicacion, fecha_cierre, moneda, presupuesto, link, json_raw, fecha_analisis)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    ''', (
        data.get('id'), data.get('numero'), data.get('nombre'), 
        data.get('descripcion'), data.get('organismo'), data.get('categoria'),
        data.get('estado'), data.get('fecha_publicacion'), data.get('fecha_cierre'),
        data.get('moneda'), data.get('presupuesto'), data.get('link'),
        json.dumps(data), datetime.now().isoformat()
    ))
    conn.commit()
    conn.close()

def save_producto(licitacion_id, producto):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        INSERT INTO productos (licitacion_id, nombre, cantidad, unidad, 
                               precio_unitario_estimado, precio_google, tienda, url_producto, imagen_url)
        VALUES (?,?,?,?,?,?,?,?,?)
    ''', (
        licitacion_id, producto.get('nombre'), producto.get('cantidad'),
        producto.get('unidad'), producto.get('precio_unitario_estimado'),
        producto.get('precio_google'), producto.get('tienda'),
        producto.get('url_producto'), producto.get('imagen_url')
    ))
    conn.commit()
    conn.close()

def get_all_licitaciones():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT * FROM licitaciones ORDER BY fecha_publicacion DESC')
    rows = c.fetchall()
    conn.close()
    return rows

def get_licitacion(licitacion_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT * FROM licitaciones WHERE id = ?', (licitacion_id,))
    row = c.fetchone()
    conn.close()
    return row

def get_productos(licitacion_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT * FROM productos WHERE licitacion_id = ?', (licitacion_id,))
    rows = c.fetchall()
    conn.close()
    return rows

def update_decision(licitacion_id, decision, notas=''):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('UPDATE licitaciones SET decision = ?, notas = ? WHERE id = ?',
              (decision, notas, licitacion_id))
    conn.commit()
    conn.close()

init_db()
print("[OK] Base de datos inicializada")
