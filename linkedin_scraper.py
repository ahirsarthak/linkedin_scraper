from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv
import time

connection_id = 'ACofffAABBi-8QBc6YcUHSrCoAnz1VY772XAxuB4mw'
# Correct usage of format placeholders
linkedin_search_url = 'https://www.linkedin.com/search/results/people/?connectionOf=["{}"]&origin=FACETED_SEARCH&page={}'

options = Options()
options.add_argument("--start-maximized")
driver = webdriver.Chrome(options=options)

# Step 1: Go to login page
driver.get('https://www.linkedin.com/login')

# Step 2: Wait for manual login
print("🔑 Please login manually in the browser window...")
try:
    WebDriverWait(driver, 300).until(
        EC.presence_of_element_located((By.ID, 'global-nav-search'))
    )
    print("Login successful! Proceeding with scraping...")
except Exception:
    print("Login not detected. Exiting.")
    driver.quit()
    exit()

# Step 3: Open CSV
csv_file = open('linkedin_connections_cleaned.csv', mode='w', newline='', encoding='utf-8-sig')
csv_writer = csv.writer(csv_file)
csv_writer.writerow(['Page', 'Name', 'Profile URL', 'Title', 'Location', 'Connection Degree'])

# Step 4: Loop through pages
for page in range(1, 101):  # Adjust the range as needed
    driver.get(linkedin_search_url.format(connection_id, page))
    print(f"Processing page {page}...")
    try:
        # Explicit wait for ul to be present and fully loaded
        ul_element = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, '//ul[@role="list"]'))
        )
        time.sleep(2)  # Additional wait for all li elements to render

        # Grab all li elements directly
        cards = ul_element.find_elements(By.TAG_NAME, 'li')
        print(f"Found {len(cards)} profiles on page {page}")

        for card in cards:
            try:
                # Name
                try:
                    name = card.find_element(By.XPATH, './/a[contains(@href,"/in/")]/span').text.strip()
                except:
                    name = ''

                # Profile URL
                try:
                    profile_url = card.find_element(By.XPATH, './/a[contains(@href,"/in/")]').get_attribute('href').split('?')[0]
                except:
                    profile_url = ''

                # Title / Description
                try:
                    title = card.find_element(By.XPATH, './/div[contains(@class,"t-black") and contains(@class,"t-normal")]').text.strip()
                except:
                    title = ''

                # Location (it is usually the last t-14 t-normal)
                try:
                    location = card.find_element(By.XPATH, './/div[contains(@class,"t-14") and contains(@class,"t-normal")][last()]').text.strip()
                except:
                    location = ''

                # Degree Connection (2nd, 3rd, etc.)
                try:
                    degree = card.find_element(By.XPATH, './/span[contains(@class,"entity-result__badge-text")]').text.strip()
                except:
                    degree = ''

                print(f"{page} | {name} | {profile_url} | {title} | {location} | {degree}")
                csv_writer.writerow([page, name, profile_url, title, location, degree])

            except Exception as e:
                print(f"Error extracting profile on page {page}: {e}")
                continue

    except Exception as e:
        print(f"Error processing page {page}: {e}")
        continue

# Step 5: Cleanup
csv_file.close()
driver.quit()
print("All done! Data saved to linkedin_connections_cleaned.csv")
