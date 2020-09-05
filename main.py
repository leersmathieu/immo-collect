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

        for current_page in range(self.p_start, self.p_end, self.search_id):
            donnees = load_page(self.driver, current_page, self.search_id)
            save_data(donnees, current_page, self.search_id)
        self.driver.close()


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
    # max pages to process
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
    print(csv.describe())
