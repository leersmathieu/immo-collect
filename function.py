# init file
import pandas as pd


def get_bool_presence(place, attributs_class, text_to_search, soup):
    try:
        list_places = soup.find_all(place, attrs={"class": attributs_class})
        return any(text_to_search == things.text.strip() for things in list_places)
    except AttributeError as e:
        print(e)
        pass
    return False




def concat_all_CSV(all_files):
    """
    Fonction to concat a list of files into a single csv
    """

    df = pd.concat([pd.read_csv(filename, index_col=None, header=0) for filename in all_files], axis=0, ignore_index=True)
    # saved in the current folder
    df.to_csv("immo_collect.csv")
    return df