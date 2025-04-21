import requests
import json
import dateparser
import os
import time
from datetime import datetime

from bs4 import BeautifulSoup
from dotenv import load_dotenv

from app.db.methods import create_tables_if_not_exist, drop_tables, add_post, update_post, update, select_post_by_theme, delete_post_by_url, get_last_date_post


load_dotenv()
TARGET_URL = os.getenv("TARGET_URL")


create_tables_if_not_exist()
headers = {
    "Accept": "*/*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"
}
def get_posts_links(): 
    req = requests.get(TARGET_URL + "/text", headers=headers)
    result = []
    if req.status_code == 200:
        soup = BeautifulSoup(req.content, "lxml")
        h2_tags = soup.find_all("h2", class_="h9Jmx")
        for elem in h2_tags:
            link = elem.find("a", href=True)
            if link:
                link = link["href"]
                if "/text/" in link and "?" not in link:
                    result.append(link)
    return result
def parse_link(link: str, update=False):
    try:
        if update:
            req = requests.get(link, headers=headers)
        else:
            req = requests.get(TARGET_URL + link, headers=headers)
        
        if req.status_code == 200:
            soup = BeautifulSoup(req.content, "lxml")
            try:
                theme = soup.find("span", class_="d-flex align-items-c").text[1:]
                header = soup.find("h1", class_="title_Gq8Rx").text
                date = soup.find("a", class_="link_VmtHQ").text
                
                parsed_date = dateparser.parse(
                    date,
                    languages=['ru', 'en'],  
                    settings={'PREFER_DATES_FROM': 'past'}  
                )
                
                
                if not parsed_date:
                    print(f"[WARNING] Не известная дата: '{date}'")
                    parsed_date = datetime.now() 
                    
                last_date_post = get_last_date_post()
                if last_date_post is not None:

                    if parsed_date > last_date_post:
                        print(f"Новый пост с более свежей датой: {parsed_date} > {last_date_post}")
                    else:
                        print(f"Пост с устаревшей датой: {parsed_date} <= {last_date_post}")
                        return None
                    
                
                text_list = soup.find_all("div", class_="uiArticleBlockText_g83x5 text-style-body-1 c-text block_fefJj")
                author = soup.find("a", class_="link_GQmWc").text
                
                text = ''
                for elem in text_list:
                    text += elem.text
            except Exception as e:
                print(f"[ERROR]: Какие-либо данные не были получены! Подробнее: {e}")
                return None

            result = {
                "theme": theme,
                "header": header,
                "date": parsed_date,  
                "text": text,
                "author": author
            }
            return result
    except Exception as e:
        print(f"[INFO] Пропустил ссылку {TARGET_URL + link}...")

try:
    create_tables_if_not_exist()
    start = time.time()
    links = get_posts_links()
    for link in links:
        result = parse_link(link)
        if not result:
            break
        else:
            add_post(
                url=TARGET_URL+link,
                theme=result["theme"],
                header=result["header"],
                text=result["text"],
                author=result["author"],
                date=result["date"]
            )
    end = time.time()

    print(f"Time spent: {round(end - start, 2)}sec.")
    
    
    
except KeyboardInterrupt:
    print("[INFO]: Программа была принудительно остановленна!")