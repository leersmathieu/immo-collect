# -*- coding: utf-8 -*-
import glob
import os
import time

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup

import re
import pandas as pd

base_url = "https://www.immoweb.be/"

# TODO
# 2 searches with Selenium :
#       - House
#       - Apart
# /!\ without life sales

######################################
#  Get the urls of the search pages  #
######################################

"""
# Aparts
    # DONE list of link by pages
    # WIP Take info
    # TODO save as one file
    # TODO Houses
    # TODO list of link by pages
    # TODO Take info
    # TODO  save as one file
    # TODO concat files
"""

appart_links = []
house_links = []

property_type = ["Appartement", "Maison"]
avendretext = re.compile('.+( à vendre)')

# make sure the path is created for csv
if not os.path.exists("immo-data"):
    os.mkdir("immo-data")

######################################
#     Get the urls of each page      #
######################################
url_appart_search = base_url + "fr/recherche/appartement/a-vendre?countries=BE&isALifeAnnuitySale=false&page={}&orderBy=relevance"
url_house_search = base_url + "fr/recherche/maison/a-vendre?countries=BE&isALifeAnnuitySale=false&page={}&orderBy=relevance"

driver = webdriver.Firefox()
driver.implicitly_wait(10)
driver.get(url_appart_search.format(1))

# check existence of the page
assert "Immoweb" in driver.title

# take away the popup (only once)
try:
    element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, 'uc-btn-accept-banner'))
    )
    if element is not None:
        element.click()
        print("button clicked")
except Exception as e:
    print(e)
# current search between 'appartement' and 'maison'
current_search_id = 0
current_url = url_appart_search if current_search_id == 0 else url_house_search
# max pages to process
nb_pages = 1  # should be 333
for page_number in range(nb_pages):
    driver.get(current_url.format(page_number))
    time.sleep(4)
    # take all the links
    soup = BeautifulSoup(driver.page_source, "lxml")
    intermediate_links = soup.find_all("a", {"class": "card__title-link"})
    collected_links = [link.get("href") for link in intermediate_links]

    ######################################
    #    Get the infos of each pages     #
    ######################################

    for url in collected_links:
        (appart_links if current_search_id == 0 else house_links).append(url)
        driver.get(url)
        soup = BeautifulSoup(driver.page_source, "lxml")

        # cherche le subtype dans "tous les biens" et skip si pas vide
        try:
            tous_les_biens = soup.find_all("h2", attrs={"class": "text-block__title"})
            if any("Tous les biens" == bien.text.strip() for bien in tous_les_biens):
                continue
        except AttributeError as e:
            print(e)
            pass

        postal_code = driver.find_element_by_css_selector("span.classified__information--address-row > span")
        city = driver.find_element_by_css_selector("span.classified__information--address-row > span + span + span")

        property_subtype = driver.find_element_by_css_selector("h1.classified__title")
        property_subtype = property_subtype.text

        price = soup.find("p", attrs={"class": "classified__price"}).find("span").find("span").text.replace(" €", "")

        if re.match(avendretext, property_subtype):
            property_subtype = property_subtype[:-9]

        print("Postal Code: {}".format(postal_code.text))
        print("City: {}".format(city.text))
        print("Type of property: {}".format(property_type[current_search_id]))
        print("Property Subtype: {}".format(property_subtype))
        print("Price: {}".format(price))

        print("Type of sale: TODO")
        print("Number of rooms: TODO")
        print("Area: TODO")
        print("Fully Equipped kitchen: TODO")
        print("Furnished: TODO")
        print("Open fire: TODO")
        print("Terrace: TODO")
        print("Garden Area: TODO")  # > 0
        print("Surface of the land: TODO")
        print("Surface area of the plot of land: TODO")
        print("Number of facades: TODO")
        print("Swimming pool: TODO")
        print("State of the building: TODO")  # new, to be renovated...

        # TODO remove me (intend to break the loop for current tests)
        break

    ######################################
    #    Save the infos of each pages    #
    ######################################

driver.close()

######################################
#         Concat all the csv         #
######################################
def concat_all_CSV():
    all_files = glob.glob("./immo-data/*.csv")
    df = pd.concat([pd.read_csv(filename, index_col=None, header=0) for filename in all_files], axis=0, ignore_index=True)
    # saved in the current folder
    df.to_csv("immo_collect.csv")
    return df
