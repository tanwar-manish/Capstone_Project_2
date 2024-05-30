import scrapy
from scrapy.http import HtmlResponse
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import csv
import time

class MyspiderSpider(scrapy.Spider):
    name = 'myspider'
    allowed_domains = ['myntra.com']

    def __init__(self, *args, **kwargs):
        super(MyspiderSpider, self).__init__(*args, **kwargs)
        self.data = []  
        self.page_number = 1  
        self.max_pages = 5  

    def start_requests(self):
        url = "https://www.myntra.com/men-tshirts"

        options = Options()
        options.add_argument('--disable-gpu')
        options.add_argument("start-maximized")
        options.add_argument("--lang=en")
        # options.add_argument('--headless')

        try:
            self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
            self.driver.get(url)
            self.parse_page()
        except Exception as e:
            self.logger.error(f"Error initializing ChromeDriver: {e}")

    def parse_page(self):
        try:
            while self.page_number <= self.max_pages:
                # Explicitly wait (page loaded completely)
                wait = WebDriverWait(self.driver, 20)
                wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="desktopSearchResults"]/div[2]/section/ul/li[1]/a/div[2]/h4[1]')))

                # Get page source
                page_source = self.driver.page_source

                #create response (scrapy response)
                response = HtmlResponse(url=self.driver.current_url, body=page_source, encoding='utf-8')
                self.parse(response)

                # Pagination logic here 
                next_button = self.driver.find_elements(By.XPATH, '//*[@class="pagination-next"]')
                if next_button:
                    next_button[0].click()
                    self.page_number += 1
                    time.sleep(5)  
                else:
                    break

            self.driver.quit()
            self.save_data()
        except Exception as e:
            self.logger.error(f"Error during pagination: {e}")
            self.driver.quit()
            self.save_data()

    def parse(self, response):
        products = response.xpath('//ul[@class="results-base"]/li')
        for product in products:
            try:
                name = product.xpath('.//a/div[2]/h4[1]/text()').get()
                brand_name = product.xpath('.//a/div[2]/h3/text()').get()
                full_price_text = product.xpath('.//a/div[2]/div/span[1]/span/text()').getall()
                price = full_price_text[1] if len(full_price_text) > 1 else None
                rating = product.xpath('.//div[2]/span[1]/text()').get()
                item = {
                    'name': name,
                    'price': price,
                    'brand': brand_name,
                    'rating': rating
                }
                self.data.append(item)
            except Exception as e:
                self.logger.error(f"Error parsing product data: {e}")

    def save_data(self):
        if self.data:
            keys = self.data[0].keys()
            with open('myntra_data.csv', 'w', newline='') as output_file:
                dict_writer = csv.DictWriter(output_file, fieldnames=keys)
                dict_writer.writeheader()
                dict_writer.writerows(self.data)

    def close(self, reason):
        self.save_data()