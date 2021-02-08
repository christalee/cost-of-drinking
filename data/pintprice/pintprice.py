import time
from typing import Dict, List, Optional
from urllib import parse, request

import pandas as pd
from bs4 import BeautifulSoup


def get_soup(country: str) -> Optional[BeautifulSoup]:
    '''Takes a country name, returns the bs output from that country's page on pintprice.com.'''
    safe = parse.quote(country)
    url = 'http://www.pintprice.com/region.php?/{}/USD.htm'.format(safe)
    try:
        html = request.urlopen(url)
        if html.status == 200:
            return BeautifulSoup(html.read(), 'html.parser')
        else:
            return None
    except:
        return None


def get_prices(country: str) -> Optional[List[List[str]]]:
    '''Takes a country name, returns the table of cities and prices from that country's page on pintprice.com.'''
    soup: Optional[BeautifulSoup] = get_soup(country)
    if soup:
        table = []
        tds: List[str] = [td.get_text().strip() for td in soup.find_all("td")]
        for x in range(0, len(tds), 2):
            table.append([tds[x], tds[x + 1]])
        return table
    else:
        return None


def get_countries(soup: BeautifulSoup) -> List[str]:
    '''Parses one page to get the list of all countries from the drop-down.'''
    countries = [c.get_text() for c in soup.find_all("option")][:-5]
    return countries


def tidy(country: str, pint_price: Dict[str, List[List[str]]]) -> pd.DataFrame:
    '''Creates a df for country and cleans up the Country and Price columns.'''
    df = pd.DataFrame(pint_price[country])

    # Move Cost/Price to the column headings
    df.columns = pd.Index(df.iloc[0])
    df = df.drop(df.index[0])

    # set the Country column and clean up the Price column
    df['Country'] = country
    df['Price'] = df['Price'].str.strip("$ USD").astype("float", errors="ignore")

    return df


if __name__ == "__main__":
    pint_price = {}

    # There's an extra <td> on the UK page, so let's skip it
    uk_table = []
    uk_soup: BeautifulSoup = get_soup("United Kingdom")
    uk_tds: List[str] = [td.get_text().strip() for td in uk_soup.find_all("td")][1:]
    for x in range(0, len(uk_tds), 2):
        uk_table.append([uk_tds[x], uk_tds[x + 1]])

    pint_price["United Kingdom"] = uk_table

    countries: List[str] = get_countries(uk_soup)
    for c in countries:
        prices = get_prices(c)
        if c != "United Kingdom" and prices:
            pint_price[c] = prices
            time.sleep(0.1)

    pint_price_df: pd.DataFrame = tidy("United Kingdom", pint_price)
    # Do it again for each country and concat onto pint_price_df
    for country in pint_price:
        if country != "United Kingdom":
            pp: pd.DataFrame = tidy(country, pint_price)
            pint_price_df = pd.concat([pint_price_df, pp])

    # One last round of cleaning and reindexing
    pint_price_df.columns = pd.Index(['city_ascii', 'beer_pub', 'country'])
    pint_price_df = pint_price_df.reindex(columns=['city_ascii', 'country', 'beer_pub'])
    pint_price_df = pint_price_df[pint_price_df['beer_pub'] != "npriced"]
    pint_price_df['city_ascii'] = pint_price_df.city_ascii.str.title()

    pint_price_df.to_csv("pintprice.csv")
