# Kingston Job Combiner 🚀

An automated background ingestion engine designed to aggregate local employment listings across Kingston, ON into a centralized cloud database architecture.

## Project Architecture

- **Layer 1: Ingestion Engine** -> Multi-module Python background web scrapers with defensive error handling, case-sensitive geographic filtering, and request throttling.
- **Layer 2: Central Database** -> Secure cloud-hosted MongoDB Atlas document cluster utilizing hidden `.env` configurations.

## Current Worker Modules

- [x] St. Lawrence College (SLC) Board Worker (`slc_scraper.py`)
- [x] Queen's University Module (`queens_scraper.py`)
- [ ] City Hall Module

## Setup & Local Installation

1. Clone the repository and navigate into the workspace directory.
2. Install the necessary system dependencies:
   ```bash
   pip install requests beautifulsoup4 pymongo python-dotenv dnspython
   ```
3. Create a local hidden configuration file named `.env` and assign your connection string:
   ```text
   MONGO_URI=mongodb+srv://<username>:<password>@cluster.mongodb.net/
   ```
4. Execute the live worker pipeline script:
   ```bash
   python slc_scraper.py
   ```
