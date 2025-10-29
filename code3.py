from flask import Flask, render_template_string

app = Flask(__name__)

HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Data Viewer</title>
<style>
body {
  font-family: Arial, Helvetica, sans-serif;
  background: #f9fafb;
  margin: 40px;
}
.container {
  width: 900px;
  margin: auto;
  background: white;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 4px 10px rgba(0,0,0,0.1);
}
h2 {
  text-align: center;
  color: #007bff;
}
input[type="file"], input[type="text"], button {
  padding: 10px;
  margin: 6px 0;
  width: 100%;
  border: 1px solid #ccc;
  border-radius: 5px;
  font-size: 14px;
}
button {
  cursor: pointer;
  font-weight: bold;
}
button:hover { opacity: 0.9; }
#runBtn {
  background: #007bff;
  color: white;
}
#sortBtn {
  background: #28a745;
  color: white;
}
table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 20px;
}
th, td {
  border: 1px solid #ddd;
  text-align: center;
  padding: 8px;
}
th {
  background: #007bff;
  color: white;
}
#rowCount {
  margin-top: 10px;
  text-align: right;
  font-weight: bold;
  color: #333;
}
</style>
</head>
<body>
<div class="container">
  <h2>Device Data Viewer</h2>

  <input type="file" id="fileInput">
  <input type="text" id="root1" placeholder="Enter Root 1 (MAC)">
  <input type="text" id="root2" placeholder="Enter Root 2 (MAC)">
  <button id="runBtn" onclick="loadFile()">Run</button>
  <button id="sortBtn" onclick="sortByAvgRSSI()">Sort</button>

  <table id="outputTable">
    <thead>
      <tr>
        <th>MAC</th><th>Rate</th><th>RSSI (Avg)</th><th>Parent</th>
      </tr>
    </thead>
    <tbody></tbody>
  </table>

  <div id="rowCount">Total devices shown: 0</div>
</div>

<script>
let allData = [];
let uniqueData = [];

// Read and process file
function loadFile() {
  const file = document.getElementById('fileInput').files[0];
  if (!file) return alert("Please choose a file!");
  const reader = new FileReader();
  reader.onload = function(e) {
    const lines = e.target.result.split(/\\r?\\n/);
    allData = [];
    for (const line of lines) {
      const m = line.match(/([0-9a-f:]{17})\\s+(\\d+\\.\\d+)\\s+[\\d\\.NA]+\\s+\\d+\\s+([0-9a-f:NA]+)\\s+\\d+\\s+(-?\\d+)/i);
      if (m) {
        allData.push({
          MAC: m[1],
          Rate: parseFloat(m[2]),
          Parent: m[3],
          RSSI: parseFloat(m[4])
        });
      }
    }
    aggregateAndDisplay();
  };
  reader.readAsText(file);
}

// Aggregate by MAC, compute average RSSI, skip roots
function aggregateAndDisplay() {
  const r1 = document.getElementById('root1').value.trim().toLowerCase();
  const r2 = document.getElementById('root2').value.trim().toLowerCase();
  const grouped = {};

  for (const item of allData) {
    const mac = item.MAC.toLowerCase();
    if (mac === r1 || mac === r2) continue; // Skip roots
    if (!grouped[mac]) grouped[mac] = { MAC: item.MAC, Rate: [], RSSI: [], Parent: item.Parent };
    grouped[mac].Rate.push(item.Rate);
    grouped[mac].RSSI.push(item.RSSI);
  }

  uniqueData = Object.values(grouped).map(d => ({
    MAC: d.MAC,
    Rate: (d.Rate.reduce((a,b) => a+b, 0) / d.Rate.length).toFixed(2),
    RSSI: (d.RSSI.reduce((a,b) => a+b, 0) / d.RSSI.length).toFixed(2),
    Parent: d.Parent
  }));

  uniqueData.sort((a,b) => a.MAC.localeCompare(b.MAC));
  display(uniqueData);
}

// Display table and row count
function display(data) {
  const tbody = document.querySelector("#outputTable tbody");
  tbody.innerHTML = "";
  data.forEach(r => {
    const tr = document.createElement("tr");
    tr.innerHTML = `<td>${r.MAC}</td><td>${r.Rate}</td><td>${r.RSSI}</td><td>${r.Parent}</td>`;
    tbody.appendChild(tr);
  });
  document.getElementById("rowCount").textContent = "Total devices shown: " + data.length;
}

// Sort by average RSSI (Descending)
function sortByAvgRSSI() {
  uniqueData.sort((a,b) => parseFloat(b.RSSI) - parseFloat(a.RSSI)); // DESCENDING
  display(uniqueData);
}
</script>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HTML_PAGE)

if __name__ == "__main__":
    print("Starting Flask server…")
    app.run(debug=True)
