#!/usr/bin/env python3
"""Attempt to access LinkedIn job page and find Easy Apply or external apply link."""
from playwright.sync_api import sync_playwright
import re

# IELTS role LinkedIn URL
IELTS_JOB_URL = "https://www.linkedin.com/jobs/view/4399236048"
# Secondary role LinkedIn URL
SEC_JOB_URL = "https://www.linkedin.com/jobs/view/4399222766"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, executable_path='/snap/bin/chromium')
    context = browser.new_context(
        user_agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        viewport={'width': 1280, 'height': 800}
    )
    page = context.new_page()
    
    # Try IELTS job
    print("=== IELTS Job Page ===")
    try:
        page.goto(IELTS_JOB_URL, timeout=15000)
        page.wait_for_load_state('domcontentloaded', timeout=12000)
        print("Page title:", page.title())
        content = page.content()
        
        # Look for Easy Apply button
        easy_apply = page.query_selector('[data-job-id] button[aria-label*="Easy Apply"]')
        if easy_apply:
            print("Found EASY APPLY button!")
        else:
            print("No Easy Apply button found")
        
        # Look for any Apply button text
        apply_buttons = page.query_selector_all('button')
        for btn in apply_buttons:
            text = btn.inner_text().lower()
            if 'apply' in text:
                aria = btn.get_attribute('aria-label') or ''
                print(f"Apply button: '{btn.inner_text()}' aria-label='{aria}'")
        
        # Check for external application URL in description
        urls = re.findall(r'https?://[^\s<>"\'\\s]+', content)
        for url in urls[:20]:
            print(f"URL: {url}")
            
        # Look for company website or direct application instructions
        if 'atlantic' in content.lower():
            atlantic_section = content[content.lower().find('atlantic'):content.lower().find('atlantic')+500]
            print("Atlantic section:", atlantic_section[:300])
            
    except Exception as e:
        print(f"Error: {e}")
    
    browser.close()
