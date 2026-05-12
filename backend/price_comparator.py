"""
Buscador de precios: Google Shopping + retailers chilenos
Compara precios y calcula ganancia potencial
"""

import re
import time
import urllib.parse
from playwright.sync_api import sync_playwright

# Retailers chilenos a buscar
RETAILERS = [
    'mercadolibre.cl',
    'sodimac.cl',
    'paris.cl', 
    'falabella.com',
    'ripley.com',
    'lider.cl',
    'jumbo.cl',
    'easy.cl',
    'la-polar.cl',
    'abcdin.cl',
    'hites.com',
]


class PriceComparator:
    def __init__(self):
        self.browser = None
        self.page = None

    def search_product(self, product_name, max_results=5):
        """
        Busca un producto en Google Shopping y retailers chilenos
        Retorna lista de {tienda, precio, url, imagen}
        """
        resultados = []
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            # 1. Buscar en Google Shopping
            resultados += self._search_google_shopping(page, product_name)
            
            # 2. Buscar en retailers chilenos
            resultados += self._search_retailers(page, product_name)
            
            browser.close()
        
        # Ordenar por precio
        resultados.sort(key=lambda x: x.get('precio', float('inf')))
        
        return resultados[:max_results]

    def _search_google_shopping(self, page, product_name):
        """Buscar en Google Shopping"""
        resultados = []
        try:
            query = urllib.parse.quote(f"{product_name} Chile")
            page.goto(f"https://www.google.com/search?q={query}&tbm=shop")
            time.sleep(2)
            
            items = page.query_selector_all('.sh-dgr__content, .sh-pr__product-results div[role="listitem"]')
            
            for item in items[:8]:
                try:
                    title_el = item.query_selector('h4, .tAxDx, .sh-t__title')
                    price_el = item.query_selector('.a8Pemb, .OiTJZd, .sh-pr__price')
                    link_el = item.query_selector('a')
                    img_el = item.query_selector('img')
                    
                    title = title_el.inner_text() if title_el else ''
                    price_text = price_el.inner_text() if price_el else ''
                    url = link_el.get_attribute('href') if link_el else ''
                    img = img_el.get_attribute('src') if img_el else ''
                    
                    precio = self._parse_price(price_text)
                    tienda = self._detect_store(url)
                    
                    if precio > 0:
                        resultados.append({
                            'tienda': tienda or 'Google Shopping',
                            'precio': precio,
                            'url': url,
                            'imagen_url': img if img and img.startswith('http') else '',
                        })
                except:
                    continue
                    
        except Exception as e:
            print(f"  Error Google Shopping: {e}")
        
        return resultados

    def _search_retailers(self, page, product_name):
        """Buscar directamente en retailers chilenos"""
        resultados = []
        query = urllib.parse.quote(product_name)
        
        for retailer in RETAILERS:
            try:
                url = f"https://www.{retailer}/search?q={query}"
                page.goto(url)
                time.sleep(2)
                
                # Extraer precio del primer resultado
                price_el = page.query_selector('.product-card__price, .prices-price, .price, [class*="precio"]')
                title_el = page.query_selector('.product-card__title, .product-name, h2, [class*="title"]')
                img_el = page.query_selector('.product-card__image img, .product-image img, img[class*="product"]')
                
                if price_el and title_el:
                    price_text = price_el.inner_text()
                    title = title_el.inner_text()
                    precio = self._parse_price(price_text)
                    img = img_el.get_attribute('src') if img_el else ''
                    
                    if precio > 0:
                        resultados.append({
                            'tienda': retailer.replace('.cl', '').replace('.com', '').capitalize(),
                            'precio': precio,
                            'url': page.url,
                            'imagen_url': img if img and img.startswith('http') else '',
                        })
            except:
                continue
        
        return resultados

    def calculate_profit(self, presupuesto_licitacion, mejor_precio, margen=0.15):
        """
        Calcula ganancia potencial
        presupuesto_licitacion: lo que paga el estado
        mejor_precio: lo que cuesta el producto en el mercado
        margen: margen de ganancia deseado (default 15%)
        """
        if not presupuesto_licitacion or not mejor_precio:
            return 0
        
        costo_total = mejor_precio * 1.19  # +19% IVA
        ganancia = presupuesto_licitacion - costo_total
        margen_real = ganancia / presupuesto_licitacion if presupuesto_licitacion > 0 else 0
        
        return {
            'presupuesto_estado': presupuesto_licitacion,
            'costo_producto': mejor_precio,
            'costo_con_iva': costo_total,
            'ganancia_estimada': ganancia,
            'margen_real': round(margen_real * 100, 1),
            'es_rentable': margen_real >= margen,
        }

    def search_product_image(self, product_name):
        """Obtiene URL de imagen del producto"""
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            try:
                query = urllib.parse.quote(product_name)
                page.goto(f"https://www.google.com/search?q={query}&tbm=isch")
                time.sleep(2)
                
                img = page.query_selector('img.rg_i, img[class*="image"]')
                if img:
                    src = img.get_attribute('src')
                    if src and src.startswith('http'):
                        return src
            except:
                pass
            finally:
                browser.close()
        
        return ''

    def _parse_price(self, text):
        """Extrae número de un texto de precio"""
        if not text:
            return 0
        nums = re.findall(r'[\d.]+', text.replace('$', '').replace('.', ''))
        return float(nums[0]) if nums else 0

    def _detect_store(self, url):
        """Detecta la tienda desde la URL"""
        if not url:
            return ''
        for store in ['mercadolibre', 'sodimac', 'paris', 'falabella', 
                      'ripley', 'lider', 'jumbo', 'easy', 'la-polar', 
                      'abcdin', 'hites']:
            if store in url.lower():
                return store.capitalize().replace('-', ' ')
        return ''


if __name__ == '__main__':
    pc = PriceComparator()
    resultados = pc.search_product('Notebook Lenovo 8GB RAM 256GB SSD')
    print("Resultados de búsqueda:")
    for r in resultados:
        print(f"  {r.get('tienda', '?'):20s} ${r.get('precio', 0):>10,.0f}")
