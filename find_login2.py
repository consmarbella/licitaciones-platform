"""Find login modal on Mercado Publico"""
import time
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

USER = "138290123"
PASS = "Ale2401-"

with sync_playwright() as pw:
    browser = pw.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto("https://www.mercadopublico.cl/Home", wait_until="networkidle")
    page.wait_for_timeout(2000)

    # Take screenshot to see layout
    page.screenshot(path="mercadopublico.png", full_page=False)
    
    # Click "Iniciar Sesion" button
    btn = page.get_by_text("Iniciar Sesion")
    if btn:
        print("[OK] Iniciar Sesion button found")
        btn.click()
        page.wait_for_timeout(3000)
        print("After click URL:", page.url)

        # Check for modal / login form
        html = page.content()
        soup = BeautifulSoup(html, "lxml")
        
        # Look for inputs that appeared
        inputs = soup.find_all("input")
        for inp in inputs:
            name = inp.get("name", "")
            type_ = inp.get("type", "")
            if name and type_ not in ("hidden",):
                print(f"  Input: name={name}, type={type_}, placeholder={inp.get('placeholder','')}")
        
        # Look for iframes
        iframes = soup.find_all("iframe")
        print(f"Iframes: {len(iframes)}")
        for ifr in iframes[:3]:
            print(f"  src={ifr.get('src','')[:100]}")
        
        # Check if there's a modal
        modals = soup.select('[class*="modal"], [class*="popup"], [id*="modal"], [id*="login"]')
        print(f"Modals/popups: {len(modals)}")

        # Try to fill login if fields are now visible
        try:
            page.wait_for_selector('input[name="username"]', timeout=3000)
            page.fill('input[name="username"]', USER)
            page.fill('input[name="password"]', PASS)
            page.get_by_text("Ingresar").click()
            page.wait_for_timeout(3000)
            print("After login URL:", page.url)
        except:
            print("[!] No login fields appeared after clicking button")
    else:
        print("[!] Iniciar Sesion button not found")

    browser.close()
