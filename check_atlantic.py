#!/usr/bin/env python3
from playwright.sync_api import sync_playwright
import re

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, executable_path='/snap/bin/chromium')
    context = browser.new_context(
        user_agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    )
    page = context.new_page()

    # Check Atlantic Teacher Careers website directly
    try:
        page.goto('https://atlanticteachercareers.com', timeout=10000)
        page.wait_for_load_state('domcontentloaded', timeout=8000)
        print("ATLANTICTEACHERS PAGE TITLE:", page.title())
        content = page.content()
        emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', content)
        for e in set(emails):
            print("EMAIL:", e)
        links = page.query_selector_all('a')
        for link in links:
            href = link.get_attribute('href') or ''
            text = link.inner_text().lower()
            if any(kw in text for kw in ['career', 'apply', 'job', 'vacancy', 'contact', 'email']):
                print(f"LINK TEXT: {link.inner_text()[:80]} -> {href}")
    except Exception as e:
        print(f"Error: {e}")

    try:
        page.goto('https://atlanticteachercareers.com/apply', timeout=8000)
        print("Apply page title:", page.title())
        emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', page.content())
        for e in set(emails):
            print("EMAIL from apply:", e)
    except Exception as e:
        print(f"Apply page error: {e}")

    browser.close()
