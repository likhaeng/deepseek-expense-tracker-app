from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

driver = webdriver.Chrome() # Or Firefox, Edge, etc.
driver.get("https://selenium-python.readthedocs.io/waits.html") # Replace with your target URL

try:
    element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".document"))
    )
    print(f"Element found: {element.text}")
except Exception:
    print("Element not found within the specified time.")
finally:
    driver.quit()