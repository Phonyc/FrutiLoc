import json
import os
import dotenv
import requests
from bs4 import BeautifulSoup

dotenv.load_dotenv()


def get_gps(url):
    """
        Obtenir les coordonnées gps de la fruitière
    :param url:
    :return:
    """
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        elem = soup.select_one('.map')
        out = json.loads(elem.get('data-component-options'))['defaultCenter']
        out["lien"] = url
        return [out]
    else:
        print(f"Failed to retrieve the webpage. Status code: {response.status_code}")
        return []


def get_links(url):
    """
        Obtenir les liens vers les pages des fruitières
    :param url:
    :return:
    """
    out = []
    next_link = None
    # Fetch the content
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        elems = soup.select('.list-item .default-list-item-content a')
        try:
            next_link = soup.find('link', rel='next').get('href')
        except AttributeError:
            next_link = None

        for elem in elems:
            out.append(elem.get('href'))
    else:
        print(f"Failed to retrieve the webpage. Status code: {response.status_code}")
    return out, next_link


class Getter:
    """
        Obtenir les coordonées GPS
    """

    def __init__(self, page_liste):
        self.page_liste = page_liste
        self.links_frutieres = []
        self.gps_cords = []

    def get_links_frutieres(self):
        """
            Obtenir les liens vers les pages des fruitières
        """
        link = self.page_liste

        while link is not None:
            result = get_links(link)
            self.links_frutieres += result[0]
            link = result[1]

    def get_gps_locs(self):
        """
            Obtenir les coordonnées GPS
        """
        for link in self.links_frutieres:
            self.gps_cords += get_gps(link)
        print(self.gps_cords)

    def save_locs(self):
        """
        Sauvegarder les localisations
        :return:
        """
        json.dump(self.gps_cords, open('locs.json', 'w'))


if __name__ == "__main__":
    getter = Getter(os.getenv("LIEN"))
    getter.get_links_frutieres()
    getter.get_gps_locs()
    getter.save_locs()
