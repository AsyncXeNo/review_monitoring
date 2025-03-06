import time
from datetime import datetime, timedelta

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
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

        try:
            filter_selection = driver.find_element(By.ID, 'reviews-filter-info-segment').get_attribute('innerText').strip()
        except Exception:
            filter_selection = 'ALL'

        if i == 1:
            filter_selection = 'ALL'

        # print(f'original: {filter_selection}')

        select_element = WebDriverWait(driver, 5).until(
            EC.visibility_of_element_located(
                (By.ID, 'star-count-dropdown')
            )
        )
        
        # select_element = driver.find_element(By.ID, 'star-count-dropdown')
        if i == 1:
            time.sleep(1.5)
        else:
            time.sleep(0.3)
        
        select = Select(select_element)

        options = select_element.find_element(By.TAG_NAME, 'optgroup').find_elements(By.TAG_NAME, 'option')
        
        # time.sleep(1)
        
        # dropdown = WebDriverWait(driver, 5).until(
        #     EC.element_to_be_clickable(
        #         (By.ID, 'a-autoid-5')
        #     )
        # )

        # time.sleep(1)

        # dropdown.click()

        select.select_by_value(options[i].get_attribute('value'))

        # listbox_items = WebDriverWait(driver, 5).until(
        #     EC.visibility_of_all_elements_located(
        #         (By.CSS_SELECTOR, "ul[role='listbox'] li")
        #     )
        # )
        
        # WebDriverWait(driver, 5).until(
        #     EC.element_to_be_clickable(
        #         listbox_items[i]
        #     )
        # )

        # time.sleep(0.2)
        
        # listbox_items[i].click()

        loop_start = datetime.now()

        while True:
            try:
                new_filter_selection = driver.find_element(By.ID, 'reviews-filter-info-segment').get_attribute('innerText').strip()
            except:
                continue
            if filter_selection == new_filter_selection:
                difference = abs(datetime.now() - loop_start)
                if difference > timedelta(seconds=10):
                    select_element = WebDriverWait(driver, 5).until(
                        EC.visibility_of_element_located(
                            (By.ID, 'star-count-dropdown')
                        )
                    )
                    select = Select(select_element)
                    options = select_element.find_element(By.TAG_NAME, 'optgroup').find_elements(By.TAG_NAME, 'option')
                    select.select_by_value(options[i].get_attribute('value'))
                    continue

                if difference > timedelta(seconds=60):
                    raise ProductUnavailable()
                continue
            else:
                break

        time.sleep(0.2)

        filter_info_section = driver.find_elements(By.ID, 'filter-info-section')[-1]
        rating_info = filter_info_section.find_elements(By.TAG_NAME, 'div')[1].get_attribute('innerText').strip()

        reviews_info[6 - i] = rating_info

    return reviews_info
    