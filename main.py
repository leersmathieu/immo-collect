import selenium
import requests
import lxml
from bs4 import BeautifulSoup


base_url = "https://www.immoweb.be/"

# TODO
# 2 searches with Selenium :
#       - House
#       - Apart
# /!\ without life sales
page_number = 1

url_appart_search = "{}fr/recherche/appartement/a-vendre?countries=BE&isALifeAnnuitySale=false&page={}&orderBy=relevance".format(base_url, page_number)
url_house_search = "{}fr/recherche/maison/a-vendre?countries=BE&isALifeAnnuitySale=false&page={}&orderBy=relevance".format(base_url, page_number)
print(url_appart_search)

appart_links = []
house_links = []

response = requests.get(url_appart_search)

if response.status_code >= 200 and response.status_code <= 400:
    soup = BeautifulSoup(response.content, "lxml")
    print(soup)



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
# Panda to organize everything in a goot csv