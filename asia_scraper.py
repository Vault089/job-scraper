#!/usr/bin/env python3
"""
eChinacities Multi-Country ESL Job Scraper
Covers: Japan, South Korea, Thailand, Vietnam, Taiwan
"""
import requests
import json
import os
import re
import hashlib
import time
import random
from datetime import datetime

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
}

BASE_DIR = '/home/amrba/job_scraper'
ASIA_DIR = f'{BASE_DIR}/asia'
os.makedirs(ASIA_DIR, exist_ok=True)

DATA_FILE = f'{ASIA_DIR}/jobs_data.json'
HISTORY_FILE = f'{ASIA_DIR}/scraped_history.json'
LOG_FILE = f'{ASIA_DIR}/scraper.log'

COUNTRIES = {
    'Japan': 37,
    'South Korea': 51,
    'Thailand': 56,
    'Vietnam': 61,
    'Taiwan': 4200,
}

SEARCH_TERMS = ['english teacher', 'ESL teacher', 'TEFL teacher']

def log(msg):
    ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    line = f'[{ts}] {msg}'
    print(line)
    with open(LOG_FILE, 'a') as f:
        f.write(line + '\n')

def compute_hash(company, title, location):
    key = f'{company}|{title}|{location}'.lower()
    return hashlib.md5(key.encode()).hexdigest()

def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r') as f:
            return set(json.load(f))
    return set()

def save_history(history):
    with open(HISTORY_FILE, 'w') as f:
        json.dump(list(history), f)

def load_jobs():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return []

def save_jobs(jobs):
    with open(DATA_FILE, 'w') as f:
        json.dump(jobs, f, indent=2)

def extract_json(html):
    """Extract JSON data from eChinacities HTML page"""
    match = re.search(r'window\.__INITIAL_STATE__\s*=\s*({.*?});', html, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except:
            pass
    
    match = re.search(r'"code"\s*:\s*200\s*,\s*"data"\s*:\s*({.*?})\s*,\s*"(?:total|num)"', html, re.DOTALL)
    if match:
        try:
            return json.loads('{"code":200,"data":' + match.group(1) + '}')
        except:
            pass
    
    match = re.search(r'"list"\s*:\s*\[(.*?)\]', html, re.DOTALL)
    if match:
        try:
            return {"code": 200, "data": {"list": json.loads('[' + match.group(1) + ']')}}
        except:
            pass
    
    return None

def scrape_country(country_name, country_id):
    """Scrape jobs for a specific country"""
    log(f"Scraping {country_name} (ID: {country_id})...")
    jobs = []
    
    for term in SEARCH_TERMS:
        for page in range(1, 6):  # Max 5 pages per term
            try:
                url = f'https://jobs.echinacities.com/jobs/search?keyword={term.replace(" ", "+")}&country={country_id}&jobType=0&lastUpdate=30&page={page}'
                resp = requests.get(url, headers=HEADERS, timeout=20)
                
                if resp.status_code != 200:
                    log(f"  HTTP {resp.status_code} for page {page}")
                    break
                
                data = extract_json(resp.text)
                if not data or data.get('code') != 200:
                    break
                
                job_list = data.get('data', {}).get('list', [])
                if not job_list:
                    break
                
                if page == 1:
                    total = data.get('data', {}).get('num', 0)
                    log(f"  '{term}': {total} total jobs")
                
                log(f"    Page {page}: {len(job_list)} jobs")
                
                for job in job_list:
                    title = job.get('title', '').strip()
                    company = job.get('company_name', 'Unknown School').strip()
                    city = job.get('city', '').strip()
                    salary = job.get('salaryRmb', job.get('salary', ''))
                    description = job.get('description', '')
                    
                    if not title or len(title) < 5:
                        continue
                    
                    # Parse salary
                    salary_min = None
                    salary_max = None
                    salary_currency = 'USD'
                    
                    if salary:
                        if 'CNY' in salary or 'RMB' in salary:
                            salary_currency = 'CNY'
                        elif 'USD' in salary or '$' in salary:
                            salary_currency = 'USD'
                        
                        numbers = re.findall(r'[\d,]+', salary.replace(',', ''))
                        if len(numbers) >= 2:
                            salary_min = int(numbers[0])
                            salary_max = int(numbers[1])
                        elif len(numbers) == 1:
                            salary_min = int(numbers[0])
                            salary_max = salary_min
                    
                    jobs.append({
                        'title': title,
                        'company': company,
                        'country': country_name,
                        'city': city if city else None,
                        'job_type': 'full_time',
                        'subject': 'english',
                        'salary_min': salary_min,
                        'salary_max': salary_max,
                        'salary_currency': salary_currency,
                        'description': f"ESL teaching position in {city}, {country_name}. {description[:500] if description else title}",
                        'source': f'echinacities-{country_name.lower().replace(" ", "-")}',
                        'url': f"https://jobs.echinacities.com/jobs/detail?id={job.get('id', '')}",
                    })
                
                time.sleep(random.uniform(1, 2))
            except Exception as e:
                log(f"  Error: {e}")
                break
    
    log(f"  Found {len(jobs)} jobs")
    return jobs

def main():
    log(f"=== eChinacities Multi-Country Scraper === {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
    
    history = load_history()
    existing_jobs = load_jobs()
    all_new_jobs = []
    
    for country_name, country_id in COUNTRIES.items():
        try:
            new_jobs = scrape_country(country_name, country_id)
            for job in new_jobs:
                job_hash = compute_hash(job['company'], job['title'], job.get('city', ''))
                if job_hash not in history:
                    all_new_jobs.append(job)
                    history.add(job_hash)
        except Exception as e:
            log(f"  Error scraping {country_name}: {e}")
        time.sleep(random.uniform(2, 5))
    
    existing_jobs.extend(all_new_jobs)
    save_jobs(existing_jobs)
    save_history(history)
    
    log(f"\n=== Summary ===")
    log(f"New jobs found: {len(all_new_jobs)}")
    log(f"Total jobs in file: {len(existing_jobs)}")
    
    country_counts = {}
    for job in existing_jobs:
        country = job.get('country', 'Unknown')
        country_counts[country] = country_counts.get(country, 0) + 1
    
    log(f"\nBy country:")
    for country, count in sorted(country_counts.items()):
        log(f"  {country}: {count}")

if __name__ == "__main__":
    main()
