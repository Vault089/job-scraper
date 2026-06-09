#!/usr/bin/env python3
"""
Push scraped jobs to Curric.app
Reads jobs_data.json from scraper output and POSTs to /api/jobs/ingest
"""
import json
import requests
import sys
import os
from datetime import datetime

API_URL = "https://curric-app.vercel.app/api/jobs/ingest"
API_KEY = "curric-scrape-2026"

def load_jobs(filepath):
    with open(filepath, 'r') as f:
        return json.load(f)

def map_job(raw, source):
    """Map scraper output to Curric.app job format"""
    # Parse salary
    salary_min = None
    salary_max = None
    salary_currency = "USD"
    
    salary_str = raw.get("salary_usd") or raw.get("salary", "")
    if "USD" in salary_str or "usd" in salary_str.lower():
        salary_currency = "USD"
    elif "CNY" in salary_str or "rmb" in salary_str.lower():
        salary_currency = "CNY"
    elif "VND" in salary_str or "vnd" in salary_str.lower():
        salary_currency = "VND"
    
    # Extract numbers from salary
    import re
    numbers = re.findall(r'[\d,]+\.?\d*', salary_str.replace(",", ""))
    if len(numbers) >= 2:
        salary_min = int(float(numbers[0]))
        salary_max = int(float(numbers[1]))
    elif len(numbers) == 1:
        salary_min = int(float(numbers[0]))
        salary_max = salary_min
    
    # Map country
    location = raw.get("location", "")
    country = raw.get("country", "")
    if not country:
        if source == "china" or "CNY" in salary_str:
            country = "China"
        elif source == "vietnam" or "VND" in salary_str:
            country = "Vietnam"
        else:
            country = "China"  # default
    
    # Map job type
    job_type = raw.get("job_type", "Full Time")
    
    # Build description
    desc_parts = []
    if raw.get("description"):
        desc_parts.append(raw["description"][:2000])
    if raw.get("tags"):
        desc_parts.append("\n\nBenefits: " + ", ".join(raw["tags"]))
    if raw.get("url"):
        desc_parts.append(f"\n\nOriginal listing: {raw['url']}")
    
    return {
        "title": raw.get("title", "").strip(),
        "company": raw.get("company", "Unknown School").strip(),
        "country": country,
        "city": location if location else None,
        "job_type": job_type,
        "subject": "english",
        "grade_level": None,
        "salary_min": salary_min,
        "salary_max": salary_max,
        "salary_currency": salary_currency,
        "description": "\n".join(desc_parts),
        "min_experience": 2,
        "required_education": "Bachelor's degree",
        "source": source,
    }

def push_jobs(jobs, source):
    """Push jobs to Curric.app API"""
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}",
    }
    
    # Send in batches of 10
    batch_size = 10
    total_created = 0
    total_duplicates = 0
    total_errors = 0
    
    for i in range(0, len(jobs), batch_size):
        batch = jobs[i:i+batch_size]
        try:
            resp = requests.post(API_URL, json=batch, headers=headers, timeout=30)
            if resp.status_code == 200:
                data = resp.json()
                total_created += data.get("created", 0)
                total_duplicates += data.get("duplicates", 0)
                total_errors += data.get("errors", 0)
                print(f"  Batch {i//batch_size + 1}: {data.get('created')} created, {data.get('duplicates')} dupes, {data.get('errors')} errors")
            else:
                print(f"  Batch {i//batch_size + 1}: HTTP {resp.status_code} - {resp.text[:200]}")
                total_errors += len(batch)
        except Exception as e:
            print(f"  Batch {i//batch_size + 1}: ERROR - {e}")
            total_errors += len(batch)
    
    return total_created, total_duplicates, total_errors

def main():
    print(f"=== Curric.app Job Ingestion === {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
    
    # China jobs
    china_file = "/mnt/f/job_scraper/jobs_data.json"
    if os.path.exists(china_file):
        raw_jobs = load_jobs(china_file)
        jobs = [map_job(j, "china") for j in raw_jobs]
        print(f"China: {len(jobs)} jobs loaded")
        created, dupes, errors = push_jobs(jobs, "china")
        print(f"China result: {created} created, {dupes} duplicates, {errors} errors\n")
    else:
        print(f"China: {china_file} not found, skipping\n")
    
    # Vietnam jobs
    vietnam_file = "/mnt/f/job_scraper/vietnam/jobs_data.json"
    if os.path.exists(vietnam_file):
        raw_jobs = load_jobs(vietnam_file)
        jobs = [map_job(j, "vietnam") for j in raw_jobs]
        print(f"Vietnam: {len(jobs)} jobs loaded")
        created, dupes, errors = push_jobs(jobs, "vietnam")
        print(f"Vietnam result: {created} created, {dupes} duplicates, {errors} errors\n")
    else:
        print(f"Vietnam: {vietnam_file} not found, skipping\n")
    
    print("Done!")

if __name__ == "__main__":
    main()
