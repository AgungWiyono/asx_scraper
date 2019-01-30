from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException

options = Options()
options.headless = True

url = 'https://www.asx.com.au/asx/share-price-research/company/'
variable = 'TLS'
# driver = webdriver.Chrome(options=options)
driver = webdriver.Chrome()

wait = WebDriverWait(driver, 10)

# Get Initial page
driver.get(url + variable)
wait.until(EC.visibility_of_element_located((By.XPATH, "//a[@class='annual-report pdf-download']")))

driver.execute_script("window.stop();")

# Get price, market_cap, and dividends
last_price_xpath = "/html/body/section[3]/article/div[1]/div/div/div[4]/div[1]/div[1]/company-summary/table/tbody/tr[1]/td[1]/span"
market_cap_xpath = "/html/body/section[3]/article/div[1]/div/div/div[4]/div[1]/div[1]/company-summary/table/tbody/tr[2]/td[1]/div/span"
most_recent_xpath = "/html/body/section[3]/article/div[1]/div/div/div[4]/div[1]/div[1]/company-summary/table/tbody/tr[3]/td[2]/table/tbody/tr[1]/td[2]/span[1]"
ex_date_xpath = "/html/body/section[3]/article/div[1]/div/div/div[4]/div[1]/div[1]/company-summary/table/tbody/tr[3]/td[2]/table/tbody/tr[2]/td[2]"
pay_date_xpath = "/html/body/section[3]/article/div[1]/div/div/div[4]/div[1]/div[1]/company-summary/table/tbody/tr[3]/td[2]/table/tbody/tr[3]/td[2]"
frangking_xpath = "/html/body/section[3]/article/div[1]/div/div/div[4]/div[1]/div[1]/company-summary/table/tbody/tr[3]/td[2]/table/tbody/tr[4]/td[2]"

last_price = driver.find_element_by_xpath(last_price_xpath).text
market_cap= driver.find_element_by_xpath(market_cap_xpath).text
most_recent = driver.find_element_by_xpath(most_recent_xpath).text
ex_date = driver.find_element_by_xpath(ex_date_xpath).text
pay_date = driver.find_element_by_xpath(pay_date_xpath).text
frangking = driver.find_element_by_xpath(frangking_xpath).text

annual_report_xpath = "/html/body/section[3]/article/div[1]/div/div/div[4]/div[2]/div[1]/div[1]/div/company-research/div[2]/ul/li/a"
annual_report_link = driver.find_element_by_xpath(annual_report_xpath)
annual_report_link.click()

driver.switch_to_window(driver.window_handles[1])

# Check if a dialog box appear
try:
    print(driver.current_url)
    agree_xpath = "/html/body/div/form/input[2]"
    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, agree_xpath)))
    agree_link = driver.find_element_by_xpath(agree_xpath)
    agree_link.click()
finally:
    print(driver.current_url)
    wait.until(lambda x: '.pdf' in driver.current_url)
    annual_report_filename = driver.current_url
    driver.close()
    driver.switch_to_window(driver.window_handles[0])

test = [market_cap, last_price, most_recent, ex_date, pay_date,
        frangking, annual_report_filename]
for i in test:
    print(i)

# Go back to previous window and go to statistic_key tab
driver.switch_to_window(driver.window_handles[0])
key_statistic_xpath = "/html/body/section[3]/article/div[1]/div/div/div[3]/ul/li[2]/a"
driver.find_element_by_xpath(key_statistic_xpath).click()

pe = "/html/body/section[3]/article/div[1]/div/div/div[4]/div/div[3]/table/tbody/tr[3]/td[6]/span"

# Get all variable
# Day variable
open_var= ["/html/body/section[3]/article/div[1]/div/div/div[4]/div/div[3]/table/tbody/tr[3]/td[2]/span", 'open']
day_high= ["/html/body/section[3]/article/div[1]/div/div/div[4]/div/div[3]/table/tbody/tr[4]/td[2]/span", 'day_high']
day_low = ["/html/body/section[3]/article/div[1]/div/div/div[4]/div/div[3]/table/tbody/tr[5]/td[2]/span", 'day_low']
daily= ["/html/body/section[3]/article/div[1]/div/div/div[4]/div/div[3]/table/tbody/tr[6]/td[2]/span", 'daily volume']
bid= ["/html/body/section[3]/article/div[1]/div/div/div[4]/div/div[3]/table/tbody/tr[7]/td[2]/span", 'Bid']
offer= ["/html/body/section[3]/article/div[1]/div/div/div[4]/div/div[3]/table/tbody/tr[8]/td[2]/span", 'Offer']
shares_numbers= ["/html/body/section[3]/article/div[1]/div/div/div[4]/div/div[3]/table/tbody/tr[9]/td[2]/span", 'Number of Shares']
wait.until(EC.visibility_of_element_located((By.XPATH, pe)))
day_keys = [open_var, day_high, day_low, daily, bid, offer, shares_numbers]
day_vars = {}
for element in day_keys:
    day_vars[element[1]] = driver.find_element_by_xpath(element[0]).text
for key in day_vars:
    print(key + ': ' + day_vars[key])

# Year variable
previous_close = ["/html/body/section[3]/article/div[1]/div/div/div[4]/div/div[3]/table/tbody/tr[3]/td[4]/span", 'Previous Close']
week_high = ["/html/body/section[3]/article/div[1]/div/div/div[4]/div/div[3]/table/tbody/tr[4]/td[4]/span", 'Week High']
week_low = ["/html/body/section[3]/article/div[1]/div/div/div[4]/div/div[3]/table/tbody/tr[5]/td[4]/span", 'Week Low']
average_volume = ["/html/body/section[3]/article/div[1]/div/div/div[4]/div/div[3]/table/tbody/tr[6]/td[4]/span", 'Average Volume']
year_keys = [previous_close, week_high, week_low, average_volume]
year_vars = {}
for element in year_keys:
    year_vars[element[1]] = driver.find_element_by_xpath(element[0]).text

for key in year_vars:
    print(key + ': ' + year_vars[key])

# Ratios variable
pe = ["/html/body/section[3]/article/div[1]/div/div/div[4]/div/div[3]/table/tbody/tr[3]/td[6]/span", 'pe']
eps = ["/html/body/section[3]/article/div[1]/div/div/div[4]/div/div[3]/table/tbody/tr[4]/td[6]/span", 'eps']
annual = ["/html/body/section[3]/article/div[1]/div/div/div[4]/div/div[3]/table/tbody/tr[5]/td[6]/span", 'annual']
wait.until(EC.visibility_of_element_located((By.XPATH, pe[0])))
ratios_keys = [pe, eps, annual]
ratios_vars = {}
for element in ratios_keys:
    ratios_vars[element[1]] = driver.find_element_by_xpath(element[0]).text
for key in ratios_vars:
    print(key + ': ' + ratios_vars[key])

# Getting all announcements
driver.get("https://www.asx.com.au/asx/statistics/announcements.do?by=asxCode&asxCode={}&timeframe=D&period=M6".format(variable))
wait.until(EC.visibility_of_element_located((By.XPATH, "/html/body/section[3]/article/div[2]/div/h2[3]")))
driver.execute_script("window.stop();")
announcement_table = driver.find_element_by_xpath("/html/body/section[3]/article/div[2]/div/announcement_data/table/tbody")
rows = announcement_table.find_elements_by_tag_name('tr')
announcement_list = []
for row in rows:
    print('row1')
    row_data = {}
    row_data['date'], row_data['time'] = row.find_element_by_tag_name('td').text.split('\n')
    row_data['headline'] = row.find_element_by_tag_name('a').text.split('\n2')[0]
    main_handle = driver.current_window_handle

    link_href = row.find_element_by_tag_name('a')
    print(link_href.get_attribute("href"))
    link_href.click()
    while len(driver.window_handles)<2:
        driver.implicitly_wait(1)
    driver.switch_to_window(driver.window_handles[-1])
    driver.implicitly_wait(3)

    # Check if a dialog box appear
    try:
        print('searching button')
        agree_xpath = "/html/body/div/form/input[2]"
        WebDriverWait(driver, 2).until(EC.visibility_of_element_located((By.XPATH, agree_xpath)))
        agree_link = driver.find_element_by_xpath(agree_xpath)
        agree_link.click()
    except TimeoutException:
        pass
    finally:
        while '.pdf' not in driver.current_url:
            driver.implicitly_wait(1)
        row_data['headline_url'] = driver.current_url
        print(driver.current_url)
        driver.close()
        driver.switch_to_window(driver.window_handles[0])
        print('fo back')
    announcement_list.append(row_data)

print(announcement_list)
