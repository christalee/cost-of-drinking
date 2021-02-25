// Start by instantiating a map and using ESRI tiles
let myMap = L.map('mapid').setView([0, 0], 1);

const Esri_WorldStreetMap = L.tileLayer(
  'https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}', {
    attribution: 'Tiles &copy; Esri &mdash; Source: Esri, DeLorme, NAVTEQ, USGS, Intermap, iPC, NRCAN, Esri Japan, METI, Esri China (Hong Kong), Esri (Thailand), TomTom, 2012'
  });

const CartoDB_Positron = L.tileLayer(
  'https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
    subdomains: 'abcd',
    maxZoom: 19
  })
Esri_WorldStreetMap.addTo(myMap);
// CartoDB_Positron.addTo(myMap);

// create bins and assign colors for legend
const colors = ['#ffffd4', '#fed98e', '#fe9929', '#d95f0e', '#993404'];
let total_bins;

function make_bins(data) {
  total_bins = new Array();
  let prices = new Array();
  for (const row of data) {
    prices.push(row.total);
  }
  const price_range = [Math.min(...prices), Math.max(...prices)]
  const price_interval = (price_range[1] - price_range[0]) / 4;
  for (let x = 0; x < 5; x += 1) {
    let cut = Math.round((price_range[0] + x * price_interval) * 100) / 100;
    total_bins.push(cut);
  }
}

// A helper fn to return the appropriate color for each band of prices
function mark_color(val, bins) {
  if (val >= bins[0] && val < bins[1]) {
    return colors[0];
  }
  if (val >= bins[1] && val < bins[2]) {
    return colors[1];
  }
  if (val >= bins[2] && val < bins[3]) {
    return colors[2];
  }
  if (val >= bins[3] && val < bins[4]) {
    return colors[3];
  } else {
    return colors[4];
  }
}

let legend = L.control({
  position: 'bottomright'
});

legend.onAdd = function (map) {
  let div = L.DomUtil.create('div', 'info legend');

  // loop through our density intervals and generate a label
  // with a colored square for each interval
  for (let i = 0; i < colors.length; i++) {
    div.innerHTML += '<i style="background: ' + colors[i] + '"></i> ' +
      String(total_bins[i]) + (total_bins[i + 1] ? ' &ndash; ' + String(total_bins[i + 1]) +
        '<br>' : '+');
  }

  return div;
};

// create all the markers and collect them in an array
let markers;

function mark(coords, text, color) {
  const circle = L.circleMarker(coords, {
    weight: 1,
    color: "black",
    fillColor: color,
    fillOpacity: 1,
    radius: 4,
    alt: text
  });
  p = L.popup(circle).setContent(`<div id="info-pane" class="chart-container"><canvas id="${text}"></canvas></div>`);
  circle.bindPopup(p);
  markers.push(circle);
}

// To filter the markers on the screen to the top cities by population,
// you need a list of what's currently on the screen, and a way to sort them
function between(marker, bounds) {
  const lat = [bounds.getSouth(), bounds.getNorth()];
  const lng = [bounds.getWest(), bounds.getEast()];
  const mark_latlng = marker.getLatLng();
  if (mark_latlng.lat >= lat[0] && mark_latlng.lat <= lat[1] && mark_latlng.lng >=
    lng[0] && mark_latlng.lng <= lng[1]) {
    return true;
  } else {
    return false;
  }
}

// sort by population
function inbounds_sort(marker) {
  const mark_latlng = marker.getLatLng();
  for (const row of df) {
    if (mark_latlng.lat === row.latitude && mark_latlng.lng === row.longitude) {
      return row.population;
    }
  }
}

// generate a list of visible markers and display the top 300 by population
function onMapZoom() {
  const bounds = myMap.getBounds();
  let inbounds = new Array();
  for (const mark of markers) {
    mark.remove()
    if (between(mark, bounds)) {
      inbounds.push(mark);
    }
  }
  inbounds.sort((a, b) => inbounds_sort(b) - inbounds_sort(a));
  for (const mark of inbounds.slice(0, 300)) {
    mark.addTo(myMap);
  }
}

myMap.on("load", onMapZoom)
  .on("zoomend", onMapZoom)
  .on("moveend", onMapZoom)
  .on("popupopen", popupChart);

// create layers for each data metric
const labels = ['beer @ pub', 'beer @ market', 'bread @ market',
  'coffee @ cafe']
const keys = ['avg_pub', 'avg_market', 'avg_bread', 'avg_coffee'];
let layersToKeys = new Map();
for (const i in labels) {
  layersToKeys.set(labels[i], keys[i]);
}

let isChecked;

// populate isChecked from currently checked boxes and update the markers
function layerUpdate() {
  isChecked = new Array();
  for (const layer of document.getElementsByClassName(
      "leaflet-control-layers-selector")) {
    if (layer.checked) {
      isChecked.push(layer.nextSibling.firstChild.data);
    }
  }
  if (isChecked.length === 0) {
    markData(df);
  } else {
    markData(sliceData());
  }
  onMapZoom();
}

// create the layer selector label object
function markerSelect(labels) {
  let mark_group = new Map();
  for (const lbl of labels) {
    mark_group.set(lbl, L.featureGroup(markers)
      .on('add', layerUpdate)
      .on('remove', layerUpdate)
    );
  }

  return Object.fromEntries(mark_group);
}

let layers = markerSelect(labels);

// get ready to parse some data!!
let raw;
let df;

// Creates an array of objects, each containing 1 row of data
function parse(json) {
  const json_obj = Object.entries(json);
  const indices = Object.entries(json_obj[0][1]);
  let data = new Array();
  for (let i = 0; i < indices.length; i += 1) {
    let row = new Object();
    for (const [k, v] of json_obj) {
      row[k] = v[i];
    }
    data.push(row);
  }

  return data;
};

// when boxes get checked, generate a corresponding data series
function sliceData() {
  let data = new Array();
  for (let i in raw['city_ascii']) {
    let row = new Object();
    for (const k of ['city_ascii', 'latitude', 'longitude', 'population']) {
      row[k] = raw[k][i];
    }
    row['total'] = 0;
    for (const label of isChecked) {
      row['total'] += raw[layersToKeys.get(label.trim())][i];
    }
    data.push(row);
  }

  return data;
}

function popupChart(e) {
  const city = e.popup.options.options.alt;
  let chart = new Chart(city, {
    type: 'bar',
    data: initialChartData(city),
    options: chartOptions
  });
}

// given some data, update the legend and plot the markers
function markData(data) {
  make_bins(data);
  legend.remove();
  legend.addTo(myMap);
  markers = new Array();
  for (const row of data) {
    mark([row.latitude, row.longitude], row.city_ascii, mark_color(row.total, total_bins));
  }
  for (const mark of markers) {
    mark.addTo(myMap);
  }
}

let dfMinMax = new Map();
function minmax () {
  let totalMin = 0;
  let totalMax = 0;
  for (const k of keys) {
    let prices = new Array();
    for (const i in raw[k]) {
      prices.push(raw[k][i]);
    }
    let price_range = [Math.min(...prices), Math.max(...prices)];
    totalMin += price_range[0];
    totalMax += price_range[1];
    // console.log(price_range);
    dfMinMax.set(k, price_range);
  }
  dfMinMax.set("total", [totalMin, totalMax]);
}

let dfBins = new Map();
function chartBins() {
  for (const k of keys) {
    let bins = new Array();
    price_range = dfMinMax.get(k);
    const price_interval = (price_range[1] - price_range[0]) / 4;
    for (let x = 0; x < 5; x += 1) {
      let cut = Math.round((price_range[0] + x * price_interval) * 100) / 100;
      bins.push(cut);
    }
    dfBins.set(k, bins);
  }
}

function chartColors (data) {
  let colors = new Array();
  for (const i in data) {
    bins = dfBins.get(keys[i]);
    colors.push(mark_color(data[i], bins));
  }

  return colors;
}

function initialChartData (city) {
  let data = new Array();

  for (const row of df) {
    if (row.city_ascii == city) {
      for (const k of keys) {
        data.push(row[k]);
      }
      cColors = chartColors(data);
    }
  }
return {
  labels: labels,
   datasets: [{
     label: city,
     backgroundColor: cColors,
     borderColor: "#000000",
     borderWidth: 1,
     data: data
   }
 ]};}

const chartOptions = {
  scales: {
      xAxes: [{
        // stacked: true,
        scaleLabel: {
          display: true,
          labelString: 'products'
        },
        ticks: {
          beginAtZero: true,
          // max: 250,
          // stepSize: 50
        }
      }],
      yAxes: [{
        // stacked: true,
        scaleLabel: {
          display: true,
          labelString: 'cost ($ USD)'
        },
        ticks: {
          beginAtZero: true,
          // max: 250,
          // stepSize: 50
        }
      }]
    },
    maintainAspectRatio: false,
    // turn off animations during chart data updates
    // animation: {
    //   duration: 0
    // }
  };

// Fetches the JSON and dumps it into variables,
// also draws the markers and layer selector
window.onload = function () {
  fetch(
      '../../files/df_final.json', {
        mode: 'same-origin'
      })
    .then(response => response.json())
    .then(data => {
      raw = data;
      myMap.zoomIn(); // this is a hack to trigger onMapZoom initially
      df = parse(data);
      markData(df);
      L.control.layers(null, layers).addTo(myMap);
      minmax();
      chartBins();
    });
}
