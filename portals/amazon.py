import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from exceptions.product import ProductUnavailable


def get_review_information(driver: webdriver.Chrome, product_link: str):
    
    driver.get(product_link)
    
    try:
        review_link = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "#histogramTable a")
            )
        )
    except Exception:
        raise ProductUnavailable(product_link)
    

    driver.execute_script("arguments[0].scrollIntoView(true);", review_link)
    time.sleep(0.2)

    review_link.click()

    reviews_info = {}

    for i in range(1, 6):
        WebDriverWait(driver, 5).until(
            EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, 'span[data-a-class="cr-filter-dropdown"]')
            )
        )[1].click()

        time.sleep(1)
        
        listbox_items = driver.find_elements(By.CSS_SELECTOR, "ul[role='listbox'] li")
        listbox_items[i].click()

        time.sleep(1)

        filter_info_section = driver.find_elements(By.ID, 'filter-info-section')[-1]
        rating_info = filter_info_section.find_elements(By.TAG_NAME, 'div')[1].get_attribute('innerText').strip()

        reviews_info[6 - i] = rating_info

    return reviews_info
    