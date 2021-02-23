import csv
import json
import logging

import numpy as np
import requests
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO, filename='logs.txt')


def make_soup(url, session):
    '''Get HTML for each location.'''
    request = session.get(f'{url}?currency=USD')
    if request.status_code == 200:
        logging.info(f'{request.url}')
        soup = BeautifulSoup(request.content, 'lxml')

        return soup


def format_item(label, item):
    '''Format price data and store it in a dict.'''
    price_data = {}
    price = item.findAll('td', class_='price city-1')
    new_price_list = [x.text.strip() for x in price]
    new_price = new_price_list[-1].replace(')', '').replace('(', '').replace('$', '')
    if '-' in new_price:
        price_data[label] = np.nan
    else:
        price_data[label] = round(float(new_price), 2)

    return price_data


def scrape_city_data(soup):
    '''Get coffee, beer, and bread data from each location and store in dict.'''
    city_price_data = {}
    table_data = soup.table.find_all('tr')

    for i in table_data:
        try:
            if 'beer in neighbourhood pub' in i.text:
                city_price_data.update(format_item('beer_pub', i))

            if 'domestic beer in the supermarket' in i.text:
                city_price_data.update(format_item("beer_market", i))

            if 'Bread' in i.text:
                city_price_data.update(format_item('bread', i))

            if 'Cappuccino' in i.text:
                city_price_data.update(format_item('coffee', i))

        except AttributeError:
            pass

    return city_price_data


def main():
    all_city_data = []
    s = requests.Session()

    with open('crossover.csv') as f:
        reader = csv.reader(f, delimiter=',')
        next(reader, None)
        for row in reader:
            city_ascii, country, url = row
            html = make_soup(url, s)
            city_data = scrape_city_data(html)
            all_city_data.append({'city_ascii': city_ascii,
                                  'country': country,
                                  'data': city_data})

    with open('expatistan-data_py.json', 'w') as f:
        json.dump(all_city_data, f)


if __name__ == "__main__":
    main()
