import time
from datetime import datetime, timedelta
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import threading
import os
import json
import pandas as pd



def read_city_names():
    # TODO: Extract City Names List
    file_path = "city_names_germany.txt"
    city_list = []
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            city_list.append(line.strip())
    return city_list

def scrape_google_search_results(city):
    print(f"Current City: {city}")

    # TODO: Execute Google Search with query unabhängiger Optiker + City in loop
    search_query = f"unabhängiger Optiker {city}"
    options = webdriver.ChromeOptions()
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    driver = webdriver.Chrome(options=options)
    driver.get(f"https://www.google.com/maps/search/unabhängiger+Optiker+{city}?hl=de&entry=ttu")
    # driver.get("https://www.google.com/maps")
    # search_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "q")))
    # search_input.send_keys(search_query)
    # search_input.send_keys(Keys.RETURN)
    # time.sleep(2)

    # TODO: Handle if no results are found
    scrollable_element = driver.find_element(By.XPATH, '//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[1]/div[1]')
    end_of_results_text = "Das Ende der Liste ist erreicht."

    all_cards_in_page = []
    scraped_data_json = []

    # TODO: Handle one result (no cards)
    while len(all_cards_in_page) == 0:

        # TODO: Scroll Down till no more results are found
        if end_of_results_text not in driver.page_source:
            ActionChains(driver).move_to_element(scrollable_element).send_keys([Keys.ARROW_DOWN] * 100).perform()
        else:
            time.sleep(1)
            print("Reached the end of the list,start scraping")
            driver.set_window_size(1200, 800)
            # driver.refresh()

            # TODO: Get all cards by class/XPATH
            all_cards_in_page = driver.find_elements(By.XPATH, '//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[1]/div[1]')
            print(f"found {len(all_cards_in_page)} cards in {city} page")

            # TODO: Loop through the found cards and click on each one
            for card in all_cards_in_page:
                ActionChains(driver).move_to_element(scrollable_element).send_keys([Keys.ARROW_DOWN] * 10).perform()
                card.click()
                time.sleep(2)
                # TODO: From the popup, scrape all information Name, Review amount, Review number, Address, Phone number and website
                optiker_name = driver.find_element(By.CSS_SELECTOR, 'h1.DUwDvf.lfPIob').text

                review_array = driver.find_elements(By.CSS_SELECTOR, 'div.F7nice span')
                print(f"review {review_array}")
                if len(review_array) > 0:
                    review_count = review_array[0].find_element(By.CSS_SELECTOR, 'span').text
                    review_number = review_array[1].findNext('span').findNext('span').text
                else:
                    review_count = 0
                    review_number = 0

                address = driver.find_element(By.XPATH, '//*[@id="QA0Szd"]/div/div/div[1]/div[3]/div/div[1]/div/div/div[2]/div[9]/div[3]/button/div/div[2]').text
                phone_number = driver.find_element(By.XPATH, '//*[@id="QA0Szd"]/div/div/div[1]/div[3]/div/div[1]/div/div/div[2]/div[9]/div[8]/button/div/div[2]/div[1]').text
                website = driver.find_element(By.XPATH, '//*[@id="QA0Szd"]/div/div/div[1]/div[3]/div/div[1]/div/div/div[2]/div[9]/div[6]/a/div/div[2]/div[1]').text

                scraped_data_json.append({
                    "city": city,
                    "name": optiker_name,
                    "review_count": review_count,
                    "review_number": review_number,
                    "address": address,
                    "phone_number": phone_number,
                    "website": website
                })
                print(f"final json {scraped_data_json}")
            # TODO: Save in excel

    # except:
    #     print(f"City {city} has no unabhängiger")
    time.sleep(5)
    driver.quit()

city_list = ["brelin", "Ahnsen"]
if len(city_list) > 0:
    thread_list = list()
    for city in city_list:
        t = threading.Thread(name='Test {}'.format(city), target=scrape_google_search_results(city))
        t.start()
        time.sleep(1)
        thread_list.append(t)

    for thread in thread_list:
        thread.join()
