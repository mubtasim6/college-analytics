import requests
import time
from bs4 import BeautifulSoup

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',
    'Referer': 'https://www.google.com/',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1'
})

# change url to get data for each top 50 college page on Niche
url = "https://www.niche.com/colleges/yale-university/"
response = session.get(url)
print(response.status_code)
time.sleep(3.6)
webpage = response.text

# html parsing
page_soup = BeautifulSoup(webpage, "html.parser")
data = {}

# find name of college
college_name_tag = page_soup.find("h1")
if college_name_tag:
    college_name = college_name_tag.text.strip()
else:
    college_name = "Unknown College"
data[college_name] = {}

# find niche grade
report_card = page_soup.find("div", {"class": "report-card"})
data[college_name]["niche_report_card"] = {}
if report_card:
    grades = report_card.find_all("li", {"class": "ordered__list__bucket__item"})
    for grade in grades:
        grade_label = grade.div.select('div')[0].text
        grade_val = grade.div.select('div')[1].text.replace('grade\u00a0','')
        data[college_name]["niche_report_card"][grade_label] = grade_val


# 'after college' metrics
data[college_name]["after_college"] = {}
after_college = page_soup.find("section", {"id": "after"})
if after_college:
    # median earning after 6 years of college
    median_earning_6_years_tag = after_college.find("div", {"class": "profile__bucket--1"}).div.div.find("div", {
        "class": "scalar__value"})
    median_earning_6_years = median_earning_6_years_tag.span.text if median_earning_6_years_tag else ''
    data[college_name]["after_college"]["median_earning_6_years"] = median_earning_6_years

    # other after college rates
    other_after_college_rates = after_college.find("div", {"class": "profile__bucket--2"}).div.find_all(recursive=False)

    # graduation rate
    graduation_rate_tag = other_after_college_rates[0].find("div", {"class": "scalar__value"})
    graduation_rate = graduation_rate_tag.span.text if graduation_rate_tag else ''
    data[college_name]["after_college"]["graduation_rate"] = graduation_rate

    # employment rate
    employment_rate_tag = other_after_college_rates[1].find("div", {"class": "scalar__value"})
    employment_rate = employment_rate_tag.span.text if employment_rate_tag else ''
    data[college_name]["after_college"]["employment_rate"] = employment_rate

    # confidence level
    poll_after_college_rates = after_college.find("div", {"class": "profile__bucket--3"})
    if poll_after_college_rates:
        confidence_level_container = poll_after_college_rates.find("div", class_="poll__single__value")
        if confidence_level_container:
            # extract the percentage value
            confidence_level_percent = confidence_level_container.find("div",
                                                                       class_="poll__single__percent").text.strip() if confidence_level_container.find(
                "div", class_="poll__single__percent") else "Information not found"

            # extract the number of responses
            confidence_level_responses = confidence_level_container.find("span",
                                                                         class_="poll__single__responses").text.strip() if confidence_level_container.find(
                "span", class_="poll__single__responses") else "Information not found"

            # add the extracted data to the dictionary
            data[college_name]["after_college"]["confidence_level_percent"] = confidence_level_percent
            data[college_name]["after_college"]["confidence_level_responses"] = confidence_level_responses.replace('responses', "").strip()
        else:
            data[college_name]["after_college"]["confidence_level"] = "Confidence level value not found"
    else:
        data[college_name]["after_college"]["confidence_level"] = "Confidence level container not found"

import pandas as pd

# convert the collected data to a list of dictionaries, each containing all data for a college
college_data_list = []
for college_name, info in data.items():
    college_info = info.copy()  # Make a copy to avoid modifying the original data
    college_info['College name'] = college_name  # Add the college name to the dictionary
    college_data_list.append(college_info)

college_data = pd.DataFrame(college_data_list)

csv_file = 'colleges_df.csv'

# check if the CSV file already exists
try:
    df_existing = pd.read_csv(csv_file)
    df_updated = pd.concat([df_existing, college_data], ignore_index=True)
except FileNotFoundError:
    # if the file does not exist, use the new DataFrame as the updated one
    df_updated = college_data

df_updated.to_csv(csv_file, index=False)
print(df_updated)