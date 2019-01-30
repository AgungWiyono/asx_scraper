from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support import expected_conditions as EC


options = webdriver.chrome.options.Options()
options.add_argument('--headless')

driver = webdriver.Chrome(options=options)

url = 'https://www.asx.com.au/asx/share-price-research/company/'
variable = 'TLS'

# Get Initial page
driver.get(url + variable)
WebDriverWait(driver, 10).until(EC.visibility_of_element_located(
    (By.XPATH, "//a[@class='annual-report pdf-download']")))

driver.execute_script("window.stop();")
print(driver.current_url)
