from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

# Set up Chrome options
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

# Initialize the Chrome driver
driver = webdriver.Chrome(options=chrome_options)

# Open the URL
url = "https://apkcombo.com/vi/youtube/com.google.android.youtube/download/phone-19.16.39-apk"
driver.get(url)

# Wait for the page to load and locate the download button by XPath
try:
    wait = WebDriverWait(driver, 15)
    # Replace with the correct XPath for the APK download button
    apk_download_xpath = "//a[@href='https://download.apkcombo.com/com.google.android.youtube/YouTube_19.16.39_apkcombo.com.apk']"
    download_button = wait.until(EC.element_to_be_clickable((By.XPATH, apk_download_xpath)))
    
    # Scroll to the element and click it
    actions = ActionChains(driver)
    actions.move_to_element(download_button).perform()
    download_button.click()

    print("Download button clicked successfully!")

    # Optional: Check the URL
    current_url = driver.current_url
    print(f"Current URL: {current_url}")

except Exception as e:
    print(f"An error occurred: {e}")

# Close the browser
driver.quit()
