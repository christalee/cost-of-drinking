# Cost of Drinking
## What this project is

- An excuse to scrape and clean some data with pandas, process and map it with Leaflet.JS, and review event handling in JavaScript, with a visually attractive result.
- A naive look at the cost of beer, coffee, and bread around the world, based on crowdsourced data.

## What this project is not

- A serious analysis of global cost of living. Please do not base any life decisions, like where to travel or move, on this visualization.
- A non-biased set of metrics. I considered major beverages of the world (beer, coffee, tea), but couldn't find good data on tea. I considered major fermented products (beer, wine, bread, cheese) but decided that was too Eurocentric. Beer, coffee, and bread is still fairly Eurocentric, but coffee is a cultural staple in some African and Middle Eastern cultures, and I hope the bread prices reflect local bread not white sandwich loaves.
- Reliable data. Since this is crowdsourced data, I can't be sure what anyone was referring to when they entered it: cheap lager, Guinness, local craft brew (probably not!). I also don't know when it was entered, what the exchange rate was on that day, or whether they transposed any digits. So I can't control for inflation, or do sophisticated analysis of purchasing power.

## Motivation

A throwaway comment on the price of beer in Budapest inspired me to see if beer could be used as a cost of living metric. The first articles I found polled a single city per country, typically the capital or largest city, which seemed unrepresentative: everyone knows the cost of living is high in New York, Tokyo, or London. So I wanted to gather data by city, average it across various sources, and map it. Since beer is not globally popular, though (in Saudi Arabia, it's illegal), I decided to expand my analysis to coffee, which is widely available even in non-coffee cultures, and bread, since everyone needs something to nibble on with their beer. (In my household, we make some of our beer and bake some of our bread; we do not roast our own coffee.) I hope the results are entertaining and thought-provoking.

## Sources
### City Data (by [apettenati](https://github.com/apettenati))
- City, Country, Latitude, Longitude, and Population data sourced from [Simple Maps](https://simplemaps.com/data/world-cities)
- Region data sourced from [Wikimedia](https://meta.wikimedia.org/wiki/List_of_countries_by_regional_classification)
- City ASCII column used for merging datasets

### Deutsche Bank (by [apettenati](https://github.com/apettenati))
- Data gathered from [Mapping the World Prices 2019](https://www.dbresearch.com/PROD/RPS_EN-PROD/Mapping_the_world_prices_2019/RPS_EN_DOC_VIEW.calias?rwnode=PROD0000000000436748&ProdCollection=PROD0000000000505140):
  - cappuccino
  - 500 mL beer in neighbourhood pub

### [Expatistan](https://www.expatistan.com/) (by [apettenati](https://github.com/apettenati))
- Data gathered January 2021 on:
  - bread for 2 people for 1 day
  - cappuccino in expat area of the city
  -	500 mL or 16 oz. beer in neighbourhood pub
  - 500 mL or 16 oz. domestic beer in the supermarket
- Expatistan data used with permission.

### Numbeo
- Data gathered January 2021 on:
  - [cappuccino in cafes](https://www.numbeo.com/cost-of-living/prices_by_city.jsp?displayCurrency=USD&itemId=114)
  - [500 mL beer in markets](https://www.numbeo.com/cost-of-living/prices_by_city.jsp?displayCurrency=USD&itemId=15)
  - [500 mL beer in restaurants](https://www.numbeo.com/cost-of-living/prices_by_city.jsp?displayCurrency=USD&itemId=4)
  - [500 g bread in markets](https://www.numbeo.com/cost-of-living/prices_by_city.jsp?displayCurrency=USD&itemId=9)

### [PintPrice](http://www.pintprice.com/index.php)
- Data gathered January 2021 on the price of 16 oz. / 500 mL beer, presumably in a neighbourhood pub

<a href='http://www.recurse.com' title='Made with love at the Recurse Center'><img src='https://cloud.githubusercontent.com/assets/2883345/11325206/336ea5f4-9150-11e5-9e90-d86ad31993d8.png' height='20px'/></a>
