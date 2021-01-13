import csv
import json
import logging
import time

import requests
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.DEBUG, filename='logs.txt')


def make_soup(url, session):
    ''' get HTML for each location '''
    request = session.get(f'{url}?currency=USD')
    # , params={'currency': 'USD'})
    if request.status_code == 200:
        logging.info(f'{request.url}')
        soup = BeautifulSoup(request.content, 'lxml')
        return soup


def scrape_city_data(soup):
    ''' get coffee and beer data from each location and store in dict '''
    city_price_data = {}
    table_data = soup.table.find_all('tr')

    for i in table_data:
        try:
            if 'Cappuccino' in i.text or 'beer' in i.text:
                # logging.debug(f'i: {i}')
                # logging.debug(f'i find a: {i.find("a")}')
                item = i.find('a').text.strip()
                price = i.find('td', class_='price city-1').text.strip()
                logging.debug(f'price {price}')
                city_price_data[item] = price
        except AttributeError:
            pass
    return city_price_data


def scrape_usd_city_data(soup):
    ''' get coffee and beer data from each location and store in dict '''
    city_price_data = {}
    table_data = soup.table.find_all('tr')
    for i in table_data:
        try:
            if 'Cappuccino' in i.text or 'beer' in i.text:
                # logging.debug(f'i: {i}')
                # logging.debug(f'i find a: {i.find("a")}')
                item = i.find('a').text.strip()
                price = i.find_all('td', class_='price city-1')
                # logging.debug(f'price {price}')
                city_price_data[item] = [x.text.strip() for x in price]
                # logging.debug(f' city price data: {city_price_data}')
        except:
            pass
    return city_price_data


def scrape_all_expatistan_locations():
    ''' grab all location urls from expatistan '''
    url = 'https://www.expatistan.com/cost-of-living/all-cities'
    soup = make_soup(url)
    # logging.debug(soup.prettify())
    hrefs = soup.find('div', id='content').find_all('a')
    cities = [a.text for a in hrefs]
    urls = [a['href'] for a in hrefs]
    return cities, urls


def write_city_data(data):
    ''' write city data to json file '''
    with open('data/expatistan/expatistan-data.json5', 'a') as f:
        json.dump(data, f)
        json.dump(',', f)


def scrape():
    # cities, urls = scrape_all_expatistan_locations() # 3266 total pages
    # with open('city-urls.txt', 'w') as f:
    #     for i in range(len(cities)):
    #         f.write(f'{cities[i]} \t {urls[i]}\n')

    cities = []
    urls = []
    with open('data/expatistan/expatistan-numbeo-crossover.csv') as f:
        reader = csv.reader(f, delimiter='\t')
        header = next(reader, None)
        for row in reader:
            city, url = row
            cities.append(city)
            urls.append(url)

    locations_html = map(make_soup, urls)
    city_data = list(map(scrape_usd_city_data, locations_html))
    all_city_data = dict(zip(cities, list(city_data)))
    write_city_data(all_city_data)
    print(all_city_data)


def scrape_in_chunks():
    s = requests.Session()
    with open('data/expatistan/expatistan-numbeo-crossover.csv') as f:
        reader = csv.reader(f, delimiter='\t')
        header = next(reader, None)
        for row in reader:
            city, url = row
            html = make_soup(url, s)
            city_data = scrape_usd_city_data(html)
            data_to_write = {city: city_data}
            write_city_data(data_to_write)


if __name__ == "__main__":
    scrape_in_chunks()
