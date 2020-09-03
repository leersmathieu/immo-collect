import selenium
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import requests
import lxml

import time
import re


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
        #TODO Take info
        #TODO  save as one file
# TODO concat files

appart_links = []
house_links = []

property_type = ["Appartment", "House"]
avendretext = '.+( à vendre)'

for page_number in range (1,2):

    ######################################
    #     Get the urls of each pages     #
    ######################################
    url_appart_search = "{}fr/recherche/appartement/a-vendre?countries=BE&isALifeAnnuitySale=false&page={}&orderBy=relevance".format(base_url, page_number)
    url_house_search = "{}fr/recherche/maison/a-vendre?countries=BE&isALifeAnnuitySale=false&page={}&orderBy=relevance".format(base_url, page_number)
    
    driver = webdriver.Firefox()
    driver.implicitly_wait(10)
    driver.get(url_appart_search)

    # check existence of the page
    assert "Immoweb" in driver.title

    # take away the popup
    try:
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'uc-btn-accept-banner'))
        )
        if element is not None:
            element.click()
            print("button clicked")
    except Exception as e:
        print(e)

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

        alone = True    # == pas un lot
        property_subtype = driver.find_element_by_css_selector("h1.classified__title")
        property_subtype = property_subtype.text

        if alone and re.match(avendretext, property_subtype):
            property_subtype = property_subtype[:-9]


        print(postal_code.text)
        print(city.text)
        print(property_type[0])
        print(property_subtype)
        driver.close()
        break


        ######################################
        #    Save the infos of each pages    #
        ######################################



######################################
#         Concat all the csv         #
######################################

