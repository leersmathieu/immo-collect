# init file
import pandas as pd
from selenium import webdriver
from bs4 import BeautifulSoup


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


def concat_all_csv(all_files) -> pd.DataFrame:
    """
    Fonction to concat a list of files into a single csv
    """

    df = pd.concat([pd.read_csv(filename, index_col=None, header=0) for filename in all_files], axis=0,
                   ignore_index=True)
    # saved in the current folder
    df.to_csv("immo_collect.csv")
    return df
