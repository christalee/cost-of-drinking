// Start by instantiating a map and using ESRI tiles
let mymap = L.map('mapid').setView([0, 0], 2);

const Esri_WorldStreetMap = L.tileLayer(
  'https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}', {
    attribution: 'Tiles &copy; Esri &mdash; Source: Esri, DeLorme, NAVTEQ, USGS, Intermap, iPC, NRCAN, Esri Japan, METI, Esri China (Hong Kong), Esri (Thailand), TomTom, 2012'
  });

Esri_WorldStreetMap.addTo(mymap);

// create all the markers and collect them in an array
const markers = new Array();
const mark = function (coords, popup, color) {
  const c = L.circleMarker(coords, {
    weight: 1,
    color: "black",
    fillColor: color,
    fillOpacity: 1,
    radius: 3
  });

  c.bindPopup(popup);
  markers.push(c);
}

// A helper fn to return the appropriate color for each band of prices
const colors = ['#ffffd4', '#fed98e', '#fe9929', '#d95f0e', '#993404'];

let bins = new Array();

function make_bins() {
  const prices = Object.values(raw.price)
  const price_range = [Math.min(...prices), Math.max(...prices)]
  const price_interval = (price_range[1] - price_range[0]) / 4;
  for (let x = 0; x < 5; x += 1) {
    let cut = Math.round((price_range[0] + x * price_interval) * 100) / 100;
    bins.push(cut);
  }
}

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
    // div.innerHTML += '<i style="background:' + colors[i] + '"></i> ' +
    //   bins[i] + (bins[i + 1] ? '&ndash;' + bins[i + 1] + '<br>' : '+');
  }

  return div;
};

// To filter the markers on the screen to the top 50 (?) by population,
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
  for (const x of db_beer) {
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
  for (const x of inbounds.slice(0, 50)) {
    x.addTo(mymap);
  }
}

// mymap.on("load", onMapZoom);
mymap.on("zoomend", onMapZoom);
mymap.on("moveend", onMapZoom);

//
// fetch('http://localhost:8000/graphs/Seoul.html', {
//     mode: 'same-origin'
//   }).then(response => response.text())
//   .then(data => {
//     // console.log(data);
//     circle.bindPopup(html, {
//       minWidth: 400
//     });
//   });

// Creates an array of objects, each containing 1 row of data
function parse(json) {
  const x = Object.entries(json);
  const y = Object.entries(x[0][1]);
  let a = new Array();
  for (let i = 0; i < y.length; i += 1) {
    let b = new Object();
    for (const [k, v] of Object.entries(json)) {
      b[k] = v[i];
    }
    a.push(b);
  }

  return a;
};

// Fetches the JSON and dumps it into variables for later use,
// also draws the markers
let raw;
let db_beer;
fetch(
    'http://localhost:8000/data/deutschebank/beer-clean.json', {
      mode: 'same-origin'
    })
  .then(response => response.json())
  .then(data => {
    raw = data;
    make_bins();

    db_beer = parse(data);
    for (const x of db_beer) {
      let text = String(x.city_ascii) + ": " + String(x.price)
      mark([x.latitude, x.longitude], text, m_color(x.price));
    }
    for (const y of markers) {
      y.addTo(mymap);
    }
    legend.addTo(mymap);
  });

// an effort to figure out how to add charts to popups
const html =
  `<head>
  <style>
    .error {
        color: red;
    }
  </style>
  <script type="text/javascript" src="https://cdn.jsdelivr.net/npm//vega@5"></script>
  <script type="text/javascript" src="https://cdn.jsdelivr.net/npm//vega-lite@4.8.1"></script>
  <script type="text/javascript" src="https://cdn.jsdelivr.net/npm//vega-embed@6"></script>
</head>
<body>
  <div id="vis"></div>
  <script>
    (function(vegaEmbed) {
      var spec = {"config": {"view": {"continuousWidth": 400, "continuousHeight": 300}}, "data": {"name": "data-436c0630e7e4313a1c81d15b3666107b"}, "mark": "bar", "encoding": {"x": {"type": "nominal", "field": "Seoul"}, "y": {"type": "quantitative", "field": "price ($)"}}, "$schema": "https://vega.github.io/schema/vega-lite/v4.8.1.json", "datasets": {"data-436c0630e7e4313a1c81d15b3666107b": [{"Seoul": "beer", "price ($)": 2.44}, {"Seoul": "bread", "price ($)": 2.76}, {"Seoul": "coffee", "price ($)": 4.34}]}};
      var embedOpt = {"mode": "vega-lite"};

      function showError(el, error){
          el.innerHTML = ('<div class="error" style="color:red;">'
                          + '<p>JavaScript Error: ' + error.message + '</p>'
                          + "<p>This usually means there's a typo in your chart specification. "
                          + "See the javascript console for the full traceback.</p>"
                          + '</div>');
          throw error;
      }
      const el = document.getElementById('vis');
      vegaEmbed("#vis", spec, embedOpt)
        .catch(error => showError(el, error));
    })(vegaEmbed);

  </script>
</body>`
