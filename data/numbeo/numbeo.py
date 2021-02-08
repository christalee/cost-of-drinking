import json
import time

import geocoder
import numpy as np
import pandas as pd
import qwikidata.sparql
from requests import Session


def clean(df, find_str, find_col="city_ascii", edit_str=None, edit_col=None):
    '''Given a df, a column to search, a search string, a column to edit, and a string to edit in, return the df with the column edited appropriately.'''
    if not edit_str:
        edit_str = find_str
    if not edit_col:
        edit_col = find_col
    df.loc[df[find_col].str.contains(find_str), edit_col] = edit_str
    return df


def read_numbeo():
    '''Read and merge all Numbeo data tables.'''
    categories = ["beer_market", "beer_pub", "bread", "coffee"]
    numbeo_beer_market, numbeo_beer_pub, numbeo_bread, numbeo_coffee = [pd.read_table('numbeo_' + x + ".txt", names=['rank', 'city', x], index_col='rank') for x in categories]
    # numbeo_beer_market = pd.read_table('numbeo_beer_market.txt', names=["rank", "city", "beer_market"], index_col="rank")
    # numbeo_beer_pub = pd.read_table("numbeo_beer_pub.txt", names=["rank", "city", "beer_pub"], index_col="rank")
    # numbeo_bread = pd.read_table('numbeo_bread.txt', names=["rank", "city", "bread"], index_col="rank")
    # numbeo_coffee = pd.read_table("numbeo_coffee.txt", names=['rank', 'city', 'coffee'], index_col="rank")

    numbeo = pd.merge(numbeo_beer_market, numbeo_beer_pub, how="outer", on="city")
    numbeo = pd.merge(numbeo, numbeo_bread, how="outer", on="city")
    numbeo = pd.merge(numbeo, numbeo_coffee, how="outer", on="city")

    return numbeo


def read_city_data():
    # read in region, lat/lng, pop data
    city_data = pd.read_csv('../city-data/world-cities-data.csv')
    city_data['region'] = city_data['region'].str.strip().str.title()

    # corrections
    city_data.loc[city_data.country.str.contains("Bahamas"), "country"] = "Bahamas"
    city_data.loc[city_data.country.str.contains("Korea, South"), "country"] = "South Korea"

    index = city_data[city_data.city_ascii.str.contains("Natal") & city_data.admin_name.str.contains("Amazonas")].index
    city_data = city_data.drop(index=index)

    return city_data


def numbeo_correct(numbeo):
    # corrections
    numbeo.city_ascii = numbeo.city_ascii.str.replace("Saint", "St.")
    numbeo.loc[numbeo.city_ascii.str.contains("Petersburg") & numbeo.country.str.contains("Russia"), "city_ascii"] = "Saint Petersburg"

    numbeo = clean(numbeo, find_str="Tel Aviv")
    numbeo = clean(numbeo, find_str="Jeddah")
    numbeo = clean(numbeo, find_str="Arhus", edit_str="Aarhus")
    numbeo = clean(numbeo, find_str="Freiburg")
    numbeo = clean(numbeo, find_str="Calicut")
    numbeo = clean(numbeo, find_str="Lucknow")
    numbeo = clean(numbeo, find_str="Padova", edit_str="Padua")
    numbeo = clean(numbeo, find_str="Astana")
    numbeo = clean(numbeo, find_str="The Hague")
    numbeo = clean(numbeo, find_str="Krakow")
    numbeo = clean(numbeo, find_str="Zaragoza")
    numbeo = clean(numbeo, find_str="Seville")
    numbeo = clean(numbeo, find_str="Kyiv")
    numbeo = clean(numbeo, find_str="Odessa")
    numbeo = clean(numbeo, find_str="Novgorod", edit_str="Nizhniy Novgorod")
    numbeo = clean(numbeo, find_str="Erbil")

    numbeo = clean(numbeo, find_col="country", find_str="Kosovo")

    return numbeo


def read_expat():  # load in expatistan data
    with open("../expatistan/expatistan-data.json") as f:
        data = json.load(f)
    expat = pd.json_normalize(data)
    expat.columns = ['city_ascii', 'country', 'beer_market', 'bread', 'coffee', 'beer_pub']

    return expat


def n_e_correct(n_e):
    # corrections prior to merging with city_data
    corrections = [['Newcastle', "Newcastle"],
                   ["Penang", "George Town"],
                   ['Heraklion', 'Irakleio'],
                   ['Ahmedabad', 'Ahmadabad'],
                   ['Patras', 'Patra'],
                   ['Pattaya', 'Phatthaya'],
                   ['Visakhapatnam', 'Vishakhapatnam'],
                   ['Hanover', 'Hannover'],
                   ['Yangon', 'Rangoon'],
                   ['Rostov', 'Rostov'],
                   ["Goa", "Panaji"],
                   ['Ain', "Al `Ayn"],
                   ["Santa Cruz", "Santa Cruz"],
                   ["Ajman", "`Ajman"],
                   ['Chittagong', 'Chattogram'],
                   ['Macao', 'Macau'],
                   ['Marsa', 'La Marsa'],
                   ['Astana', 'Nur-Sultan'],
                   ["Seville", "Sevilla"],
                   ["Zaporizhzhya", "Zaporizhzhia"]]

    for find, edit in corrections:
        n_e = clean(n_e, find_str=find, edit_str=edit)

    n_e.loc[n_e.city_ascii.str.contains("Rangoon"), "country"] = "Burma"
    n_e.loc[n_e.city_ascii.str.contains("Macau"), "country"] = "Macau"

    n_e.loc[n_e.country.str.contains("Cz"), "country"] = "Czechia"
    n_e.loc[n_e.country.str.contains("Mace"), "country"] = "Macedonia"
    n_e.loc[n_e.country.str.contains("Ivory"), "country"] = "Côte D’Ivoire"

    return n_e


cols = ["city_ascii", 'country', 'region', 'latitude', 'longitude', 'population', 'admin_name']
admin_cols = ['city_ascii',
              'admin_name',
              'country',
              'region',
              'latitude',
              'longitude',
              'population',
              'beer_market_n',
              'bread_n',
              'coffee_n',
              'beer_pub_n',
              'beer_market_e',
              'bread_e',
              'coffee_e',
              'beer_pub_e',
              ]


def state_unabbr(state):
    '''For US cities, generate a list of unabbreviated state names.'''
    abbr = pd.read_table("../city-data/us-state-abbr.tsv", names=['abbr', 'name'], header=0)
    name = abbr.loc[abbr['abbr'] == state, 'name']
    if len(name) > 0:
        return name.values[0]
    else:
        return np.nan


def state_gen(split):
    states = []
    for i in split:
        if i[-1] == "United States":
            states.append(state_unabbr(i[1]))

    states.append("Florida")

    return states


def us_merge(states, n_e, city_data):
    '''For US cities, add states under admin_name, then merge with city_data latitude, longitude, region, and population.'''
    numbeo_us = n_e[n_e['country'] == 'United States']
    numbeo_us["admin_name"] = states

    numbeo_us = pd.merge(numbeo_us, city_data[cols], how='left', on=['city_ascii', 'country', 'admin_name'])
    numbeo_us = numbeo_us.reindex(columns=admin_cols)

    return numbeo_us


def globe_merge(n_e, city_data):
    # for non-US cities, don't match on admin_name
    numbeo_globe = n_e[n_e['country'] != "United States"]

    numbeo_globe = pd.merge(numbeo_globe, city_data[cols], how='left', on=['city_ascii', 'country'])
    numbeo_globe = numbeo_globe.reindex(columns=admin_cols)

    return numbeo_globe


def dedupe(n_e, numbeo_globe):
    # rows where city & country had more than one match in city_data
    x = n_e[n_e['country'] != "United States"]
    indices = []
    for city, country in zip(x['city_ascii'], x['country']):
        y = numbeo_globe.loc[(numbeo_globe.city_ascii == city) & (numbeo_globe.country == country)]
        if len(y) != 1:
            max_pop = y.population.max()
            index = y[y.population != max_pop].index
            indices.append(index[0])

    return indices


def get_city_wikidata(city, country):
    query = """
    SELECT ?city ?cityLabel ?country ?countryLabel ?population
    WHERE
    {
      ?city rdfs:label '%s'@en.
      ?city wdt:P1082 ?population.
      ?city wdt:P17 ?country.
      ?city rdfs:label ?cityLabel.
      ?country rdfs:label ?countryLabel.
      FILTER(LANG(?cityLabel) = "en").
      FILTER(LANG(?countryLabel) = "en").
      FILTER(CONTAINS(?countryLabel, "%s")).
    }
    """ % (city, country)

    res = qwikidata.sparql.return_sparql_query_results(query)
    out = res['results']['bindings'][0]
    return out


def get_region(country):
    region = numbeo_globe.loc[numbeo_globe.country.str.contains(country), "region"]
    return region.dropna().unique()[0]


def find_lost(lost):
    with Session() as s:
        for row in lost.values:
            city = row[0]
            country = row[2]
            try:
                lost.loc[lost.city_ascii == city, "region"] = get_region(country)

                latlng = geocoder.osm(city + ", " + country, session=s).latlng
                if latlng:
                    lost.loc[lost.city_ascii == city, 'latitude'] = latlng[0]
                    lost.loc[lost.city_ascii == city, "longitude"] = latlng[1]

                wikidata = get_city_wikidata(city, country)
                lost.loc[lost.city_ascii == city, "population"] = int(wikidata['population']['value'])
            except:
                pass
            time.sleep(1)
    return lost


def main():
    numbeo = read_numbeo()
    city_data = read_city_data()

    # create a separate country column
    split = numbeo['city'].str.split(", ")
    numbeo['country'] = split.str[-1]
    numbeo['city'] = split.str[0]

    # to align with city_data column names
    numbeo = numbeo.rename(columns={"city": "city_ascii"})

    numbeo = numbeo_correct(numbeo)
    expat = read_expat()

    # merge expatistan and numbeo data
    on_cols = ['city_ascii', 'country']
    n_e = pd.merge(numbeo, expat, how="outer", on=on_cols, suffixes=("_n", "_e"))
    n_e = n_e_correct(n_e)

    # separate numbeo into US and non-US cities
    states = state_gen(split)
    n_us = us_merge(states, n_e, city_data)
    n_g = globe_merge(n_e, city_data)
    # dedupe those rows
    n_g = n_g.drop(index=dedupe(n_e, n_g))

    lost = n_g[np.isnan(n_g['latitude']) | np.isnan(n_g['population'])]
    lost = find_lost(lost)

    for i in range(len(lost)):
        row = lost.iloc[i]
        index = row.name
        n_g[n_g.index == index] = row.values

    n_e_clean = pd.concat([n_us, n_g], ignore_index=True)

    # n_e_clean.index = list(range(len(n_e_clean)))
    n_e_clean.to_csv("n_e_clean_py.csv")
    n_e_clean.to_json("n_e_clean_py.json")


if __name__ == "__main__":
    main()
