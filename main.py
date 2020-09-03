import selenium
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
import requests
import lxml
from bs4 import BeautifulSoup
import time


base_url = "https://www.immoweb.be/"

# TODO
# 2 searches with Selenium :
#       - House
#       - Apart
# /!\ without life sales



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

for page_number in range (1,2):

    url_appart_search = "{}fr/recherche/appartement/a-vendre?countries=BE&isALifeAnnuitySale=false&page={}&orderBy=relevance".format(base_url, page_number)
    url_house_search = "{}fr/recherche/maison/a-vendre?countries=BE&isALifeAnnuitySale=false&page={}&orderBy=relevance".format(base_url, page_number)
    
    driver = webdriver.Chrome()
    driver.implicitly_wait(10)
    driver.get(url_appart_search)
    assert "Immoweb" in driver.title
    try:
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'uc-btn-accept-banner'))
        )
        if element is not None:
            element.click()
            print("button clicked")
    except Exception as e:
        print(e)

    soup = BeautifulSoup(driver.page_source, "lxml")
    intermediate_links = soup.find_all("a", {"class": "card__title-link"})
    for link in intermediate_links:
        link = link.get("href")
        appart_links.append(link)

    for url in appart_links:
        driver.get(url)
        try:
            element = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.ID, 'uc-btn-accept-banner'))
            )
            if element is not None:
                element.click()
                print("button clicked")
        except Exception as e:
            print(e)

        soup = BeautifulSoup(driver.page_source, "lxml")
        adress = soup.find_all("p",{'class':'classified__information--address-clickable'})
        for e in adress:
            print(e.text)
        driver.close()
        break





# TODO
# make a for in range (333?)

# TODO
# For each search : (333 pages each) (Selenium)
#       For each pages :
#               For each house/apart :
#                       Take link (2 lists, one for house, one for apart)


# TODO
# For each link :
#       Take information (BeautifulSoup)


# TODO
# Panda to organize everything in a good csv