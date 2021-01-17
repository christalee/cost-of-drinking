import csv
import json
import logging
import requests
from bs4 import BeautifulSoup
import numpy as np

logging.basicConfig(level=logging.INFO, filename='logs.txt')

def make_soup(url, session):
    ''' get HTML for each location '''
    request = session.get(f'{url}?currency=USD')
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
            if 'beer in neighbourhood pub' in i.text:
                item = 'beer_pub'
                price = i.findAll('td', class_='price city-1')
                new_price_list = [x.text.strip() for x in price]
                new_price = new_price_list[-1].replace(')', '').replace('(', '').replace('$', '')
                if '-' in new_price:
                    city_price_data[item] = np.nan
                else:
                    city_price_data[item] = round(float(new_price), 2)
            if 'domestic beer in the supermarket' in i.text:
                item = 'beer_supermarket'
                price = i.findAll('td', class_='price city-1')
                new_price_list = [x.text.strip() for x in price]
                new_price = new_price_list[-1].replace(')', '').replace('(', '').replace('$', '')
                if '-' in new_price:
                    city_price_data[item] = np.nan
                else:
                    city_price_data[item] = round(float(new_price), 2)
            if 'Bread' in i.text:
                item = 'bread'
                price = i.findAll('td', class_='price city-1')
                new_price_list = [x.text.strip() for x in price]
                new_price = new_price_list[-1].replace(')', '').replace('(', '').replace('$', '')
                if '-' in new_price:
                    city_price_data[item] = np.nan
                else:
                    city_price_data[item] = round(float(new_price), 2)
            if 'Cappuccino' in i.text:
                item = 'cappuccino'
                price = i.findAll('td', class_='price city-1')
                new_price_list = [x.text.strip() for x in price]
                new_price = new_price_list[-1].replace(')', '').replace('(', '').replace('$', '')
                if '-' in new_price:
                    city_price_data[item] = np.nan
                else:
                    city_price_data[item] = round(float(new_price), 2)
        except AttributeError:
            pass
    return city_price_data

def write_city_data(data):
    ''' write city data to json file '''
    with open('expatistan-data-15Jan20.json', 'w') as f:
        json.dump(data, f)

def main():
    all_city_data = []
    s = requests.Session()
    with open('crossover.csv') as f:
        reader = csv.reader(f, delimiter=',')
        header = next(reader, None)
        for row in reader:
            city_ascii, country, url = row
            html = make_soup(url, s)
            city_data = scrape_city_data(html)
            all_city_data.append({'city_ascii': city_ascii,
                                  'country': country,
                                  'data': city_data})
    write_city_data(all_city_data)

if __name__ == "__main__":
    main()
