import os
import zipfile

import undetected_chromedriver as uc
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
# from fake_useragent import UserAgent
from webdriver_manager.chrome import ChromeDriverManager
# import undetected_chromedriver as uc


WEB_DRIVER_WAIT_TIMEOUT = 10


def _driver_wrapper(f):
    def wrapper(*args, **kwargs):
        driver: webdriver.Chrome = f(*args, **kwargs)

        driver.maximize_window()
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})") 

        return driver
    
    return wrapper


def _get_chrome_options():
    chrome_options = uc.ChromeOptions()
    # ua = UserAgent()

    chrome_options.add_argument("--user-data-dir=/home/asyncxeno/Dev/review-monitoring/user_data_dir")
    chrome_options.add_argument("--profile-directory=Default")
    # chrome_options.add_argument('--remote-debugging-port=9222')

    # chrome_options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Safari/605.1.15')
    # chrome_options.add_argument("--disable-blink-features=AutomationControlled") 
    # chrome_options.add_argument("--disable-infobars")
    # chrome_options.add_argument("--disable-save-password-bubble")

    # chrome_options.add_argument('--remote-debugging-port=9222') 
    # chrome_options.add_argument("--headless=new")

    # chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"]) 
    # chrome_options.add_experimental_option("useAutomationExtension", False) 

    # chrome_options.add_experimental_option( "prefs",{'profile.managed_default_content_settings.javascript': 2})
    # chrome_options.add_argument('--headless=new')

    return chrome_options


@_driver_wrapper
def get_chromedriver_without_proxy() -> webdriver.Chrome:
    chrome_options = _get_chrome_options()
    driver = uc.Chrome(options=chrome_options, driver_executable_path=ChromeDriverManager().install())
    return driver


@_driver_wrapper
def get_chromedriver_with_proxy(host: str, port: str, user: str, password: str):
    manifest_json = """
    {
        "version": "1.0.0",
        "manifest_version": 2,
        "name": "Chrome Proxy",
        "permissions": [
            "proxy",
            "tabs",
            "unlimitedStorage",
            "storage",
            "<all_urls>",
            "webRequest",
            "webRequestBlocking"
        ],
        "background": {
            "scripts": ["background.js"]
        },
        "minimum_chrome_version":"22.0.0"
    }
    """

    background_js = """
    var config = {
            mode: "fixed_servers",
            rules: {
            singleProxy: {
                scheme: "http",
                host: "%s",
                port: parseInt(%s)
            },
            bypassList: ["localhost"]
            }
        };

    chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

    function callbackFn(details) {
        return {
            authCredentials: {
                username: "%s",
                password: "%s"
            }
        };
    }

    chrome.webRequest.onAuthRequired.addListener(
                callbackFn,
                {urls: ["<all_urls>"]},
                ['blocking']
    );
    """ % (host, port, user, password)

    chrome_options = _get_chrome_options()

    pluginfile = 'proxy_auth_plugin'

    if (not os.path.exists(pluginfile)):
        os.mkdir(pluginfile)

    with open(f'{pluginfile}/manifest.json', 'w') as f:
        f.write(manifest_json)
    
    with open(f'{pluginfile}/background.js', 'w') as f:
        f.write(background_js)

    # with zipfile.ZipFile(pluginfile, 'w') as zp:
    #     zp.writestr('manifest.json', manifest_json)
    #     zp.writestr('background.js', background_js)

    chrome_options.add_argument(f'--load-extension={pluginfile}')

    # chrome_options.add_extension(pluginfile)

    driver = webdriver.Chrome(options=chrome_options)

    return driver
