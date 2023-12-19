from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options

# Set up Firefox options for headless mode
firefox_options = Options()
firefox_options.headless = True

driver = webdriver.Firefox(options=firefox_options)
driver.get("http://www.python.org")# Enable headless mode

assert "Python" in driver.title
elem = driver.find_element(By.NAME, "q")
print(elem)
elem.clear()
elem.send_keys("pycon")
elem.send_keys(Keys.RETURN)
assert "No results found." not in driver.page_source
driver.close()