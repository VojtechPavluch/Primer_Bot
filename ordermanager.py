from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.webdriver import Service
from selenium.webdriver.support.ui import Select
import time
import json
from resource import resource_path

PATH = "./driver/chromedriver.exe"
EASTPORT_URL = "https://www.eastport.cz/cz/oligo/"


class OrderManager:

    def __init__(self, credentials):
        options = webdriver.ChromeOptions()
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--headless')
        options.add_argument('--start-maximized')
        self.driver = webdriver.Chrome(service=Service(resource_path(PATH)), options=options)
        self.credentials = credentials

    def order_primers(self):
        """Creates an order at 'www.eastport.cz' using sequences from 'order.json' file"""
        self.driver.get(EASTPORT_URL)
        time.sleep(1)

        cookie_btn = self.driver.find_element(By.XPATH, '//*[@id="cookieBar"]/div[1]/div/div/div')
        cookie_btn.click()
        try:
            with open("order.json") as file:
                data = json.load(file)
                for item in data:
                    oligo_btn = self.driver.find_element(By.XPATH,
                                                         '//*[@id="snippet-oligoForm-oligoType"]/div/div/table/tbody/tr[1]/td[1]/span/i')
                    oligo_btn.click()
                    time.sleep(1)

                    label_entry = self.driver.find_element(By.ID, 'name')
                    sequence_entry = self.driver.find_element(By.ID, 'sequence')
                    scale = Select(self.driver.find_element(By.XPATH, '//*[@id="scale"]'))
                    pur = Select(self.driver.find_element(By.XPATH, '//*[@id="purification"]'))
                    doc = Select(self.driver.find_element(By.XPATH, '//*[@id="documentation"]'))
                    cond = Select(self.driver.find_element(By.XPATH, '//*[@id="shipping_condition"]'))
                    save_btn = self.driver.find_element(By.XPATH,
                                                        '//*[@id="snippet-oligoForm-oligoSpecification"]/div/div[10]/button')

                    label_entry.send_keys(item['label'])
                    sequence_entry.send_keys(item['sequence'])
                    scale.select_by_value('0,02 µmol')
                    pur.select_by_value('Desalted')
                    doc.select_by_value('MassCheck')
                    cond.select_by_value('dry')
                    save_btn.click()
                    time.sleep(1)
                rec_btn = self.driver.find_element(By.XPATH, '//*[@id="summary-tab"]')
                rec_btn.click()
                time.sleep(1)
                log_btn = self.driver.find_element(By.XPATH, '//*[@id="snippet--orders"]/div[3]/a[2]')
                log_btn.click()
                time.sleep(1)

                email_entry = self.driver.find_element(By.XPATH, '//*[@id="frm-eshopUserPanel-signInForm-username"]')
                email_entry.send_keys(self.credentials['email'])
                password_entry = self.driver.find_element(By.XPATH, '//*[@id="frm-eshopUserPanel-signInForm-password"]')
                password_entry.send_keys(self.credentials['password'])
                log_in = self.driver.find_element(By.XPATH, '//*[@id="frm-eshopUserPanel-signInForm"]/div/div[4]/button')
                log_in.click()
        except FileNotFoundError:
            print("Orders.json file not found.")


