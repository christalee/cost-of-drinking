let mymap = L.map('mapid').setView([51.505, -0.09], 2);

const Esri_WorldStreetMap = L.tileLayer(
  'https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}', {
    attribution: 'Tiles &copy; Esri &mdash; Source: Esri, DeLorme, NAVTEQ, USGS, Intermap, iPC, NRCAN, Esri Japan, METI, Esri China (Hong Kong), Esri (Thailand), TomTom, 2012'
  });

Esri_WorldStreetMap.addTo(mymap);

// const marker = L.marker([51.5, 0.0]).addTo(mymap);
const circle = L.circle([51.508, -0.11], {
  color: 'red',
  fillColor: 'red',
  radius: 1000
}).addTo(mymap);

const mark = function (coords) {
  const c = L.circle(coords, {
    color: 'red',
    fillColor: 'red',
    radius: 1000
  }).addTo(mymap);

  return c;
}

const locations = new Array();
for (x = 0; x <= 50; x += 1) {
  locations[x] = [Math.random() * 10, Math.random() * 10];
}
locations.forEach(mark);

const html =
  `<!DOCTYPE html>
<html>
<head>
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
</body>
</html>`
circle.bindPopup(html, {
  minWidth: 120
})
