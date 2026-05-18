#!/usr/bin/env python3
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, executable_path='/snap/bin/chromium')
    context = browser.new_context(
        user_agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    )
    page = context.new_page()

    # Search for Atlantic Teacher Careers direct application
    page.goto('https://www.google.com/search?q=atlantic+teacher+careers+vietnam+apply', timeout=15000)
    page.wait_for_load_state('networkidle', timeout=10000)

    links = page.query_selector_all('a')
    for link in links:
        href = link.get_attribute('href') or ''
        text = link.inner_text()[:100] if link.inner_text() else ''
        if any(kw in (href + text).lower() for kw in ['atlantic', 'fivestar']):
            print(f"TEXT: {text}")
            print(f"HREF: {href}")
            print()

    browser.close()
