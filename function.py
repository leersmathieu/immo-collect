# init file
import glob
import os
from typing import List, Dict, Union

import pandas as pd
import re

from pandas import DataFrame
from selenium.common.exceptions import NoSuchElementException
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

avendretext = re.compile('.+( à vendre)')
search_for_postal_code = re.compile("/(?P<postal_code>[0-9]+)/[0-9]+\?searchId=")
property_type = ["Appartement", "Maison"]

# make sure the path is created for csv
if not os.path.exists("immo-data"):
    os.mkdir("immo-data")

######################################
#     Get the urls of each page      #
######################################
base_url = "https://www.immoweb.be/"
url_appart_search = base_url + "fr/recherche/appartement/a-vendre?countries=BE&isALifeAnnuitySale=false&page={}&orderBy=relevance"
url_house_search = base_url + "fr/recherche/maison/a-vendre?countries=BE&isALifeAnnuitySale=false&page={}&orderBy=relevance"


def get_bool_presence(place: str, attributs_class: str, text_to_search: str, soup: BeautifulSoup) -> bool:
    try:
        list_places = soup.find_all(place, attrs={"class": attributs_class})
        return any(text_to_search == things.text.strip() for things in list_places)
    except AttributeError as e:
        print(e)
        pass
    return False


def init_webdriver(is_firefox: bool = False) -> webdriver:
    if is_firefox:
        profile = webdriver.FirefoxProfile()
        # disable pictures
        profile.set_preference('permissions.default.image', 2)
        driver = webdriver.Firefox(firefox_profile=profile)
    else:
        options = webdriver.ChromeOptions()
        # hide pictures
        options.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2})
        driver = webdriver.Chrome(options=options)
    return driver


def init_connection(driver: webdriver, url, title: str = None, check_button: bool = False):
    driver.get(url)
    if title is not None:
        assert title in driver.title
    if check_button:
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


def collect_info(driver: webdriver, url: str, current_search_id: int) -> Dict:
    ######################################
    #    Get the infos of a page         #
    ######################################
    driver.get(url)

    soup = BeautifulSoup(driver.page_source, "lxml")

    # cherche le subtype dans "tous les biens" et skip si pas vide
    # (les différents éléments des lots sont pris séparément)
    if get_bool_presence("h2", "text-block__title", "Tous les biens", soup):
        return {}

    #####################
    #   Instanciations  #
    #####################

    # Base
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

    # Finances
    price = None

    #####################
    #   Informations    #
    #####################

    # Base
    postal_code = re.search(search_for_postal_code, url).group("postal_code")
    try:
        city = driver.find_element_by_css_selector("p.classified__information--address-clickable").text.split(" — ")[
                -1].strip()
    except NoSuchElementException:
        # fallback
        city = driver.find_element_by_css_selector("span.classified__information--address-row").text.split(" — ")[
                -1].replace("|", "").strip()
    property_subtype = driver.find_element_by_css_selector("h1.classified__title")
    property_subtype = property_subtype.text

    if re.match(avendretext, property_subtype):
        property_subtype = property_subtype[:-9]

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

        # Finances
        elif entete == "Finances":
            lines = elem.find_all("div", {"class": "accordion__content"})
            for line in lines:
                span = line.find_all("span", {"class": "sr-only"})
                try:
                    price = span[0].text.replace("€", "").strip()
                except IndexError:
                    # fallback
                    price = soup.find("p", {"class": "classified__price"}).find("span", {
                        "class": "sr-only"}).text.replace("€", "").strip()

    data = {
        "Lien": url,
        "Prix": price,
        "Type de propriété": property_type[current_search_id],
        "Vente publique": vente_publique,
        "Immeuble de rapport": rapport,
        "Bien neuf": bien_neuf,
        "Code Postal": postal_code,
        "Ville": city,
        "Sous-type de propriété": property_subtype,
        "Nombre de façades": facade,
        "Etat du bâtiment": etat_batiment,
        "Surface habitable": area,
        "Nombre de chambre(s)": chamber,
        "Type de cuisine": cuisine_equipe,
        "Feu ouvert": feu_ouvert,
        "Meublé": meuble,
        "Jardin": jardin,
        "Surface du jardin": surface_jardin,
        "Terrasse": terrasse,
        "Surface de la terrasse": surface_terrasse,
        "Surface totale du terrain": surface_terrain,
        "Piscine": piscine,
        "Surface de la zone constructible": surface_constructible
    }
    return data


def save_data(donnees: List[Dict], page_number, current_search_id: int):
    ######################################
    #    Save the infos of each pages    #
    ######################################

    # Sauver avec panda => 1 csv : 30 entrées
    if len(donnees) > 0:  # if there is a least a data not skipped
        df = pd.DataFrame(donnees)
        df.to_csv("./immo-data/{}-{:03d}.csv".format(property_type[current_search_id].lower(), page_number),
                  index=False)
    else:
        print("Skipping to store an empty data for page {}".format(page_number))


def concat_all_csv(all_files_path: str, recursive=False) -> Union[DataFrame, None]:
    """
    Fonction to concat a list of files into a single csv
    """
    all_files = glob.glob(all_files_path, recursive=recursive)
    if len(all_files) > 0:
        df = pd.concat([pd.read_csv(filename, index_col=None, header=0) for filename in all_files], axis=0,
                       ignore_index=True)
        # saved in the current folder
        df.to_csv("immo_collect.csv")
        return df
    return None
