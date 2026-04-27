import subprocess
import os
import time
import re
import threading
from flask import Flask, render_template_string, request

app = Flask(__name__)

active_processes = {}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LORD-VENOM</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap');
        
        body { 
            background-color: #0a0a0a; 
            color: #e0e0e0; 
            font-family: 'JetBrains Mono', monospace;
            text-align: center;
            padding: 20px;
            line-height: 1.6;
            margin: 0;
        }
        .container { 
            max-width: 500px;
            margin: 0 auto;
            background: #111;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 0 25px rgba(128, 0, 128, 0.2);
            border: 1px solid #333;
        }
        .header-box {
            border: 2px solid #a020f0;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 20px;
            background: linear-gradient(135deg, #0a0a0a 0%, #1a002e 100%);
        }
        .title { 
            color: #a020f0; 
            font-weight: bold; 
            font-size: 1.8em;
            letter-spacing: 4px;
            margin: 0;
            text-shadow: 0 0 10px #a020f0;
        }
        .subtitle {
            color: #888;
            font-size: 0.7em;
            margin-top: 5px;
            text-transform: uppercase;
        }
        .status-line {
            text-align: left;
            margin: 8px 0;
            font-size: 0.9em;
            color: #aaa;
        }
        .status-line .label {
            color: #a020f0;
            display: inline-block;
            width: 130px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        .status-line .value {
            color: #fff;
        }
        .check {
            color: #a020f0;
        }
        .divider {
            border: none;
            border-top: 1px solid #333;
            margin: 20px 0;
        }
        .section-title {
            color: #a020f0;
            font-weight: bold;
            text-align: left;
            margin: 15px 0 10px 0;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 2px;
        }
        .description {
            text-align: left;
            color: #777;
            font-size: 0.85em;
            line-height: 1.8;
        }
        .command-box {
            background: #1a002e;
            border: 1px solid #a020f0;
            border-radius: 5px;
            padding: 15px;
            margin: 15px 0;
            text-align: left;
        }
        .command-name {
            color: #a020f0;
            font-weight: bold;
            font-size: 1.1em;
        }
        .code-display { 
            font-size: 2.2em; 
            color: #a020f0;
            background: #000;
            padding: 20px;
            margin: 20px 0;
            border: 2px solid #a020f0;
            border-radius: 5px;
            letter-spacing: 8px;
            font-weight: bold;
            box-shadow: inset 0 0 15px rgba(160, 32, 240, 0.3);
        }
        input { 
            width: 100%; 
            padding: 12px; 
            background: #000;
            color: #a020f0;
            border: 1px solid #444;
            border-radius: 5px;
            margin: 10px 0;
            font-family: 'JetBrains Mono', monospace;
            box-sizing: border-box;
        }
        .btn { 
            background: #a020f0; 
            color: #fff;
            padding: 15px 30px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 1em;
            font-weight: bold;
            width: 100%;
            text-transform: uppercase;
            letter-spacing: 2px;
        }
        .footer {
            margin-top: 20px;
            color: #444;
            font-size: 0.8em;
        }
        .footer .powered {
            color: #a020f0;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header-box">
            <div class="title">LORD-VENOM</div>
            <div class="subtitle">Nexus Intelligence Interface</div>
        </div>

        <div class="status-line">
            <span class="label">CORE STATUS :</span>
            <span class="value check">ONLINE ✓</span>
        </div>

        <hr class="divider">

        {% if pairing_code %}
            <div class="section-title">ENCRYPTED KEY GENERATED</div>
            <div class="code-display">{{ pairing_code }}</div>
            <a href="/" style="color: #a020f0; text-decoration: none; display: block; margin-top: 20px;">← RETURN TO CORE</a>
        {% else %}
            <div class="section-title">CONNECT DEVICE</div>
            <form method="POST">
                <input type="text" name="number" placeholder="234xxxxxxxxxx" required>
                <button type="submit" class="btn">Initialize Pairing</button>
            </form>
        {% endif %}

        <div class="footer">
            PROJECT MAINTAINED BY <span class="powered">DESTINY JOB</span>
        </div>
    </div>
</body>
</html>
"""

def extract_pairing_code(line):
    match = re.search(r'VENOM_CODE_START:([A-Z0-9]+):VENOM_CODE_END', line)
    if match: return match.group(1)
    return None

def run_pairing_process(number, session_id):
    # Search for the script in LORD-VENOM folder or root
    script_path = 'LORD-VENOM/pair.js' if os.path.exists('LORD-VENOM/pair.js') else 'pair.js'
    
    try:
        process = subprocess.Popen(['node', script_path, number], stdout=subprocess.PIPE, text=True)
        active_processes[session_id] = {'code': None}
        
        for line in iter(process.stdout.readline, ''):
            code = extract_pairing_code(line)
            if code: active_processes[session_id]['code'] = code
    except Exception as e:
        print(f"Error: {e}")

@app.route('/', methods=['GET', 'POST'])
def home():
    pairing_code = None
    if request.method == 'POST':
        number = re.sub(r'\D', '', request.form.get('number', ''))
        session_id = f"v_{int(time.time())}"
        threading.Thread(target=run_pairing_process, args=(number, session_id)).start()
        
        for _ in range(30):
            if session_id in active_processes and active_processes[session_id]['code']:
                pairing_code = active_processes[session_id]['code']
                break
            time.sleep(0.5)
    return render_template_string(HTML_TEMPLATE, pairing_code=pairing_code)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
