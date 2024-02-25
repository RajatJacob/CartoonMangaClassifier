import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import urllib
import re
import json
import math
import os
import shutil
from pathlib import Path
from bs4 import BeautifulSoup

driver = None


def get_driver():
    global driver
    if driver is None:
        chrome_options = webdriver.ChromeOptions()
        # chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        driver = webdriver.Chrome(options=chrome_options)
    return driver


category_queries = json.load(open('category_queries.json'))


def get_from_google_images(query, path):
    driver = get_driver()
    if not os.path.exists(path):
        os.makedirs(path)
    url = (
        "https://www.google.com/search?q={s}&tbm=isch&tbs=sur%3Afc&hl=en"
        "&ved=0CAIQpwVqFwoTCKCa1c6s4-oCFQAAAAAdAAAAABAC&biw=1251&bih=568"
    )

    driver.get(url.format(s=query))

    driver.execute_script(
        "window.scrollTo(0,document.body.scrollHeight);")
    driver.implicitly_wait(1)
    driver.execute_script("window.scrollTo(0,0);")
    driver.implicitly_wait(1)

    imgResults = driver.find_elements(
        By.XPATH, "//img[contains(@class,'Q4LuWd')]")

    print("Got results.")

    src = []
    for img in imgResults:
        distance_from_top = math.sqrt(
            img.location['x'] + img.location['y'])
        src.append((distance_from_top, img.get_attribute('src')))

    src = list(map(lambda i: i[1], sorted(src, key=lambda i: i[0])))

    print(f"Got {len(src)} image URLs.")

    if len(src) == 0:
        return

    for i in range(10):
        standarised_query = re.sub(r'\s', '', str(query).lower())
        file_path = f"{path}/{standarised_query}{i}.jpg"
        urllib.request.urlretrieve(str(src[i]), file_path)
        print(f"Downloaded image [{file_path}].")


def get_all_google_images():
    shutil.rmtree('images')
    for category, queries in json.load(open('category_queries.json')).items():
        for query in queries:
            get_from_google_images(query, f'images/{category}')


def get_from_imdb(title_id: str):
    driver = get_driver()
    url = f'https://www.imdb.com/title/{title_id}/mediaindex'
    driver.get(url)
    driver.implicitly_wait(1)
    a_wait = WebDriverWait(driver, 10)
    a = a_wait.until(EC.element_to_be_clickable(
        (By.CSS_SELECTOR, '#media_index_thumbnail_grid a img')))
    a.click()
    for _ in range(100):
        img = driver.find_element(By.CSS_SELECTOR, 'img.peek')
        src = img.get_attribute('src')
        file_name = src.split('/')[-1]
        file_path = Path(f'images/manga/{title_id}/{file_name}')
        file_path.parent.mkdir(parents=True, exist_ok=True)
        urllib.request.urlretrieve(str(src), str(file_path))
        next_button = driver.find_element(By.CLASS_NAME, 'ipc-pager--right')
        next_button.click()


def download_all_imdb_titles():
    TITLES = {
        "Attack On Titan": "tt2560140",
        "Jujutsu Kaisen": "tt12343534",
        "Tokyo Ghoul": "tt3741634",
        "Demon Slayer": "tt9335498"
    }
    for title, title_id in TITLES.items():
        get_from_imdb(title_id)


def download_garfield():
    # This is a static site, so BeautifulSoup makes more sense
    BASE_URL = "http://pt.jikos.cz/garfield/"
    soup = BeautifulSoup(requests.get(BASE_URL).text, 'html.parser')
    p = soup.find_all('p')[1]
    links = [f'{BASE_URL}{a.text}' for a in p.find_all('a')]
    img_urls = set()
    for link in links[:20]:
        soup = BeautifulSoup(requests.get(link).text, 'html.parser')
        img = soup.find_all('img')
        img_urls.update({i['src'] for i in img})
    for img_url in img_urls:
        try:
            file_name = '-'.join(img_url.split('/')[-2:])
            print(file_name)
            file_path = Path(f'images/cartoons/{file_name}')
            file_path.parent.mkdir(parents=True, exist_ok=True)
            urllib.request.urlretrieve(str(img_url), str(file_path))
        except Exception:
            pass


if __name__ == '__main__':
    # get_all_google_images()
    download_all_imdb_titles()
    download_garfield()
