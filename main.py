# -*- coding: utf-8 -*-

from function import *

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

    # init webdriver (firefox or chrome)
    driver = init_webdriver(is_firefox=False)

    # check existence of the page
    init_connection(driver, url_appart_search.format(0), title="Immoweb", check_button=True)

    # current search between 'appartement' and 'maison'
    current_search_id = 1

    # max pages to process
    page_start = 0
    page_end = 333  # not included

    for page_number in range(page_start, page_end):
        donnees = load_page(driver, page_number, current_search_id)
        save_data(donnees, page_number, current_search_id)
    driver.close()

    ######################################
    #         Concat all the csv         #
    ######################################

    csv = concat_all_csv("./immo-data/*.csv")
    print(csv.describe())
