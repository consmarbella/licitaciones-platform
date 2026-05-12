"""Test login on Mercado Publico"""
import time
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

USER = "138290123"
PASS = "Ale2401-"

with sync_playwright() as pw:
    browser = pw.chromium.launch(headless=True)
    page = browser.new_page()

    page.goto("https://www.mercadopublico.cl/Home")
    page.wait_for_timeout(3000)
    print("Title:", page.title()[:100])
    print("URL:", page.url)

    # Look for login form
    username_input = page.query_selector('input[name="username"]')
    if username_input:
        print("[OK] Login form found")
        username_input.fill(USER)
        page.fill('input[name="password"]', PASS)

        # Try clicking login button
        login_btn = page.query_selector('button[type="submit"]')
        if login_btn:
            login_btn.click()
        else:
            page.keyboard.press("Enter")
        
        page.wait_for_timeout(4000)
        print("After login URL:", page.url)
    else:
        print("[!] No login form found")

    # Try Compra Agil
    page.goto("https://www.mercadopublico.cl/Home/Search")
    page.wait_for_timeout(3000)
    print("Search URL:", page.url)
    
    content = page.content()
    print("Content size:", len(content), "bytes")

    soup = BeautifulSoup(content, "lxml")
    links = soup.find_all("a", href=True)
    licitacion_links = [l for l in links if "licitacion" in l["href"].lower() or "licitacion" in l.text.lower()]
    print("Licitacion links found:", len(licitacion_links))
    for link in licitacion_links[:5]:
        print(" -", link.text.strip()[:100], "->", link["href"][:80])

    browser.close()
