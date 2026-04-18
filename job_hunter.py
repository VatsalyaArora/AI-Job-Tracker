import pandas as pd
import subprocess
import gspread
import time
from oauth2client.service_account import ServiceAccountCredentials
from jobspy import scrape_jobs
import numpy as np

# --- SETTINGS ---
REGION = "Milan, Italy" # You can change this to "Munich" or "Eindhoven"
SHEET_NAME = "Jobs" # Make sure this matches your Sheet title
CREDENTIALS_FILE = 'credentials.json'

def get_llama_score(title, description):
    """Ask your local Llama 3 to grade the job based on your CV."""
    prompt = f"""
    Candidate: AI Master's Student, 3+ yrs exp, C++, Unreal Engine, CV (Car Detection Project).
    Job: {title}
    Description: {description[:500]}
    
    On a scale of 0 to 100, how well does this job match a C++ AI Engineer?
    Return ONLY the number.
    """
    try:
        res = subprocess.run(['ollama', 'run', 'llama3', prompt], capture_output=True, text=True, encoding='utf-8')
        # Extract just the digits from the output
        return int(''.join(filter(str.isdigit, res.stdout)))
    except:
        return 0

# 1. SCRAPE JOBS
print("🚀 Scraping LinkedIn & Indeed...")
jobs = scrape_jobs(
    site_name=["linkedin", "indeed", "glassdoor"],
    search_term="AI Engineer, AI Engineer Intern",
    location=REGION,
    results_wanted=50,
    hours_old=72,
    country_indeed="italy",
    linkedin_fetch_description=True
)

if not jobs.empty:
    print("🧠 Grading...")
    jobs['score'] = jobs.apply(lambda x: get_llama_score(x.title, x.description), axis=1)
    jobs = jobs.sort_values(by='score', ascending=False)

    # CRITICAL: Clean NaN values so Google API doesn't crash
    jobs = jobs.replace([np.nan, np.inf, -np.inf], None)
    jobs = jobs.fillna("")

    # 3. PUSH TO GOOGLE SHEETS
    print("📝 Syncing to Google...")
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, scope)
    client = gspread.authorize(creds)

    for attempt in range(3):
        try:
            sheet = client.open(SHEET_NAME).sheet1
            
            # Prepare data: score, title, company, link
            # We convert to string to be extra safe with JSON
            final_list = jobs[['score', 'title', 'company', 'job_url']].values.tolist()
            header = ["Match Score", "Job Title", "Company", "Link"]
            full_upload = [header] + final_list

            sheet.clear()
            # UPDATED SYNTAX: Values first, then Range
            sheet.update(full_upload, 'A1') 
            
            print("✅ Success! Check your sheet.")
            break
        except Exception as e:
            print(f"Attempt {attempt+1} failed: {e}. Retrying...")
            time.sleep(5)
else:
    print("❌ No jobs found.")