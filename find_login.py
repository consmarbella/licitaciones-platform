"""Find the actual login page on Mercado Publico"""
import time
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

with sync_playwright() as pw:
    browser = pw.chromium.launch(headless=True)
    page = browser.new_page()

    # Try different login URLs
    urls = [
        "https://www.mercadopublico.cl/Home",
        "https://www.mercadopublico.cl/Account/Login",
        "https://www.mercadopublico.cl/auth/login",
        "https://www.mercadopublico.cl/Login",
        "https://logingov.chilecompra.cl",
    ]

    for url in urls:
        try:
            page.goto(url, wait_until="networkidle", timeout=15000)
            page.wait_for_timeout(2000)
            content = page.content()
            
            has_form = 'input' in content and 'password' in content
            has_input = 'username' in content or 'rut' in content or 'user' in content
            
            print(f"{url}")
            print(f"  Title: {page.title()[:80]}")
            print(f"  Size: {len(content)} bytes")
            print(f"  Has form: {has_form}, Has input: {has_input}")
            
            # Look for any input fields
            soup = BeautifulSoup(content, "lxml")
            inputs = soup.find_all("input")
            if inputs:
                print(f"  Inputs: {[i.get('name','') for i in inputs[:5]]}")
            
            buttons = soup.find_all("button")
            if buttons:
                print(f"  Buttons: {[b.text.strip()[:30] for b in buttons[:3]]}")
            print()
        except Exception as e:
            print(f"{url} -> Error: {str(e)[:60]}")
            print()

    browser.close()
