from threading import Thread
from typing import List, Dict

from bs4 import BeautifulSoup

from function import init_webdriver, init_connection, url_appart_search, save_data, url_house_search, collect_info


class CustomThread(Thread):
    def __init__(self, p_start: int, p_end: int, search_id: int, is_firefox: bool = False) -> None:
        """
        a thread constructor
        :param p_start: the first page to search
        :param p_end: the last page to search (not included)
        :param search_id: the type of search between "appartement" and "maison"
        """
        super().__init__()
        self.p_start = p_start
        self.p_end = p_end
        self.search_id = search_id
        self.driver = None
        self.is_firefox = is_firefox

    def run(self) -> None:
        """
        a task initiating the webdriver and then search in the range provided of page of links to collect all the infos
        each info about 30 entries is stored in a folder "immo-data"
        :return: None
        """
        # init webdriver (firefox or chrome)
        self.driver = init_webdriver(self.is_firefox)
        # check existence of the page
        init_connection(self.driver, url_appart_search.format(0), title="Immoweb", check_button=True)

        for current_page in range(self.p_start, self.p_end):
            donnees = self.get_page_data(current_page)
            save_data(donnees, current_page, self.search_id)
        self.driver.close()

    def collect_links(self, current_url: str) -> List[str]:
        """
        search and return all the links in the provided url
        :param current_url: the url where to search for links
        :return: all the founded links
        """
        # target the right page
        self.driver.get(current_url)
        # take all the links
        soup = BeautifulSoup(self.driver.page_source, "lxml")
        intermediate_links = soup.find_all("a", {"class": "card__title-link"})
        return [link.get("href") for link in intermediate_links]

    def get_page_data(self, page_number: int) -> List[Dict]:
        """
        collect all the infos by searching in all the links of an initial page of links
        self.search_id defines the type of search between "appartement" and "maison"
        :param page_number: the page number of the search of links
        :return: a list of collected datas
        """
        current_url = (url_appart_search if self.search_id == 0 else url_house_search).format(page_number)
        collected_links = self.collect_links(current_url)
        donnees = []
        for url in collected_links:
            try:
                data = collect_info(self.driver, url, self.search_id)
            except AttributeError:
                print("Skipping an entry with an attribute error for url: ", url)
                continue

            if len(data) > 0:
                donnees.append(data)
                print(data)
            else:
                print("skipping a batch link", url)
        return donnees