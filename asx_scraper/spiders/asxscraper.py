# -*- coding: utf-8 -*-
import time
import csv
import json

import scrapy
from scrapy.selector import Selector
from scrapy.http.request import Request
from scrapy.crawler import CrawlerProcess
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException


class AsxscraperSpider(scrapy.Spider):
    rotate_user_agent = True
    company_codes = []
    with open('asx_scraper/urls_list_0-499.csv', 'r') as rf:
        reader = csv.reader(rf)
        for i in reader:
            company_codes.extend([i[1]])

    name = 'asxbot'
    allowed_domains = ['www.asx.com.au']
    start_urls = ["https://www.asx.com.au/asx/share-price-research/company/"+i
                  for i in company_codes]

    def __init__(self, *args, **kwargs):
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-web-security")
        options.add_argument("--allow-insecure-localhost")

        cap = DesiredCapabilities.CHROME
        cap['pageLoadStrategy'] = 'none'
        cap['acceptSslCerts'] = True
        cap['acceptInsecureCerts'] = True

        self.driver = webdriver.Chrome(desired_capabilities=cap, options=options,
                                       executable_path="/usr/lib/chromium-browser/chromedriver")
        # self.driver = webdriver.Chrome(desired_capabilities=cap,
        #                                executable_path="/usr/lib/chromium-browser/chromedriver")

        super(AsxscraperSpider, self).__init__(*args, **kwargs)

    def parse(self, response):
        url = response.request.url
        yield Request(url=url, callback=self.parse_data)

    def parse_data(self, response):
        code = response.request.url[-3:]
        wait = WebDriverWait(self.driver, 10)

        # Wait for annual reports link to be rendered
        has_annual_report = True
        self.driver.get(response.url)
        time.sleep(3)
        footer_logo = "/html/body/section[4]/footer/div[2]/div[1]"
        annual_report_xpath = "//a[@class='annual-report pdf-download']"
        try:
            WebDriverWait(self.driver, 20).until(EC.visibility_of_element_located(
                (By.XPATH, footer_logo)
            ))
        except TimeoutException:
            has_annual_report = False
        self.driver.execute_script("window.stop();")

        # Price, market_cap and dividens xpath
        last_price = ["/html[1]/body[1]/section[3]/article[1]/div[1]/div[1]\
                      /div[1]/div[4]/div[1]/div[1]/company-summary[1]/table[1]\
                      /tbody[1]/tr[1]/td[1]/span[1]/text()",
                      'last_price']
        market_cap = ["/html[1]/body[1]/section[3]/article[1]/div[1]/div[1]\
                      /div[1]/div[4]/div[1]/div[1]/company-summary[1]/table[1]\
                      /tbody[1]/tr[2]/td[1]/div[1]/span[1]/text()",
                      'market_cap']
        most_recent = ["/html/body/section[3]/article/div[1]/div/div/div[4]\
                       /div[1]/div[1]/company-summary/table/tbody/tr[3]/td[2]\
                       /table/tbody/tr[1]/td[2]/span[1]/text()",
                       'most_recent']
        ex_date = ["/html/body/section[3]/article/div[1]/div/div/div[4]\
                   /div[1]/div[1]/company-summary/table/tbody/tr[3]/td[2]\
                   /table/tbody/tr[2]/td[2]/text()",
                   'dividen_ex_date']
        pay_date = ["/html/body/section[3]/article/div[1]/div/div/div[4]\
                    /div[1]/div[1]/company-summary/table/tbody/tr[3]/td[2]\
                    /table/tbody/tr[3]/td[2]/text()",
                    'dividen_pay_date']
        frangking = ["/html/body/section[3]/article/div[1]/div/div/div[4]\
                     /div[1]/div[1]/company-summary/table/tbody/tr[3]/td[2]\
                     /table/tbody/tr[4]/td[2]/text()",
                     'frangking']

        # Scrape main page variable
        print('scrape main data')
        main_page_keys = [last_price, market_cap, most_recent,
                          ex_date, pay_date, frangking]
        hxs = Selector(text=self.driver.page_source)
        main_page_var = {}
        for key in main_page_keys:
            main_page_var[key[1]] = hxs.xpath(key[0]).extract()[0].strip()

        print('annual report scraper')
        if has_annual_report is True:
            print('scrape annual report')
            annual_report_xpath = "/html/body/section[3]/article/div[1]/div/div\
                    /div[4]/div[2]/div[1]/div[1]/div/company-research/div[2]/ul\
                    /li/a"
            annual_report_link = self.driver.find_element_by_xpath(
                                annual_report_xpath)
            annual_report_link.click()

            self.driver.switch_to_window(self.driver.window_handles[1])

            # Check if a dialog box appear
            # If appear, click agree then continue
            try:
                agree_xpath = "//input[@value='Agree and proceed']"
                WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, agree_xpath)))
                agree_link = self.driver.find_element_by_xpath(agree_xpath)
                hidden_element = self.driver.find_element_by_xpath("/html/body/div/form/input[3]")
                main_page_var['annual_report'] = "https://www.asx.com.au" \
                                                 + hidden_element.get_attribute('value')
                self.driver.close()
                self.driver.switch_to_window(self.driver.window_handles[0])
                print('Annual report scraped from agree button')
            except TimeoutException:
                WebDriverWait(self.driver, 10).until(lambda x: '.pdf'
                                                     in self.driver.current_url)
                main_page_var['annual_report'] = str(self.driver.current_url)
                self.driver.close()
                self.driver.switch_to_window(self.driver.window_handles[0])
                print('Annual report scraped from url')
        else:
            print('No annual report')
            main_page_var['annual_report'] = '-'

        # Get to statistic key tab
        self.driver.switch_to_window(self.driver.window_handles[0])
        key_statistic_xpath = "/html/body/section[3]/article/div[1]/div/div\
                                /div[3]/ul/li[2]/a"
        self.driver.find_element_by_xpath(key_statistic_xpath).click()

        # Statistic key variable section
        try:
            WebDriverWait(self.driver, 30).until(EC.presence_of_element_located(
                (By.XPATH, "//th[@colspan='7']")))
        except:
            pass
        self.driver.execute_script("window.stop();")
        hxs = Selector(text=self.driver.page_source)

        # Statistic keys day xpath
        open_var= ["/html/body/section[3]/article/div[1]/div/div/div[4]/div\
                   /div[3]/table/tbody/tr[3]/td[2]/span/text()",
                   'open']
        day_high= ["/html/body/section[3]/article/div[1]/div/div/div[4]/div\
                   /div[3]/table/tbody/tr[4]/td[2]/span/text()",
                   'day_high']
        day_low = ["/html/body/section[3]/article/div[1]/div/div/div[4]/div\
                   /div[3]/table/tbody/tr[5]/td[2]/span/text()",
                   'day_low']
        daily= ["/html/body/section[3]/article/div[1]/div/div/div[4]/div\
                /div[3]/table/tbody/tr[6]/td[2]/span/text()",
                'daily volume']
        bid= ["/html/body/section[3]/article/div[1]/div/div/div[4]/div\
              /div[3]/table/tbody/tr[7]/td[2]/span/text()",
              'Bid']
        offer= ["/html/body/section[3]/article/div[1]/div/div/div[4]/div\
                /div[3]/table/tbody/tr[8]/td[2]/span/text()",
                'Offer']
        shares_numbers= ["/html/body/section[3]/article/div[1]/div/div/div[4]\
                         /div/div[3]/table/tbody/tr[9]/td[2]/span/text()",
                         'Number of Shares']

        # Statistic keys day scraper
        day_keys = [open_var, day_high, day_low, daily, bid,
                    offer, shares_numbers]
        day_vars = {}
        for key in day_keys:
            day_vars[key[1]] = hxs.xpath(key[0]).extract()[0]


        # Statistic key year xpath
        previous_close = ["/html/body/section[3]/article/div[1]/div/div/div[4]\
                          /div/div[3]/table/tbody/tr[3]/td[4]/span/text()",
                          'Previous Close']
        week_high = ["/html/body/section[3]/article/div[1]/div/div/div[4]\
                     /div/div[3]/table/tbody/tr[4]/td[4]/span/text()",
                     'Week High']
        week_low = ["/html/body/section[3]/article/div[1]/div/div/div[4]\
                    /div/div[3]/table/tbody/tr[5]/td[4]/span/text()",
                    'Week Low']
        average_volume = ["/html/body/section[3]/article/div[1]/div/div/div\
                          [4]/div/div[3]/table/tbody/tr[6]/td[4]/span/text()",
                          'Average Volume']
        # Statistic keys day scraper
        year_keys = [previous_close, week_high, week_low, average_volume]
        year_vars = {}
        for key in year_keys:
            year_vars[key[1]] = hxs.xpath(key[0]).extract()[0]

        # Statistic keys Ratios variable
        pe = ["/html/body/section[3]/article/div[1]/div/div/div[4]/div/div[3]\
              /table/tbody/tr[3]/td[6]/span/text()",
              'pe']
        eps = ["/html/body/section[3]/article/div[1]/div/div/div[4]/div/\
               div[3]/table/tbody/tr[4]/td[6]/span/text()",
               'eps']
        annual = ["/html/body/section[3]/article/div[1]/div/div/div[4]/div\
                  /div[3]/table/tbody/tr[5]/td[6]/span/text()",
                  'annual']

        # Statistic key ratios scraper
        print('scrape ratios')
        ratios_keys = [pe, eps, annual]
        ratios_vars = {}
        for key in ratios_keys:
            ratios_vars[key[1]] = hxs.xpath(key[0]).extract()[0]

        # Announcement Section
        # Get the announcement table
        self.driver.get("https://www.asx.com.au/asx/statistics/announcements.do?by=asxCode&asxCode={}&timeframe=D&period=M6".format(code))
        WebDriverWait(self.driver, 30).until(EC.visibility_of_element_located(
            (By.XPATH, "//h2[contains(text(),'Useful Information')]")))
        self.driver.execute_script("window.stop();")
        announcement_table = self.driver.find_element_by_xpath(
                            "/html/body/section[3]/article/div[2]/div/announcement_data/table/tbody")
        rows = announcement_table.find_elements_by_tag_name('tr')

        # Iterate over rows in table
        announcement_list = []
        for row in rows:

            # Get announcement attribute
            row_data = {}
            row_data['date'], row_data['time'] = \
                    row.find_element_by_tag_name('td').text.split('\n')
            row_data['headline'] = row.find_element_by_tag_name(\
                                            'a').text.split('\n')[0]
            announcement_uri = row.find_element_by_tag_name('a')
            row_data['uri'] = "https://www.asx.com.au" \
                              + announcement_uri.get_attribute('href')

            announcement_list.append(row_data)


        # Return the result
        data = {
                   code:{
                                    'main_data': main_page_var,
                                    'statistics': {
                                                    'day': day_vars,
                                                    'year': year_vars,
                                                    'ratios': ratios_vars
                                                  },
                                    'announcements': announcement_list
                                 }
        }
        return  data


class SecondAsxScraperSpider(AsxscraperSpider):
    company_codes = []
    with open('asx_scraper/urls_list_101-200.csv', 'r') as rf:
        reader = csv.reader(rf)
        for i in reader:
            company_codes.extend([i[1]])

    name = 'asxbot_second'
    allowed_domains = ['www.asx.com.au']
    start_urls = ["https://www.asx.com.au/asx/share-price-research/company/"+i
                  for i in company_codes]

# proccess = CrawlerProcess()
# proccess.crawl(AsxscraperSpider)
# proccess.crawl(SecondAsxScraperSpider)
# proccess.start()
