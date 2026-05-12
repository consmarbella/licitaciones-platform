"""Test login in Mercado Publico via Playwright"""
import time
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

USERNAME = "138290123"
PASSWORD = "Ale2401-"

with sync_playwright() as pw:
    browser = pw.chromium.launch(headless=True)
    page = browser.new_page()

    page.goto("https://www.mercadopublico.cl/Login/Login")
    time.sleep(2)
    print(f"Title: {page.title()}")

    page.fill('input[name="username"]', USERNAME)
    page.fill('input[name="password"]', PASSWORD)
    page.click('button[type="submit"]')
    time.sleep(3)

    print(f"After login URL: {page.url}")
    print(f"After login Title: {page.title()}")

    page.goto("https://www.mercadopublico.cl/Home/Search?status=Publicada&category=Bienes")
    time.sleep(3)
    print(f"Search URL: {page.url}")

    content = page.content()
    print(f"Content size: {len(content)} bytes")

    soup = BeautifulSoup(content, "lxml")
    items = soup.select('[class*="licitacion"], [class*="resultado"], [class*="item"], table tr')
    print(f"Items encontrados: {len(items)}")

    for item in items[:5]:
        text = item.get_text(strip=True)[:300]
        if len(text) > 30:
            print(f"  - {text[:200]}")

    browser.close()
