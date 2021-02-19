// Start by instantiating a map and using ESRI tiles
let mymap = L.map('mapid').setView([0, 0], 2);

const Esri_WorldStreetMap = L.tileLayer(
  'https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}', {
    attribution: 'Tiles &copy; Esri &mdash; Source: Esri, DeLorme, NAVTEQ, USGS, Intermap, iPC, NRCAN, Esri Japan, METI, Esri China (Hong Kong), Esri (Thailand), TomTom, 2012'
  });

Esri_WorldStreetMap.addTo(mymap);

// create all the markers and collect them in an array
let markers;

function mark(coords, popup, color) {
  const c = L.circleMarker(coords, {
    weight: 1,
    color: "black",
    fillColor: color,
    fillOpacity: 1,
    radius: 4
  });

  c.bindPopup(popup);
  markers.push(c);
}

const colors = ['#ffffd4', '#fed98e', '#fe9929', '#d95f0e', '#993404'];
let bins;

function make_bins(data) {
  bins = new Array();
  let prices = new Array();
  for (const x of data) {
    prices.push(x.total);
  }
  const price_range = [Math.min(...prices), Math.max(...prices)]
  const price_interval = (price_range[1] - price_range[0]) / 4;
  for (let x = 0; x < 5; x += 1) {
    let cut = Math.round((price_range[0] + x * price_interval) * 100) / 100;
    bins.push(cut);
  }
}

// A helper fn to return the appropriate color for each band of prices
function m_color(val) {
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

  // loop through our density intervals and generate a label with a colored square
  // for each interval
  for (let i = 0; i < colors.length; i++) {
    div.innerHTML += '<i style="background: ' + colors[i] + '"></i> ' +
      String(bins[i]) + (bins[i + 1] ? ' &ndash; ' + String(bins[i + 1]) +
        '<br>' : '+');
  }

  return div;
};

// To filter the markers on the screen to the top cities by population,
// you need a list of what's currently on the screen, and a way to sort them
function between(marker, bounds) {
  const lat = [bounds.getSouth(), bounds.getNorth()];
  const lng = [bounds.getWest(), bounds.getEast()];
  const m_latlng = marker.getLatLng();
  if (m_latlng.lat >= lat[0] && m_latlng.lat <= lat[1] && m_latlng.lng >=
    lng[0] &&
    m_latlng.lng <= lng[1]) {
    return true;
  } else {
    return false;
  }
}

function inbounds_sort(marker) {
  const latlng = marker.getLatLng();
  for (const x of df) {
    if (latlng.lat === x.latitude && latlng.lng === x.longitude) {
      return x.population;
    }
  }
}

function onMapZoom(e) {
  const bounds = mymap.getBounds();
  let inbounds = new Array();
  for (const m of markers) {
    m.remove()
    if (between(m, bounds)) {
      inbounds.push(m);
    }
  }
  inbounds.sort((a, b) => inbounds_sort(b) - inbounds_sort(a));
  for (const x of inbounds.slice(0, 300)) {
    x.addTo(mymap);
  }
}

mymap.on("load", onMapZoom);
mymap.on("zoomend", onMapZoom);
mymap.on("moveend", onMapZoom);

const labels = ['avg_pub', 'avg_market', 'avg_bread', 'avg_coffee'];
let isChecked;

function layerAdd() {
  isChecked = new Array();
  for (const l of document.getElementsByClassName(
      "leaflet-control-layers-selector")) {
    if (l.checked) {
      isChecked.push(l.nextSibling.firstChild.data);
    }
  }
  if (isChecked.length === 0) {
    markData(df);
  } else {
    markData(sliceData());
  }
}

function markerSelect(labels) {
  let m = new Map();
  for (const l of labels) {
    m.set(l, L.featureGroup(markers)
      .on('add', layerAdd)
      .on('remove', layerAdd)
    );
  }

  return Object.fromEntries(m);
}

let layers = markerSelect(labels);

let raw;
let df;

// Creates an array of objects, each containing 1 row of data
function parse(json) {
  const x = Object.entries(json);
  const y = Object.entries(x[0][1]);
  let a = new Array();
  for (let i = 0; i < y.length; i += 1) {
    let b = new Object();
    for (const [k, v] of x) {
      b[k] = v[i];
    }
    a.push(b);
  }

  return a;
};

function sliceData() {
  let data = new Array();
  for (let i in raw['city_ascii']) {
    let x = new Object();
    for (const k of ['city_ascii', 'latitude', 'longitude', 'population']) {
      x[k] = raw[k][i];
    }
    x['total'] = 0;
    for (const j of isChecked) {
      x['total'] += raw[j.trim()][i];
    }
    data.push(x);
  }

  return data;
}

function markData(data) {
  make_bins(data);
  legend.remove();
  legend.addTo(mymap);
  markers = new Array();
  for (const x of data) {
    let text = String(x.city_ascii) + ": " + String(x.total);
    mark([x.latitude, x.longitude], text, m_color(x.total));
  }
  for (const y of markers) {
    y.addTo(mymap);
  }
}

// Fetches the JSON and dumps it into variables for later use,
// also draws the markers
window.onload = function () {
  fetch(
      'http://localhost:3000/df_final.json', {
        mode: 'same-origin'
      })
    .then(response => response.json())
    .then(data => {
      raw = data;
      df = parse(data);
      markData(df);
      L.control.layers(null, layers).addTo(mymap);
    });
}
