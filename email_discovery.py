#!/usr/bin/env python3
"""
Email discovery for job postings.
For each job: try extract from posting → try company website → fallback agency addresses.
Only jobs with a valid email path survive to the application stage.
"""
import re, urllib.request, urllib.parse, time, random, ssl
from html import unescape

# ── Agency fallbacks (for job board posts where the agency is the application channel) ──
AGENCY_FALLBACKS = {
    'Legal & Teaching Jobs for Foreign Teachers in Vietnam': 'info@legalandteachingjobs.com',
    'Atlantic Teacher Careers': 'info@atlanticteacher.com',
    'TEFL UK': 'info@tefluk.com',
    'Guardian Jobs': 'info@guardianjobs.com',
    'Global TEFL - Global Language Training Ltd.': 'info@globaltefl.com',
    'LUKglobal': 'headstartvietnam@gmail.com',  # already in posting
    'Step Up Education': 'recruitment@stepup.edu.vn',  # already in posting
}

# ── Known company email patterns (companies that consistently use the same contact) ──
KNOWN_COMPANY_EMAILS = {
    'ila': 'recruitment@ila.edu.vn',
    'apollo english': 'careers@apollo.edu.vn',
    'vus smart english': 'careers@vus.edu.vn',
    'british council vietnam': 'vietnam@britishcouncil.org',
    'rmit vietnam': 'hr.vietnam@rmit.edu.vn',
    'kiwi english vietnam': 'recruitment@kiwienglish.edu.vn',
    'kyna english': 'hr@kynaforkids.vn',
    'atlantic five-star english': 'recruitment@atlantic.edu.vn',
    'vinschool': 'tuyensinh@vinschool.edu.vn',
}

# ── Candidate email patterns (valid corporate emails, not Gmail/QQ/etc.) ──
CORPORATE_EMAIL_RE = re.compile(
    r'[\w.+%+-]+@[\w-]+\.[\w.-]+',
    re.IGNORECASE
)
GMAIL_PATTERNS = ['gmail', 'yahoo', 'hotmail', 'outlook', 'live', 'qq.com', '163.com', '126.com', 'example.com']
SPAM_TRAP_PATTERNS = ['noreply', 'no-reply', 'donotreply', 'jobs@indeed', 'linkedin', 'support@', 'info@generic']


def extract_from_posting(job) -> list[str]:
    """Extract emails directly from job description/requirements fields."""
    texts = [
        job.get('description', ''),
        job.get('requirements', ''),
        job.get('title', ''),
        job.get('company', ''),
    ]
    all_text = ' '.join(t for t in texts if t)
    
    # Find all email-like strings
    candidates = CORPORATE_EMAIL_RE.findall(all_text)
    
    valid = []
    for email in candidates:
        email_lower = email.lower()
        # Skip obvious noise
        if any(bad in email_lower for bad in GMAIL_PATTERNS):
            continue
        if any(bad in email_lower for bad in SPAM_TRAP_PATTERNS):
            continue
        # Skip if too generic / single-letter domain
        domain = email.split('@')[1].lower() if '@' in email else ''
        if len(domain) < 4 or domain.startswith('example'):
            continue
        valid.append(email.lower())
    
    return list(set(valid))


def extract_domain_from_company(company_name: str) -> str | None:
    """Guess company website domain from company name."""
    # Clean up company name
    clean = company_name.lower().strip()
    clean = re.sub(r'[^\w\s]', ' ', clean)
    clean = re.sub(r'\s+', ' ', clean)
    
    # Remove common suffixes
    for suffix in [' vietnam', ' vietnam co., ltd', ' co., ltd', ' ltd', ' jsc', ' inc.', ' corp.']:
        if clean.endswith(suffix):
            clean = clean[:-len(suffix)].strip()
    
    # Remove common words
    for word in ['international', 'global', 'school', 'education', 'academy', 'university', 'college']:
        clean = clean.replace(word, '').strip()
    
    # Build domain candidates
    if not clean or len(clean) < 2:
        return None
    
    candidates = [
        f"https://{clean}.com",
        f"https://{clean}.edu.vn",
        f"https://{clean}.edu.vn",
        f"https://www.{clean}.com",
        f"https://www.{clean}.edu.vn",
    ]
    
    return candidates


def scrape_company_for_email(browser, company_name: str, job_id: str = '') -> str | None:
    """
    Attempt to find a contact/HR email by scraping the company's website.
    Returns first valid corporate email found, or None.
    """
    domains = extract_domain_from_company(company_name)
    if not domains:
        return None
    
    for domain in domains[:3]:
        try:
            ctx = ssl.create_default_context()
            req = urllib.request.Request(domain, headers={
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html',
            })
            with urllib.request.urlopen(req, timeout=8, context=ctx) as r:
                html = r.read().decode('utf-8', errors='ignore')
            
            # Find emails in page text
            emails = CORPORATE_EMAIL_RE.findall(html)
            for email in emails:
                email_lower = email.lower()
                if any(bad in email_lower for bad in GMAIL_PATTERNS):
                    continue
                if any(bad in email_lower for bad in SPAM_TRAP_PATTERNS):
                    continue
                domain_part = email.split('@')[1].lower()
                # Must be same domain as company, or a known corporate domain
                if domain_part == domains[0].split('/')[-1].split('.')[0]:
                    continue  # skip partial matches from nav
                return email.lower()
            
            # Also look for mailto: links
            mailto_matches = re.findall(r'mailto:([^\s<>"\']+)', html, re.I)
            for match in mailto_matches:
                email = match.split('?')[0]  # strip query params
                if '@' in email:
                    email_lower = email.lower()
                    if not any(bad in email_lower for bad in GMAIL_PATTERNS + SPAM_TRAP_PATTERNS):
                        return email.lower()
        
        except Exception:
            pass
        
        time.sleep(random.uniform(0.5, 1.0))
    
    return None


def discover_email(job, browser=None) -> str | None:
    """
    Full email discovery pipeline for a single job.
    Returns the best email to use, or None if no email path exists.
    """
    company = job.get('company', '').strip()
    job_id = job.get('id', '')
    
    # Step 1: Extract from posting
    emails_from_posting = extract_from_posting(job)
    if emails_from_posting:
        # Return the first corporate email found in posting
        return emails_from_posting[0]
    
    # Step 2: Check known company emails
    company_lower = company.lower()
    for known, email in KNOWN_COMPANY_EMAILS.items():
        if known in company_lower:
            return email
    
    # Step 3: Check agency fallbacks
    for agency, fallback_email in AGENCY_FALLBACKS.items():
        if agency.lower() in company_lower:
            return fallback_email
    
    # Step 4: Try to scrape company website (if browser available)
    if browser:
        scraped = scrape_company_for_email(browser, company, job_id)
        if scraped:
            return scraped
    
    return None


def job_has_email_path(job, browser=None) -> bool:
    """Returns True if the job has a valid email path we can apply through."""
    email = discover_email(job, browser)
    return email is not None


def enrich_job_with_email(job, browser=None) -> dict:
    """
    Run email discovery on a job dict. Adds 'recruiter_email' field.
    If no email found, marks 'no_email_path': True.
    """
    email = discover_email(job, browser)
    job['recruiter_email'] = email
    if email:
        job['email_path'] = 'direct'
    else:
        job['no_email_path'] = True
        job['email_path'] = 'none'
    return job


if __name__ == '__main__':
    # Quick test
    test_jobs = [
        {'company': 'Atlantic Teacher Careers', 'title': 'Full-time Secondary Teacher',
         'description': 'Apply at recruitment@atlantic.edu.vn', 'id': '1'},
        {'company': 'Legal & Teaching Jobs for Foreign Teachers in Vietnam',
         'title': 'ESL Teacher', 'description': 'Contact us at info@legalandteachingjobs.com', 'id': '2'},
        {'company': 'Some Random School', 'title': 'Teacher',
         'description': 'Apply through LinkedIn only', 'id': '3'},
    ]
    
    for j in test_jobs:
        result = discover_email(j)
        print(f"[{j['company'][:30]}] -> {result}")