import time
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.common.exceptions import StaleElementReferenceException
from multiprocessing.dummy import Pool as ThreadPool
from threading import Lock

def initialize_driver():
    chrome_options = Options()
    webdriver_service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=webdriver_service, options=chrome_options)
    return driver

# инициализируем 5 драйверов
drivers = [initialize_driver() for _ in range(5)]

def get_link_from_page(driver, url):
    try:
        driver.get(url)
        element = WebDriverWait(driver, 2).until(
            EC.presence_of_element_located((By.CLASS_NAME, "xt0psk2"))
        )
        link = element.get_attribute('href')
        # Записываем ссылку в файл
        with open("processed_links.txt", "a", encoding="utf-8") as file:
            file.write(link + "\n")
        return link
    except StaleElementReferenceException:
        print("Link Moved")
        return None
    except (NoSuchElementException, TimeoutException):
        return None

def find_email_and_name(driver):
    # Finding email
    try:
        element = WebDriverWait(driver, 2).until(
            EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div/div[1]/div/div[3]/div/div/div/div[1]/div[1]/div/div/div[4]/div[2]/div/div[1]/div[2]/div/div[1]"))
        )
        html = element.get_attribute('innerHTML')
        email_regex = r"[\w\.-]+@[\w\.-]+"
        match = re.search(email_regex, html)
        email = match.group(0) if match else None
    except (NoSuchElementException, TimeoutException):
        email = None

    # Finding name
    try:
        element = WebDriverWait(driver, 2).until(
            EC.presence_of_element_located((By.XPATH, "//h1[@class='x1heor9g x1qlqyl8 x1pd3egz x1a2a7pz']"))
        )
        name = element.text
    except (NoSuchElementException, TimeoutException):
        name = None

    return email, name


lock = Lock()
processed_data = set()

def process_url(url):
    global urls  # to make changes to the list available to all threads
    driver = drivers.pop()
    link = get_link_from_page(driver, url)
    if link is not None:
        print(f"Found link: {link}")
        with lock:
            if link in processed_links:
                print("Link already processed. Skipping...")
                drivers.append(driver)
                return
            processed_links.add(link)
        driver.get(link)
        time.sleep(0.5)
        email, name = find_email_and_name(driver)
        if email:  # check if email is not None
            data = f"{email}|{name}\n"
            with lock:
                if data not in processed_data:
                    processed_data.add(data)
                    with open("profiles.txt", "a", encoding="utf-8") as file:
                        file.write(data)
                    with open("processed_links.txt", "a", encoding="utf-8") as file:
                        file.write(link + "\n")
        else:
            print("No email found for the link.")
    else:
        print("No link found. Moving to next URL.")
    drivers.append(driver)

# Load previously processed links
try:
    with open("processed_links.txt", "r", encoding="utf-8") as file:
        processed_links = set(file.read().splitlines())
except FileNotFoundError:
    processed_links = set()

pool = ThreadPool(5)
with open('ad_links.txt', 'r') as file:
    urls = [line.strip().split(',')[0] for line in file if line.strip() not in processed_links]

results = pool.map(process_url, urls)

for driver in drivers:
    driver.quit()
