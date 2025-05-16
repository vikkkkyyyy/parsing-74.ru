import time
import schedule
from datetime import datetime
from app.scripts.parse import ParseManager
from app.db.methods import (
    create_tables_if_not_exist,
    insert_received_data
)

COUNT = 1

def job():
    global COUNT
    print(f"[{datetime.now()}]: Выполняю задачу ({COUNT})")
    create_tables_if_not_exist()
    
    parse_manager = ParseManager()
    
    links_with_dates = parse_manager.get_posts_links_with_dates()
    received_data = parse_manager.parse_links(links_with_dates)
    
    insert_received_data(received_data)
    print(f"[{datetime.now()}]: Закончил выполнять задачу ({COUNT})")
    COUNT += 1
    
schedule.every(2).hours.do(job)


while True:
    schedule.run_pending()
    time.sleep(5)