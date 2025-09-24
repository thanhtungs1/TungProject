from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement
from concurrent.futures import ThreadPoolExecutor, as_completed
from selenium.webdriver.common.action_chains import ActionChains, ScrollOrigin
import pandas as pd
import time
import sys
import os
from selenium.webdriver.chrome.options import Options  

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, parent_dir)

from db_manipulator import insert_update_data


start = time.time()

provinces = [
    'ho-chi-minh', 'ha-noi', 'da-nang','can-tho','hai-phong','hue','khanh-hoa','dong-nai','nghe-an','vung-tau',
    'an-giang','bac-lieu','bac-giang','bac-ninh','ben-tre','binh-duong','binh-dinh','binh-phuoc',
    'binh-thuan','ca-mau','dak-lak','dien-bien','dong-thap'
]
categories = ['food', 'fresh']
urls = [f"https://shopeefood.vn/{province}/{cat}/deals" for province in provinces for cat in categories]

def scroll_down(driver, scroll_times=3, delay=0.5):
    last_height = driver.execute_script("return document.body.scrollHeight")
    for _ in range(scroll_times):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(delay)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

def next_page(driver):
    try:
        previous_page = driver.find_element(By.CSS_SELECTOR, 'li.active').text
        next_btn = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "span.icon.icon-paging-next"))
        )
        driver.execute_script("arguments[0].click();", next_btn)
        time.sleep(1)
        new_page = driver.find_element(By.CSS_SELECTOR, 'li.active').text
        if new_page == previous_page:
            return False
        return True
    except Exception as e:
        print("Lỗi ở NextPage")
    return False

def get_data(url):
    page = 1
    crawled_data = []

    driver = webdriver.Chrome() 
    try:
        driver.get(url)
        print(f"🔍 Đang truy cập: {url}")

        WebDriverWait(driver, 10).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )

        while True:
            scroll_down(driver)
            try:
                restaurants = WebDriverWait(driver, 20).until(
                    EC.presence_of_all_elements_located((By.CLASS_NAME, 'item-restaurant'))
                )
            except:
                print(f"Không tìm thấy nhà hàng trên trang: {url}")
                break

            for restaurant in restaurants:
                try:
                    address_name = restaurant.find_element(By.CLASS_NAME, 'name-res').text
                    address = restaurant.find_element(By.CLASS_NAME, 'address-res').text
                    crawled_data.append({
                                "address_name": address_name,
                                "address": address,
                                "geometry": None,
                                "source_id": 8
                                })
                except:
                    continue

            if not next_page(driver):
                print(f" --> Đã lấy hết dữ liệu: {url}")
                break
            page += 1

    finally:
        driver.quit()
    return insert_update_data(crawled_data)  


def crawl():
    with ThreadPoolExecutor(max_workers=2) as executor:
        for url in urls:
            executor.submit(get_data, url)



if __name__ == '__main__':
    crawl()

