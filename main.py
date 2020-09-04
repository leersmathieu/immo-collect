# -*- coding: utf-8 -*-
import glob
import os
import time
import re
import pandas as pd

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup

from function import *

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
    
    donnees = []

    for url in collected_links:
        (appart_links if current_search_id == 0 else house_links).append(url)
        url = "https://www.immoweb.be/fr/annonce/bien-exceptionnel/a-vendre/dolembreux/4140/8721950?searchId=5f524465d696c"
        driver.get(url)
        soup = BeautifulSoup(driver.page_source, "lxml")

        # cherche le subtype dans "tous les biens" et skip si pas vide 
        # (les différents éléments des lots sont pris séparément)
        if get_bool_presence("h2", "text-block__title", "Tous les biens", soup):
            continue


        #####################
        #   Instanciations  #
        #####################

        # Base
        price = None
        vente_publique = get_bool_presence("h2", "text-block__title", "Vente publique", soup)
        rapport = get_bool_presence("th", "classified-table__header", "Immeuble de rapport", soup)
        bien_neuf = get_bool_presence("span", "flag-list__text", "Nouvelle construction", soup)
        postal_code = None
        city = None
        property_subtype = None
        

        # Général
        facade = None
        etat_batiment = None

        # Intérieur
        area = None
        chamber = None
        cuisine_equipe = None
        feu_ouvert = False
        meuble = False

        # Extérieur
        jardin = False
        surface_jardin = None
        terrasse = False
        surface_terrasse = None
        surface_terrain = None

        # Installations
        piscine = False

        # Urbanisme
        surface_constructible = None



        #####################
        #   Informations    #
        #####################

        # Base
        postal_code = driver.find_element_by_css_selector("span.classified__information--address-row > span")
        city = driver.find_element_by_css_selector("span.classified__information--address-row > span:nth-last-child(1)")

        property_subtype = driver.find_element_by_css_selector("h1.classified__title")
        property_subtype = property_subtype.text

        if re.match(avendretext, property_subtype):
            property_subtype = property_subtype[:-9]

        price = soup.find("p", attrs={"class": "classified__price"}).find("span").find("span").text
        price = price.replace("€", "").strip()


        accordion = soup.find_all('div', {"class": "accordion accordion--section"})

        for elem in accordion:
            entete = elem.find("h2").text

            # Général
            if entete == "Général":
                lines = elem.find_all("div", {"class": "accordion__content"})
                for line in lines:
                    trs = line.find_all("tr")
                    for tr in trs:
                        th = tr.find("th").text.strip()

                        if th.startswith("Façades"):
                            facade = int(tr.find("td").text.strip())

                        elif th.startswith("État du bâtiment"):
                            etat_batiment = tr.find("td").text.strip()

            # Intérieur
            elif entete == "Intérieur":
                lines = elem.find_all("div", {"class": "accordion__content"})
                for line in lines:
                    trs = line.find_all("tr")
                    for tr in trs:
                        th = tr.find("th").text.strip()

                        if th.startswith("Surface habitable"):
                            area = tr.find("td").text.split()
                            area = int(area[0])

                        elif th.startswith("Chambres"):
                            chamber = int(tr.find("td").text.strip())

                        elif th.startswith("Feu ouvert"):
                            feu_ouvert = True

                        elif th.startswith("Type de cuisine"):
                            cuisine_equipe = tr.find("td").text.strip()

                        elif th.startswith("Meublé"):
                            meuble = True

            # Extérieur
            elif entete == "Extérieur":
                lines = elem.find_all("div", {"class": "accordion__content"})
                for line in lines:
                    trs = line.find_all("tr")
                    for tr in trs:
                        th = tr.find("th").text.strip()

                        if th.startswith("Surface du jardin"):
                            surface_jardin = tr.find("td").text.split()
                            surface_jardin = int(surface_jardin[0])
                            if surface_jardin > 0:
                                jardin = True
                        elif th.startswith("Jardin"):
                            jardin = True

                        elif th.startswith("Surface de la terrasse"):
                            surface_terrasse = tr.find("td").text.split()
                            surface_terrasse = int(surface_terrasse[0])
                            if surface_terrasse > 0:
                                terrasse = True
                        elif th.startswith("Terrasse"):
                            terrasse = True

                        elif th.startswith("Surface du terrain"):
                            surface_terrain = tr.find("td").text.split()
                            surface_terrain = int(surface_terrain[0])

            # Installations
            elif entete == "Installations":
                lines = elem.find_all("div", {"class": "accordion__content"})
                for line in lines:
                    trs = line.find_all("tr")
                    for tr in trs:
                        th = tr.find("th").text.strip()

                        if th.startswith("Piscine"):
                            piscine = True

            # Urbanisme
            elif entete == "Urbanisme":
                lines = elem.find_all("div", {"class": "accordion__content"})
                for line in lines:
                    trs = line.find_all("tr")
                    for tr in trs:
                        th = tr.find("th").text.strip()

                        if th.startswith("Surface constructible"):
                            surface_constructible = tr.find("td").text.split()
                            surface_constructible = int(surface_constructible[0])


        for _ in range(1, 2):
            print("Postal Code: {}".format(postal_code.text))
            print("City: {}".format(city.text))
            print("Type of property: {}".format(property_type[current_search_id]))
            print("Property Subtype: {}".format(property_subtype))
            print("Price: {} €".format(price))
            # TYPE OF SALES
            print("Vente publique ?", vente_publique)
            print("Immeuble de rapport ?", rapport)
            print("Bien neuf ?", bien_neuf)
            ################
            print("Number of rooms:", chamber)
            print("Area:", area)

            print("Fully Equipped kitchen:", cuisine_equipe)
            print("Furnished:", meuble)
            print("Open fire:", feu_ouvert)
            print("Terrace:", terrasse)
            print("Superficie Terrasse:", surface_terrasse)
            print("Garden:", jardin)
            print("Garden Area:", surface_jardin)
            print("Surface of the land:", surface_terrain)
            print("Surface area of the plot of land:", surface_constructible)
            print("Number of facades:", facade)
            print("Swimming pool:", piscine)
            print("State of the building:", etat_batiment)


        donnees = {
            
        }
        # TODO remove me (intend to break the loop for current tests)
        break
        


    ######################################
    #    Save the infos of each pages    #
    ######################################

    # Sauver avec panda => 1 csv : 30 entrées


driver.close()

######################################
#         Concat all the csv         #
######################################

# all_files = glob.glob("./immo-data/*.csv")
# concat_all_CSV(all_files)

