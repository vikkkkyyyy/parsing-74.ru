import requests
import os
from typing import Optional
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from datetime import datetime
from app.db.methods import get_last_date_post

load_dotenv()
TARGET_URL = os.getenv("TARGET_URL")
HEADERS = {
    "Accept": "*/*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"
}


class ParseManager:
    def __init__(self):
        self.req_links = requests.get(TARGET_URL + "/text", headers=HEADERS)
        self.soup_links = BeautifulSoup(self.req_links.content, "lxml")
    
    def comparing_dates(self, db_date: datetime, post_date: datetime) -> bool:
        if db_date:
            if post_date > db_date:
                return True
            return False
        return True
        
    def get_posts_links_with_dates(self) -> Optional[dict]:
        try: 
            result = {}
            if self.req_links.status_code == 200:
                try:
                    h2_tags = self.soup_links.find_all("h2", class_="h9Jmx")
                    links = []
                    for elem in h2_tags:
                        link = elem.find("a", href=True)
                        if link:
                            link = link["href"]
                            if "/text/" in link and "?" not in link and "longread" not in link:
                                links.append(link)
                    
                    time_tags = self.soup_links.find_all("time", class_="_2DfZq")
                    dates = []
                    for tag in time_tags:
                        datetime_value = tag.get("datetime")
                        datetime_value = datetime.strptime(datetime_value, "%Y-%m-%dT%H:%M:%S")
                        dates.append(datetime_value)
                    
                    result = dict(zip(links, dates))
                    
                except Exception as e:
                    print(f"[ERROR] Ошибка при получении ссылок на новости: {e}")
            else:
                print(f"[ERROR] Неверный ответ сервера: {self.req_links.status_code}")
                
            return result
        
        except Exception as e:
            print(f"[CRITICAL] Непредвиденная ошибка: {e}")
            return None
        
    def parse_links(self, links_dates_dict: dict) -> Optional[list]:
        try:
            result = []
            
            db_last_date = get_last_date_post()
            
            for link, date in links_dates_dict.items():
                if not self.comparing_dates(db_last_date, date):
                    break
            
                req = requests.get(TARGET_URL + link, headers=HEADERS)
                if req.status_code == 200:
                    soup = BeautifulSoup(req.content, "lxml")
                    
                    try:
                        theme = soup.find("span", class_="d-flex align-items-c").text[1:]
                    except Exception as e:
                        print(f"[WARNING] Тема не была получена: {e}")
                        theme = None
                    try:
                        header = soup.find("h1", class_="title_Gq8Rx").text
                    except Exception as e:
                        print(f"[ERROR] Заголовок не был получен: {e}")
                        continue
                    try:
                        text_list = soup.find_all("div", class_="uiArticleBlockText_g83x5 text-style-body-1 c-text block_fefJj")
                    except Exception as e:
                        print(f"[ERROR] Текст новости не был получен: {e}")
                        continue
                    try:
                        author = soup.find("a", class_="link_GQmWc").text
                    except Exception as e:
                        print(f"[WARNING] Автор записи не был получен: {e}")
                        author = None
                    text = ''
                    for elem in text_list:
                        text += elem.text
                        
                    result.append((link, theme, header, text, author, date))
                
                else:
                    print(f"[ERROR] Неверный ответ сервера: {req.status_code}")
                    
            return result             
                
        except Exception as e:
            print(f"[CRITICAL] Непредввиденная ошибка: {e}")
            return None