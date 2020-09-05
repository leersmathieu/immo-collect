# -*- coding: utf-8 -*-
from threading import Thread

from function import *


class CustomThread(Thread):
    def __init__(self, p_start: int, p_end: int, search_id: int) -> None:
        super().__init__()
        self.p_start = p_start
        self.p_end = p_end
        self.search_id = search_id
        self.driver = None

    def run(self) -> None:
        # init webdriver (firefox or chrome)
        self.driver = init_webdriver(is_firefox=False)
        # check existence of the page
        init_connection(self.driver, url_appart_search.format(0), title="Immoweb", check_button=True)

        for current_page in range(self.p_start, self.p_end):
            donnees = self.get_page_data(current_page)
            save_data(donnees, current_page, self.search_id)
        self.driver.close()

    def get_page_data(self, page_number: int) -> List[Dict]:
        current_url = (url_appart_search if current_search_id == 0 else url_house_search).format(page_number)
        collected_links = self.collect_links(current_url)
        donnees = []
        for url in collected_links:
            data = collect_info(self.driver, url, self.search_id)
            donnees.append(data)
            print(data)
        return donnees

    def collect_links(self, current_url: str) -> List[str]:
        # target the right page
        self.driver.get(current_url)
        # take all the links
        soup = BeautifulSoup(self.driver.page_source, "lxml")
        intermediate_links = soup.find_all("a", {"class": "card__title-link"})
        return [link.get("href") for link in intermediate_links]


if __name__ == '__main__':
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

    current_search_id = 1
    # min/max pages to process
    page_start = 0
    page_end = 333  # not included
    plage_page = [(0, 50), (50, 100)]

    thread_list = []
    for thread_id in range(0, len(plage_page)):
        t = CustomThread(plage_page[thread_id][0], plage_page[thread_id][1], current_search_id)
        thread_list.append(t)

    for t in thread_list:
        t.start()

    for t in thread_list:
        t.join()

    ######################################
    #         Concat all the csv         #
    ######################################

    csv = concat_all_csv("./immo-data/*.csv")
    if csv is not None:
        print(csv.describe())
