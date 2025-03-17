import os
import dotenv
import requests
from bs4 import BeautifulSoup

dotenv.load_dotenv()


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
        h1_tags = soup.select('.list-item .default-list-item-content a')
        try:
            next_link = soup.find('link', rel='next').get('href')
        except AttributeError:
            next_link = None

        for tag in h1_tags:
            out.append(tag.get('href'))
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

    def get_links_frutieres(self):
        """
            Obtenir les liens vers les pages des fruitières
        """
        link = self.page_liste

        while link is not None:
            result = get_links(link)
            self.links_frutieres += result[0]
            link = result[1]


if __name__ == "__main__":
    getter = Getter(os.getenv("LIEN"))
    getter.get_links_frutieres()
    print(getter.links_frutieres)
