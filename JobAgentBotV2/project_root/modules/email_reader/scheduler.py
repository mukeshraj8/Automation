# scheduler.py

import schedule
import time
from processor import process_emails  # This will be in main processing module

def job():
    print("Running scheduled job for email processing...")
    process_emails()

def start_scheduler(interval_minutes: int = 15):
    schedule.every(interval_minutes).minutes.do(job)
    print(f"Scheduler started - running every {interval_minutes} minutes.")
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        print("Scheduler interrupted. Exiting...")

if __name__ == "__main__":
    start_scheduler()
