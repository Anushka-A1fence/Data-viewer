from flask import Flask, render_template_string, request
import re
from io import TextIOWrapper
import os

app = Flask(__name__)

HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Parent Node Finder</title>
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
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.docsLink {
  text-decoration: none;
  font-size: 14px;
  color: #007bff;
}
input[type="file"], input[type="text"], button {
  padding: 10px;
  margin: 6px 0;
  width: 100%;
  border: 1px solid #ccc;
  border-radius: 8px;
}
button {
  font-size: 16px;
  font-weight: bold;
  cursor: pointer;
  border: none;
  color: white;
}
#runBtn { background-color: #007bff; }
#runBtn:hover { background-color: #0056b3; }
#sortBtn { background-color: #28a745; }
#sortBtn:hover { background-color: #1e7e34; }
#errorMsg {
  color: red;
  font-weight: bold;
  text-align: center;
  margin-top: 10px;
}
table {
  border-collapse: collapse;
  width: 100%;
  margin-top: 20px;
}
th, td {
  text-align: center;
  padding: 8px;
  border-bottom: 1px solid #ddd;
}
th {
  background-color: #007bff;
  color: white;
  cursor: pointer;
}
tfoot {
  font-weight: bold;
  background-color: #f1f1f1;
}
</style>
<script>
function validateMAC(mac) {
  const macFormatRe = /^([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$/;
  return macFormatRe.test(mac);
}

function handleRun() {
  const file = document.getElementById('fileInput').files[0];
  const mac1 = document.getElementById('mac1').value.trim();
  const mac2 = document.getElementById('mac2').value.trim();
  const errorMsg = document.getElementById('errorMsg');
  const output = document.getElementById('output');
  
  if (!file) {
    errorMsg.textContent = "Please select a file!";
    output.innerHTML = "";
    return;
  }
  if ((mac1 && !validateMAC(mac1)) || (mac2 && !validateMAC(mac2))) {
    errorMsg.textContent = "Entered incorrect MAC ID!";
    output.innerHTML = "";
    return;
  }

  errorMsg.textContent = "";

  const formData = new FormData();
  formData.append('file', file);
  formData.append('mac1', mac1);
  formData.append('mac2', mac2);

  fetch('/process', { method: 'POST', body: formData })
    .then(res => res.text())
    .then(html => output.innerHTML = html)
    .catch(err => output.innerHTML = "<p style='color:red;'>Error processing file.</p>");
}

function sortTable() {
  const table = document.querySelector("table");
  const rows = Array.from(table.rows).slice(1, -1);
  const sorted = rows.sort((a, b) => {
    const rssiA = parseFloat(a.cells[6].innerText);
    const rssiB = parseFloat(b.cells[6].innerText);
    return rssiB - rssiA;
  });
  const tbody = table.querySelector("tbody");
  tbody.innerHTML = "";
  sorted.forEach(row => tbody.appendChild(row));
}
</script>
</head>
<body>
  <div class="container">
    <div class="header">
      <h2>Parent Node Finder</h2>
      <a href="/docs" class="docsLink">Documentation</a>
    </div>
    <input type="file" id="fileInput"><br>
    <input type="text" id="mac1" placeholder="Enter Root 1 (MAC)"><br>
    <input type="text" id="mac2" placeholder="Enter Root 2 (MAC)"><br>
    <button id="runBtn" onclick="handleRun()">Run</button>
    <button id="sortBtn" onclick="sortTable()">Sort</button>
    <p id="errorMsg"></p>
    <div id="output"></div>
  </div>
</body>
</html>
"""

def parse_reports(text):
    """Split the file into multiple reports using timestamp lines."""
    # Split on timestamp pattern followed by a blank line
    blocks = re.split(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d+\s*\n\s*\n', text.strip())
    reports = [b.strip() for b in blocks if "MAC" in b]
    return reports

def parse_table(report_text):
    """Parse each report’s table section into structured data."""
    lines = report_text.splitlines()
    data_lines = []
    start_collecting = False
    for line in lines:
        if re.match(r'^[-]{5,}', line):  # line of dashes
            start_collecting = True
            continue
        if start_collecting and line.strip() and not line.startswith("Devices reporting"):
            parts = re.split(r'\s{2,}', line.strip())
            if len(parts) >= 8:
                data_lines.append(parts[:8])
    return data_lines

@app.route('/')
def home():
    return render_template_string(HTML_PAGE)

@app.route('/process', methods=['POST'])
def process_file():
    file = request.files['file']
    mac1 = request.form.get('mac1', '').lower()
    mac2 = request.form.get('mac2', '').lower()

    text = TextIOWrapper(file, encoding='utf-8').read()
    reports = parse_reports(text)
    if not reports:
        return "<p style='color:red;'>No valid reports found in file.</p>"

    latest_report = reports[-1]  # Show only the last one
    rows = parse_table(latest_report)

    # Filter out the entered MACs
    filtered_rows = [r for r in rows if r[0].lower() not in [mac1, mac2]]

    # Generate HTML table
    table_html = """
    <table>
      <thead>
        <tr>
          <th>MAC</th><th>Rate</th><th>IP</th><th>Layer</th>
          <th>Parent</th><th>FW</th><th>RSSI</th><th>Heap</th>
        </tr>
      </thead>
      <tbody>
    """
    for r in filtered_rows:
        table_html += "<tr>" + "".join(f"<td>{cell}</td>" for cell in r) + "</tr>"
    table_html += f"""
      </tbody>
      <tfoot><tr><td colspan="8">Total MAC IDs: {len(filtered_rows)}</td></tr></tfoot>
    </table>
    """
    return table_html


@app.route('/docs')
def docs():
    """Serve the project's docs/README.md at /docs.
    If the `markdown` package is available it will be rendered to HTML; otherwise
    the raw markdown is shown inside a <pre> block.
    """
    docs_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if not os.path.exists(docs_path):
        return "<p style='color:red;'>Docs not found.</p>", 404

    try:
        # Prefer to render Markdown if the module is installed
        import markdown
        with open(docs_path, 'r', encoding='utf-8') as f:
            md = f.read()
        html = markdown.markdown(md, extensions=['fenced_code', 'tables'])
        page = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset='utf-8'>
  <title>Docs</title>
  <style>body{{font-family:Arial, Helvetica, sans-serif;margin:40px}}.container{{max-width:900px;margin:auto;background:white;padding:20px;border-radius:12px;box-shadow:0 4px 10px rgba(0,0,0,0.1)}}</style>
</head>
<body>
  <div class='container'>{html}</div>
</body>
</html>"""
        return page
    except Exception:
        # Fallback: show raw markdown inside a pre block
        with open(docs_path, 'r', encoding='utf-8') as f:
            content = f.read()
        escaped = content.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        page = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset='utf-8'>
  <title>Docs</title>
  <style>body{{font-family:Arial, Helvetica, sans-serif;margin:40px}}.container{{max-width:900px;margin:auto;background:white;padding:20px;border-radius:12px;box-shadow:0 4px 10px rgba(0,0,0,0.1)}}</style>
</head>
<body>
  <div class='container'><pre>{escaped}</pre></div>
</body>
</html>"""
        return page

if __name__ == '__main__':
    app.run(debug=True)
