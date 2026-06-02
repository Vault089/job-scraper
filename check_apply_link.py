#!/usr/bin/env python3
"""Check Atlantic Teacher Careers LinkedIn company page and find application URL."""
from playwright.sync_api import sync_playwright
import re

ATLANTIC_COMPANY_URL = "https://vn.linkedin.com/company/atlantic-teacher-career"
IELTS_JOB_URL = "https://www.linkedin.com/jobs/view/4399236048"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, executable_path='/snap/bin/chromium')
    context = browser.new_context(
        user_agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        viewport={'width': 1280, 'height': 800}
    )
    page = context.new_page()
    
    # Check the company page first
    print("=== Atlantic Company Page ===")
    try:
        page.goto(ATLANTIC_COMPANY_URL, timeout=15000)
        page.wait_for_load_state('domcontentloaded', timeout=12000)
        print("Page title:", page.title())
        
        # Look for job postings / apply links on company page
        links = page.query_selector_all('a[href]')
        for link in links:
            href = link.get_attribute('href')
            text = link.inner_text()[:80] if link.inner_text() else ''
            if any(kw in (href+text).lower() for kw in ['apply', 'career', 'job', 'vacancy', 'teach']):
                print(f"LINK: {text} -> {href}")
    except Exception as e:
        print(f"Company page error: {e}")
    
    # Now go to the job page and click the Apply button
    print("\n=== Job Page Apply ===")
    page2 = context.new_page()
    try:
        page2.goto(IELTS_JOB_URL, timeout=15000)
        page2.wait_for_load_state('domcontentloaded', timeout=12000)
        
        # Try clicking the Apply button
        apply_btn = None
        buttons = page2.query_selector_all('button')
        for btn in buttons:
            text = btn.inner_text().lower().strip()
            if 'apply' in text:
                apply_btn = btn
                print(f"Found Apply button: '{btn.inner_text()}'")
                break
        
        if apply_btn:
            # Try to click and see what happens
            print("Clicking Apply button...")
            apply_btn.click()
            page2.wait_for_timeout(3000)
            
            # Check URL after click
            print("URL after click:", page2.url)
            print("Page title after click:", page2.title())
            
            # Look for form fields or redirects
            content = page2.content()
            forms = page2.query_selector_all('form')
            print(f"Forms found: {len(forms)}")
            
            # Check for external redirect
            if 'atlantic' in content.lower() or 'external' in content.lower():
                urls = re.findall(r'https?://[^\s<>"\'\\s]+', content)
                for url in urls[:10]:
                    if 'linkedin' not in url:
                        print(f"Non-LinkedIn URL: {url}")
                        
    except Exception as e:
        print(f"Job page error: {e}")
    
    browser.close()
