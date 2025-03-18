"""
Obtenir les localisations des fruitières à Comté
"""
import json
import os
import dotenv
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

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

    def __init__(self, page_liste, gps_cords=None):
        if gps_cords is None:
            gps_cords = []
        self.page_liste = page_liste
        self.links_frutieres = []
        self.gps_cords = gps_cords
        self.data_image = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACIAAAAsCAYAAAAATWqyAAAAGXRFWHRTb2Z0d2FyZQBBZG9iZSBJbWFnZVJlYWR5ccllPAAABTtJREFUeNq8WGtsFUUU/rb3gtdCAykFG9AUDTQUKimhxUewEusrJYoBo4FfEgoqotHERH6oP9TGmJhIrIlWAf9hjAaEiME2pgFfVVpFii8sWqIQLLSx3EJLW7p+Z2Z2b2l7d/b23vZLTmZ2duacb2fmnDk7DlKA67rXs1hJKacsohRQppjXFygnKT9TDlH2O47zFzIFGnco91EOuqnjoBnr2Ow4FhIlLN6m3DykFTh3BGj/Doj/CfSe082xPCDnBmDWTUBeyXDVjZTHOUNHUiZCEs+weI0ySTV0/w0c2wa07gIungn+vOx8YN46oPhpYOp1Xms/5TmSeSMUERKImFnYqBoGuPRNL5LEW8BgX2rrmjWZZLYApS8BUW8r4T0zO5eTEjFr+S6lSjV0HgPqVwNdf6S30abNB+7aDeQWey3bKZtIxvU5DxvyrE/izJfAvuXpkxCIDtElOjWqjK2RM8LZWMbiG0oEnUc5kB7a14WMYvI04H56du5ieZKluZWz8r0/IyQh5TuKRH8cqFuTeRIC0Sm6xYbYok1j21+ahyhLVO3wC8D5VowbRLfY0FhibOulIavDLEoRZyD8sJDeMWBXKG5ZsIobsdDsg+OMq3u1m1u9KQo8zP45EqjRxOUpk6i50IRl4FuGjpZtwUoiMYa314GFj/EzIsN8n8v+C1e4kfvwcm+wnhsZY27xQ8oiWZpKrWRQB6tAElfxpKnjsCdGklDzG9HvpI/0DYLYEpsalVnmAAM6fgR62oMHl70C5N9mn3rpI32DILbEpkZ5ljlFgbPNFtebzij5VPhNKX1lTBASNtXSzPZ3cxCuvVOH7FTCu4yxeZDGbCES0z5+PniQ3uGpwTYmYTOWCPGTpgYP6u9OnYhtzBCbQkSH0NiM4EEdP6VOxDYmYbNLiJxQ1elFwYPaG3XQCn3QHddjgpCweUKI6K2bvzw4YROf//rJob6fZl/H2FRoFiINfqo3qyzYwD8MVIeYLw32J+8j76SP9A2C2BKbGg1CZL+EF/W4YKP9a3/fCeyhkrY9DOOXEu1SlzZ5J31sSNjqURm/OfQkY9qgvkYOvXhbuH0g505Oga7HT9rPF9+t5+pDL0ulwzt46FV5ROax+JUSRRtP0LoHMK64+xNg7iqVEVOKSKRVxRGpsKhRnaRD4SPjR0J0axKCGmP7ilQxm4X8d8xXmfvHJZlPkCR3WfODl9FLMlxCIhevSJ5Nwzo1XdKxYpe3hpmB6BKdmoS43VqPxIgsni+aWOg8biZ3f+nLmSMiuvKWek/P01az7QdLyNVT7lC/l59WAKcb0iMxhzpW1nvmvpDtSiKD1l9OkpnDgv8UyMWFU9wvTP8vdY6NhJwnD1JVtso2OiiLSeL0iJUbNfg6zikVVwRTyOn2HWOfjfLtHgnBhtFIJCViyNDZUatdmnGlaFPqJIoe1WM1aqlz71ivJbLNobgAA9zgu7nZ/vstHAk5WVdzaPRqmGC5lER6kjpV4OWJdq+1kkshSk4VH9izcy/bV66qSPQZV+0J9G7rTY6+XNmqHmYwyJVV24kse1X31dhKHdasygkzy+a64oC4nWr47F4e858nSbLv4V/KAe9JKpVDrx/SImLIXMOiRUKdujESl+49O8xVZxpXzVc/C/I/RxL/hgq8YYkYhev9q6kVO4d9B+sr3vdICNaHJTHWW8Ya/87wqy2uWwstUk/gTYw3aCRGOarMDfS67kfFWqSuIe9imAjQEC272nJHixYNaSvGRIIGN49ywbsZEw1zI11N6TZSHeaGORn+F2AAJtRIMx4t+hUAAAAASUVORK5CYII="

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
        for link in tqdm(self.links_frutieres):
            self.gps_cords += get_gps(link)
        print(self.gps_cords)

    def save_locs(self):
        """
        Sauvegarder les localisations
        :return:
        """
        json.dump(self.gps_cords, open('locs.json', 'w'))

    def save_to_kml(self):
        """
            Sauvegarder les données en Kml
        """
        out = '<kml xmlns="http://www.opengis.net/kml/2.2" xmlns:gx="http://www.google.com/kml/ext/2.2" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.opengis.net/kml/2.2 https://developers.google.com/kml/schema/kml22gx.xsd"><ExtendedData/><Document>'
        for point in tqdm(self.gps_cords):
            out += f'''
            <Placemark>
                <description>{point["lien"]}</description>
            <Style>
                <IconStyle>
                    <scale>1.0625</scale>
                    <Icon>
                        <href>{self.data_image}</href>
                        <gx:w>34</gx:w>
                        <gx:h>44</gx:h>
                    </Icon>
                    <hotSpot x="17" y="0" xunits="pixels" yunits="pixels"/>
                </IconStyle>
            </Style>
            <ExtendedData>
                <Data name="measure">
                    <value>lon : {point["lng"]}° / lat : {point["lat"]}°</value>
                </Data>
            </ExtendedData>
            <Point>
                <coordinates>{point["lng"]},{point["lat"]}</coordinates>
            </Point>
        </Placemark>
        '''
        out += '</Document></kml>'
        with open('fruitieres.kml', 'w') as f:
            f.write(out)


if __name__ == "__main__":
    # Avec sauvegarde
    getter = Getter(os.getenv("LIEN"), gps_cords=json.load(open('locs.json')))
    getter.save_to_kml()

    # Depuis le début
    # getter = Getter(os.getenv("LIEN"))
    # getter.get_links_frutieres()
    # getter.get_gps_locs()
    # getter.save_locs()
