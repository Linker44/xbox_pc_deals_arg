from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from prettytable import PrettyTable
import json
import os

driver = webdriver.Chrome()
options = webdriver.ChromeOptions()
# skip annoying usb log
options.add_experimental_option('excludeSwitches', ['enable-logging'])
# disable images for faster load times
prefs = {"profile.managed_default_content_settings.images": 2}

options.add_experimental_option("prefs", prefs)
service = Service(exectuable_path="chromedriver.exe")
driver = webdriver.Chrome(service=service, options=options)

table = PrettyTable()
table.field_names = ["TITLE", "ORIGINAL PRICE", "DISCOUNT PRICE", "LINK"]

url = "https://www.microsoft.com/es-ar/store/deals/games/pc"
driver.get(url)
original_window = driver.current_window_handle

card_xpath = "//div[@data-bi-ct='Product Card']"
WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located((
    By.XPATH, card_xpath)))
cards = driver.find_elements(By.XPATH, card_xpath)

for card in cards:

    title = card.get_attribute("data-bi-cn")

    # click and open hyperlink in new window
    link = card.find_element(By.XPATH, ".//a").get_attribute("href")
    escaped_link = json.dumps(link)
    driver.execute_script(f"window.open({escaped_link},'_blank');")
    WebDriverWait(driver, 10).until(EC.number_of_windows_to_be(2))
    driver.switch_to.window(driver.window_handles[-1])

    # get the pricing text
    buy_button_path = "//button[contains(@aria-label, 'Comprar')]"
    try:
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located(
            (By.XPATH, buy_button_path)))
    except:
        continue
    price_element = driver.find_element(
        By.XPATH, buy_button_path)
    price = price_element.get_attribute('aria-label')

    # Extract the original and discount prices from the text
    price_index = price.find("Precio original:")
    full_price = price[price_index:].split(";")
    original_price = full_price[0].split("$")[1]
    discount_price = "No Discount"
    if len(full_price) == 2:
        discount_price = full_price[1].split("$")[1]
    table.add_row([title, original_price, discount_price, link])

    os.system('cls' if os.name == 'nt' else 'clear')
    print(table)

    # close window and switch back to original one
    driver.close()
    driver.switch_to.window(original_window)
driver.quit()
