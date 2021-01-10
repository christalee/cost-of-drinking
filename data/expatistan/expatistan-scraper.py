import requests
from bs4 import BeautifulSoup
import logging
import json

logging.basicConfig(level=logging.INFO)

def make_soup(url):
    ''' get HTML for each location '''
    request = requests.get(url, params={'currency': 'USD'})
    if request.status_code == 200:
        # logging.debug(f'status code for {url} is {request.status_code}')
        soup = BeautifulSoup(request.content, 'lxml')
        return soup

def scrape_city_data(soup):
    ''' get coffee and beer data from each location and store in dict '''
    city_price_data = {}
    table_data = soup.table.find_all('tr')

    for i in table_data:
        try:
            if 'Cappuccino' in i.text or 'beer' in i.text:
                logging.debug(f'i: {i}')
                logging.debug(f'i find a: {i.find("a")}')
                item = i.find('a').text.strip()
                price = i.find('td', class_='price city-1').text.strip()
                city_price_data[item] = price
        except AttributeError:
            pass
    return city_price_data

def scrape_expatistan_locations():
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
    with open('expatistan-data.json', 'w') as f:
        json.dump(data, f)

if __name__ == "__main__":
    cities, urls = scrape_expatistan_locations() # 3266 total pages
    # scraping the first 11 for testing
    cities = cities[0:10]
    urls = urls[0:10]
    locations_html = map(make_soup, urls)
    city_data = list(map(scrape_city_data, locations_html))
    all_city_data = dict(zip(cities, list(city_data)))
    write_city_data(all_city_data)
    print(all_city_data)
    # TODO: write scraper for USD column
    # TODO: determine which locations to pull
    # TODO: distinguish countries from cities

