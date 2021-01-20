let mymap = L.map('mapid').setView([51.505, -0.09], 2);

const Esri_WorldStreetMap = L.tileLayer(
  'https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}', {
    attribution: 'Tiles &copy; Esri &mdash; Source: Esri, DeLorme, NAVTEQ, USGS, Intermap, iPC, NRCAN, Esri Japan, METI, Esri China (Hong Kong), Esri (Thailand), TomTom, 2012'
  });

Esri_WorldStreetMap.addTo(mymap);

const markers = new Array();
const mark = function (coords, popup) {
  const c = L.circle(coords, {
    color: 'red',
    fillColor: 'red',
    radius: 1000
  });

  c.bindPopup(popup);
  markers.push(c);
}

function between(marker, bounds) {
  const lat = [bounds.getSouth(), bounds.getNorth()];
  const lng = [bounds.getWest(), bounds.getEast()];
  const m_latlng = marker.getLatLng();
  if (m_latlng.lat >= lat[0] && m_latlng.lat <= lat[1] && m_latlng.lng >= lng[0] &&
    m_latlng.lng <= lng[1]) {
    return true;
  } else {
    return false;
  }
}

function onMapZoom(e) {
  const bounds = mymap.getBounds();
  // console.log(bounds);
  let inbounds = new Array();
  for (const m of markers) {
    m.remove()
    if (between(m, bounds)) {
      inbounds.push(m);
    }
  }
  inbounds.sort((a, b) => inbounds_sort(b) - inbounds_sort(a));
  console.log(inbounds);
  for (const x of inbounds.slice(0, 50)) {
    x.addTo(mymap);
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

let db_beer;
fetch('http://localhost:8000/data/deutschebank/beer-clean.json', {
    mode: 'same-origin'
  })
  .then(response => response.json())
  .then(data => {
    console.log(data);
    db_beer = parse(data);
    for (const x of db_beer) {
      mark([x.latitude, x.longitude], String(x.population));
    }
    for (const y of markers) {
      y.addTo(mymap);
    }
  });

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

// circle.bindPopup(html, {
//   minWidth: 400
// })
