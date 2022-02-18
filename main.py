from datetime import datetime
import requests
from bs4 import BeautifulSoup
import time
import re
import json
from tqdm.notebook import tqdm

counter = 0

def write_to_file(list_input):
    # The scraped info will be written to a CSV here.
    with open(f"/data/flat_prices/allflats_{str(datetime.now().date())}.txt", "a") as file:  # Open the csv file.
        print(f'{str(list_input)}\n')
        file.write(f'{json.dumps(list_input)}\n')
    global counter
    counter += 1
    print(f'{counter} / {results_count}')


def scrape(soup, item_class, sleep=1):  # Takes the driver and the subdomain for concats as params
    # Find the elements of the article tag
    adds = soup.find_all("div", class_=item_class)

    # Iterate over each book article tag
    for each_add in adds:
        try:
            features = {'datetime': str(datetime.now().date())}
            features.update({'id': each_add.get('id')})
            features.update({'url': each_add.find('a', class_='list__item__content__title__name').get('href')})
            features.update({'description': each_add.find('div', class_='ogl__description').text})
            features.update({'price': each_add.find('div', class_='list__item__picture__price').p.text})
            features.update({'price_m': each_add.find('p', class_="list__item__details__info details--info--price").text})
            details = each_add.find_all('div', class_="list__item__details__icons__wrap")
            for d in details:
                p = d.find_all('p')
                features.update({p[0].text: p[1].text})

            # Get details
            html_text = requests.get(features['url']).text
            soup_item = BeautifulSoup(html_text, 'html.parser')
            item_details = soup_item.find_all('div', class_='oglDetails panel')[1]

            list_details = item_details.findChildren('div', recursive=False)
            for c in list_details:
                item_key = c['class'][-1]
                item_value = c.find('span', class_='oglField__value')
                if item_value:
                    features.update({re.sub('oglField--', '', c['class'][-1]): item_value.text})
                elif item_key == 'oglField--address':
                    map = c.find('a', class_='link__map android_micro_action_location')
                    if map:
                        features.update({'map': map.get('href')})
                elif item_key == 'oglField--array':
                    features.update({'more': [m.span.text for m in c.find_all('li', class_='oglFieldList__item')]})

            # Invoke the write_to_csv function
            write_to_file(features)
            time.sleep(sleep)
        except:
            pass


def browse_and_scrape(seed_url, page_number=0):
    # Page_number from the argument gets formatted in the URL & Fetched
    formatted_url = seed_url.format(str(page_number))
    print(f"Current page: {page_number}")
    global counter
    global results_count
    print(f'{counter} / {results_count}')

    try:
        html_text = requests.get(formatted_url).text
        # Prepare the soup
        soup = BeautifulSoup(html_text, "html.parser")
        print(f"Now Scraping - {formatted_url}")

        # This if clause stops the script when it hits an empty page
        try:
            next_page = soup.find('div', class_="no-result")
        except:
            next_page = None

        if next_page is None:
            scrape(soup, 'list__item')  # Invoke the scrape function
            # Be a responsible citizen by waiting before you hit again
            time.sleep(1)
            page_number += 1
            # Recursively invoke the same function with the increment
            browse_and_scrape(seed_url, page_number)
        else:
            scrape(soup, 'list__item')  # The script exits here
            return True
        return True
    except:
        pass


if __name__ == '__main__':
    # seed_url = 'https://ogloszenia.trojmiasto.pl/nieruchomosci/ai,_650000,e1i,58_1_87_7_31,ikl,101_106,qi,50_,ri,3_,wi,100_200_230_250_260_220_240_210,o2,0.html?strona={}'
    seed_url = 'https://ogloszenia.trojmiasto.pl/nieruchomosci/ikl,101_106,nf1i,1_2_3,wi,100_200_230_250_260_220_240_210,o2,0.html' # - okolicy
    seed_url = 'https://ogloszenia.trojmiasto.pl/nieruchomosci/f1i,1_2_3,ikl,101_106,o2,0.html'
    print("Web scraping has begun")

    # get total count
    html_text = requests.get(seed_url).text
    soup = BeautifulSoup(html_text, "html.parser")
    mx = soup.find('div', class_='form-heading__desc')
    results_count = (int(re.sub('[^0-9]', '', mx.find('span').text)))


    result = browse_and_scrape(seed_url+'?strona={}')
    if result:
        print("Web scraping is now complete!")
    else:
        print(f"Oops, That doesn't seem right!!! - {result}")


