import os
import requests
from bs4 import BeautifulSoup
import time
import pymongo
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

CONNECTION_STRING = os.getenv("MONGO_URI")
mongo_client = pymongo.MongoClient(CONNECTION_STRING)
db = mongo_client["job_board"]
jobs_collection = db["jobs"]

queens_url = "https://queensu.njoyn.com/cl4/xweb/Xweb.asp?tbtoken=Y1pfQB4XCBN7FAd3NyBUCFs6ARBEcFdbe0gjWi19E2NbL0ZvL0VqdBAEAgkbUxFaS3cqWA%3D%3D&chk=ZVpaShw%3D&page=joblisting&CLID=74827"
response = requests.get(queens_url)
soup = BeautifulSoup(response.content, "html.parser")
print(response.status_code)

all_saved_jobs = []

for row in soup.find_all('tr')[1:]:
    cells = row.find_all('td')
    
    if len(cells) > 1:

        title = cells[1].text.strip()
        company = "Queen's University" 
        

        anchor = row.find('a')
        if anchor:
            relative_path = anchor.get('href')
            base_portal_url = "https://queensu.njoyn.com/cl4/xweb/"
            job_url = relative_path if relative_path.startswith("http") else base_portal_url + relative_path
        else:
            job_url = "N/A"
            

        raw_date_text = cells[5].text.strip()
        try:

            expiry_date_object = datetime.strptime(raw_date_text, "%B %d, %Y")
        except Exception as e:
            expiry_date_object = None


        job_payload = {
            "title": title,
            "company": company,
            "job_url": job_url,
            "expiry_date": expiry_date_object
        }

        existing_job = jobs_collection.find_one({"job_url": job_url})

        if existing_job:
            print(f"-> Queen's job already exists in storage. Skipping.")
        else:
            jobs_collection.insert_one(job_payload)
            print(f"Successfully saved NEW Queen's job: {title}")
            
        print("-" * 40)