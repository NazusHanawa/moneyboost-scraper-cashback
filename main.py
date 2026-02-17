import os
import time

from dotenv import load_dotenv
from database import DB
from scrapers import CashbackScraper
from platforms import platforms_list


load_dotenv()

db = DB(os.environ.get("DATABASE_URL"), os.environ.get("AUTH_TOKEN"))

partnerships = db.get_partnerships()
last_cashbacks = db.get_last_cashbacks()

cashback_scrapper = CashbackScraper(partnerships, platforms_list, last_cashbacks)

first_time = time.time()
last_update_time = 0
scrap_count = 0
UPDATE_TIME = 3600

while True:
    try:
        scrap_count += 1
        current_time = time.time()
        print(f"\nScrapping {scrap_count}: {current_time - first_time:.0f}s")
        
        new_cashbacks = cashback_scrapper.get_new_cashbacks()
        if new_cashbacks:
            print(f"NEW: {new_cashbacks}")
            db.update_old_cashbacks_date_end(cashback_scrapper.old_cashbacks)
            db.add_cashbacks(new_cashbacks.values())
            last_update_time = current_time
        elif current_time - last_update_time >= UPDATE_TIME:
            print("Update date_end...")
            db.update_old_cashbacks_date_end(cashback_scrapper.old_cashbacks)
            last_update_time = current_time
            
    except KeyboardInterrupt:
        break
    except Exception as e:
        print(f"Main loop erro: {e}")
        time.sleep(30)
        continue
        
    
    
    
    




