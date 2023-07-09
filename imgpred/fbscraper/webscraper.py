import os
import wget
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
import time
from imgpred.fbscraper.blob_config import get_blob_service_client, create_container
from urllib.parse import urlparse
import requests


def run_web_scraper(fbemail, fbpassword):
    # Set up Azure Blob Storage connection
    container_name = "scrapeddata"
    blob_service_client = get_blob_service_client()

    # Create the container if it doesn't exist
    # create_container(container_name)

    # Configure Chrome options for headless mode
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")  # headless mode

    # Disable browser notifications
    # chrome_options = webdriver.ChromeOptions()
    prefs = {"profile.default_content_setting_values.notifications": 2}
    chrome_options.add_experimental_option("prefs", prefs)

        # Specify the path to chromedriver.exe
    chromedriver_path = 'C:/Program Files/drivers/chromedriver.exe'

    # Initialize the webdriver
    driver = webdriver.Chrome(options=chrome_options)

    # Open the Facebook login page
    driver.get("http://www.facebook.com")

    # Target the username and password fields
    username = WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='email']")))
    password = WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='pass']")))

    # Enter username and password
    username.clear()
    username.send_keys(fbemail)
    password.clear()
    password.send_keys(fbpassword)

    # Click the login button
    button = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))).click()

    # Wait for login and page load
    time.sleep(5)

    # Scrape and save images
    images = []

    for i in ['photos', 'photos_by']:
        driver.get("https://www.facebook.com/profile.php?id=100093812979628&sk=" + i)
        time.sleep(5)

        n_scrolls = 2
        for j in range(1, n_scrolls):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(5)

            # Target all the link elements on the page
            anchors = driver.find_elements(By.TAG_NAME, 'a')
            anchors = [a.get_attribute('href') for a in anchors]
            # Narrow down all links to image links only
            anchors = [a for a in anchors if str(a).startswith("https://www.facebook.com/photo.php")]

            print(anchors)

            for a in anchors:
                driver.get(a)
                time.sleep(5)
                img = driver.find_elements(By.TAG_NAME, "img")
                images.append(img[0].get_attribute("src"))

    # Save the scraped images in Blob Storage
    for image_url in images:
        # Get the image file name from the URL
        image_file_name = os.path.basename(urlparse(image_url).path)

        # Upload the image directly to Blob Storage
        image_content = requests.get(image_url).content
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=image_file_name)
        blob_client.upload_blob(image_content, overwrite=True)

    # Close the webdriver
    driver.quit()

    return images
