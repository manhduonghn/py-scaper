from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

# Set up Chrome options and WebDriver
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run in headless mode
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

service = Service('/usr/bin/chromedriver')  # Update with your chromedriver path
driver = webdriver.Chrome(service=service, options=chrome_options)

# Set an explicit wait time
wait = WebDriverWait(driver, 10)

# Navigate to the page
url = "https://apkcombo.com/vi/youtube/com.google.android.youtube/download/phone-19.16.39-apk"
driver.get(url)

try:
    # Wait for the element containing the download button to load and become clickable
    download_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '.download-button')))
    
    # Scroll into view
    actions = ActionChains(driver)
    actions.move_to_element(download_button).perform()
    
    # Click the download button
    download_button.click()
    print("Download link clicked successfully!")

    # Check if the download link redirects or triggers a file download
    current_url = driver.current_url
    print(f"After clicking, URL is: {current_url}")
    
except Exception as e:
    print(f"An error occurred: {e}")

# Close the browser
driver.quit()
