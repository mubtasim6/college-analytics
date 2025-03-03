from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time

# Setup Chrome options
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run browser in headless mode
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--window-size=1920x1080")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36")

# Initialize WebDriver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

# Open the webpage
url = "https://www.niche.com/colleges/university-of-the-pacific/"
driver.get(url)

# Wait for JavaScript to load content
time.sleep(5)

# Parse the page with BeautifulSoup
soup = BeautifulSoup(driver.page_source, "html.parser")

# Extract college name
college_name_tag = soup.find("h1")
college_name = college_name_tag.text.strip() if college_name_tag else "Unknown College"
print("College Name:", college_name)

# Extract niche grade
report_card = soup.find("div", {"class": "report-card"})
if report_card:
    grades = report_card.find_all("li", {"class": "ordered__list__bucket__item"})
    for grade in grades:
        label = grade.div.select('div')[0].text
        value = grade.div.select('div')[1].text.replace('grade\u00a0','')
        print(f"{label}: {value}")

# Close the Selenium browser
driver.quit()
