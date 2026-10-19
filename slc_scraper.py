import os
import requests
from bs4 import BeautifulSoup
import time
import pymongo
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()  # Load environment variables from .env file
# PHASE 2: INITIALIZE MONGO
CONNECTION_STRING = os.getenv("MONGO_URI")

mongo_client = pymongo.MongoClient(CONNECTION_STRING)
db = mongo_client["job_board"]
jobs_collection = db["jobs"]


# TARGET THE HUB & BUILD THE ARRAY (Your continuous progress)
slc_url = "https://slc.totalhire.com"
response = requests.get(slc_url)
soup = BeautifulSoup(response.content, "html.parser")
print(response.status_code)

job_urls = []
for anchor in soup.find_all('a', class_="joblink"):

    relative_path = anchor.get('href')

    if relative_path:
        full_url = slc_url + relative_path
        job_urls.append(full_url)
print(f"Successfully queued up {len(job_urls)} individual job URLs!")
#THE AUTOMATED LOOP
for job_url in job_urls:

    # We fetch the specific job page from the list
    job_response = requests.get(job_url)
    detail_soup = BeautifulSoup(job_response.content, "html.parser")

    # SAFE TITLE EXTRACTION
    job_title_element = detail_soup.find("h2", attrs={"itemprop": "title"})
    title = job_title_element.text.strip() if job_title_element else "N/A"


    # SAFE COMPANY EXTRACTION
    employer_shell = detail_soup.find('li', class_="employer")
    if employer_shell:
        company_element = employer_shell.find('a')
        company = company_element.text.strip() if company_element else "N/A"
    else:
        company = "N/A"

    # SAFE LOCATION EXTRACTION
    location_shell = detail_soup.find('li', id='form-item-43')
    if location_shell:
        all_spans = location_shell.find_all('span')
        city_text = all_spans[1].text.strip() if len(all_spans) > 1 else "N/A"
    else:
        city_text = "N/A"
    print(f"Checking Location Text: '{city_text}'")
    if "Kingston" not in city_text:
        print(f"Skipping: Not a Kingston role.")
        print("-" * 40)
        time.sleep(1.5)
        continue

    date_element = detail_soup.find("li", class_="closedate")
    
    if date_element:
        raw_text = date_element.text.strip()
        clean_date_str = raw_text.replace("Closing Date:", "").strip() # e.g. "Dec 31, 2026"
        
        try:
            # Convert the text string into an official, calculable date object
            # %b = Short month name (Dec), %d = Day (31), %Y = Year (2026)
            expiry_date_object = datetime.strptime(clean_date_str, "%b %d, %Y")
        except Exception as e:
            # Fallback if a date is written in a weird format
            expiry_date_object = None
    else:
        expiry_date_object = None
    # STORE THE EXTRACTED DATA IN MONGODB
    job_payload = {
        "title": title,
        "company": company,
        "job_url": job_url,
        "expiry_date": expiry_date_object
    }

    # check if the job already exists in the database to avoid duplicates
    existing_job = jobs_collection.find_one({"job_url": job_url})

    if existing_job:
        print(f"-> Job already exists in the database. Skipping database insertion")
    else:
        print(f"Prepared package for database: {job_payload['title']}")
        jobs_collection.insert_one(job_payload)
        print(f"Successfully saved to Cloud Database!")
    
    print("-" * 40)
    # print(f"-> Title: {title}")
    # print(f"-> Company: {company}")
    # print("-" * 40)
    time.sleep(1.5)  # Sleep for 1.5 seconds to avoid overwhelming the server

print("\n--- READING LIVE STOREAGE CONTENT FROM MONGO ---")

all_saved_jobs = jobs_collection.find()

for saved_job in all_saved_jobs:
    print(f"Database Record -> Title: {saved_job['title']} | Company: {saved_job['company']} | Expiry Date: {saved_job['expiry_date']}")
    print("-" * 50)


print("\n--- RUNNING EXPIRATION CLEANER ENGINE ---")

#  Grab the exact date and time of right now
current_time = datetime.now()

query_filter = {"expiry_date": {"$lt": current_time}}
delete_result = jobs_collection.delete_many(query_filter)

print(f"Cleanup complete! Automatically removed {delete_result.deleted_count} expired postings from your database.")
