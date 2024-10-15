from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains

# Set up Chrome options and the WebDriver
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run in headless mode (no browser UI)
service = Service('/usr/bin/chromedriver')  # Specify the path to your chromedriver
chrome_options.add_argument(
        f"user-agent=Mozilla/5.0 (Android 13; Mobile; rv:125.0) Gecko/125.0 Firefox/125.0"
)
driver = webdriver.Chrome(service=service, options=chrome_options)

# Navigate to the webpage
url = "https://apkcombo.com/vi/youtube/com.google.android.youtube/download/phone-19.16.39-apk"
driver.get(url)

# Locate the download button by its class and click on it
try:
    # Use the class name for the download button
    download_button = driver.find_element(By.CSS_SELECTOR, '.download-button')
    # Scroll into view if needed
    actions = ActionChains(driver)
    actions.move_to_element(download_button).perform()
    # Click the button
    download_button.click()
    print("Download link clicked successfully!")
except Exception as e:
    print(f"An error occurred: {e}")

# Close the browser
driver.quit()
