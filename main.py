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


# Aparts
# DONE list of link by pages
# WIP Take info
# TODO save as one file
# TODO Houses
# TODO list of link by pages
# TODO Take info
# TODO  save as one file
# TODO concat files

appart_links = []
house_links = []

property_type = ["Appartment", "House"]
avendretext = '.+( à vendre)'

# make sure the path is created for csv
if not os.path.exists("data"):
    os.mkdir("data")

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
# max pages to process
nb_pages = 1  # should be 333
for page_number in range(nb_pages):
    driver.get(url_appart_search.format(page_number))
    time.sleep(4)
    # take all the links
    soup = BeautifulSoup(driver.page_source, "lxml")
    intermediate_links = soup.find_all("a", {"class": "card__title-link"})
    for link in intermediate_links:
        link = link.get("href")
        appart_links.append(link)

        ######################################
        #    Get the infos of each pages     #
        ######################################

    for url in appart_links:
        driver.get(url)
        soup = BeautifulSoup(driver.page_source, "lxml")

        postal_code = driver.find_element_by_css_selector("span.classified__information--address-row > span")
        city = driver.find_element_by_css_selector("span.classified__information--address-row > span + span + span")

        # TODO au lieu de regarder le titre, regarder le prix
        # si prix =+ range => lot, et chercher le subtype dans le "tous les biens", ainsi que prix
        # sauf si pas "tous les biens" => même si range, pas un lot

        alone = True  # == pas un lot
        property_subtype = driver.find_element_by_css_selector("h1.classified__title")
        property_subtype = property_subtype.text

        if alone and re.match(avendretext, property_subtype):
            property_subtype = property_subtype[:-9]

        price = soup.find("p", attrs={"class": "classified__price"}).find("span").find("span").text[:-2]

        print("Postal Code: {}".format(postal_code.text))
        print("City: {}".format(city.text))
        print("Type of property: {}".format(property_type[0]))
        print("Property Subtype: ".format(property_subtype))
        print("Price: {}".format(str(price)))

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

driver.close()

        ######################################
        #    Save the infos of each pages    #
        ######################################

######################################
#         Concat all the csv         #
######################################
def concat_all_CSV():
    all_files = glob.glob("./data/*.csv")
    df = pd.concat([pd.read_csv(filename, index_col=None, header=0) for filename in all_files], axis=0, ignore_index=True)
    # saved in the current folder
    df.to_csv("immo_collect.csv")
    return df
