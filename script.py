#!venv/bin/python3

import traceback
import copy
import json
import utils.config as _
from datetime import datetime

from loguru import logger

# from pyvirtualdisplay import Display

from utils.mail import send_output_mail, send_email, send_error_mail
from utils.sheets import get_amazon_data, save_data
from utils.selenium_utils import get_chromedriver_without_proxy
from portals.amazon import get_review_information, CAPTCHAS_SOLVED
from exceptions.product import ProductUnavailable


if __name__ == '__main__':

    logger.info('Starting script')

    send_email('Notification System <dev@kartikcodes.in>', ['dev.kartikaggarwal117@gmail.com'], 'Amazon Reviewmon Execute!', 'Amazon Reviewmon script has started execution!', [])
    
    with open('data/latest.json', 'r') as f:
        latest_review_data = json.load(f)

    latest_date = latest_review_data.get('date') or 'NA'
    today_date = datetime.today().strftime('%d-%m-%y')

    # disp = Display()
    # disp.start()

    output = []

    # Fetch data
    try:
        logger.info('Loading data')
        amazon_data = get_amazon_data()
    except Exception as e:
        logger.error(e)
        send_error_mail('Error while loading data from google sheet')

    driver = get_chromedriver_without_proxy()

    for index, entry in enumerate(amazon_data):

        ASIN = entry['ASIN']
        URL = entry['Product link']
        
        if not isinstance(ASIN, str) or ASIN.strip() == '':
            logger.warning(f'skipping amazon product, ASIN: {ASIN}')
            continue

        count = 0
        while True:
            try:
                scraped_info = get_review_information(driver, URL)
                break
            except ProductUnavailable:
                scraped_info = {5: 'NA', 4: 'NA', 3: 'NA', 2: 'NA', 1: 'NA'}
                break
            except Exception as e:
                # trace = traceback.format_exc()
                logger.error(traceback.format_exc())
                count += 1
                if count > 1:
                    scraped_info = {5: 'NA', 4: 'NA', 3: 'NA', 2: 'NA', 1: 'NA'}
                    break
                else:
                    continue

        latest_product_info = latest_review_data.get(ASIN)
        if not latest_product_info:
            latest_product_info = {"5": 'NA', "4": 'NA', "3": 'NA', "2": 'NA', "1": 'NA'}

        latest_product_info = copy.deepcopy(latest_product_info)

        new_info = {
            'ASIN': ASIN,
            'Product Link': URL,
            f'5 star ratings ({latest_date})': latest_product_info["5"],
            f'5 star ratings ({today_date})': scraped_info[5],
            f'4 star ratings ({latest_date})': latest_product_info["4"],
            f'4 star ratings ({today_date})': scraped_info[4],
            f'3 star ratings ({latest_date})': latest_product_info["3"],
            f'3 star ratings ({today_date})': scraped_info[3],
            f'2 star ratings ({latest_date})': latest_product_info["2"],
            f'2 star ratings ({today_date})': scraped_info[2],
            f'1 star ratings ({latest_date})': latest_product_info["1"],
            f'1 star ratings ({today_date})': scraped_info[1],
        }

        output.append(new_info)
        
        latest_review_data[ASIN] = {
            "1": scraped_info[1],
            "2": scraped_info[2],
            "3": scraped_info[3],
            "4": scraped_info[4],
            "5": scraped_info[5]
        }

        logger.debug(f'[{index+1}/{len(amazon_data)}] Scraped review information: {URL} {new_info}')
        

    driver.close()
    # disp.stop()
    
    logger.info('Data scraping complete, saving...')

    save_data(output)

    logger.info('Emailing data...')

    send_output_mail()

    logger.info('Updating latest info...')

    latest_review_data['date'] = today_date

    with open('data/latest.json', 'w') as f:
        json.dump(latest_review_data, f, indent=4)

    logger.info(f'Captchas solved: {CAPTCHAS_SOLVED}')
    logger.info('Script has run to completion!')