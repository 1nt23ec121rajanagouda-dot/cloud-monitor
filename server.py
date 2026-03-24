from flask import Flask, request

app = Flask(__name__)

@app.route('/data', methods=['POST'])
def receive_data():
    data = request.json
    print("Received Data:", data)
    
    # Save to file
    with open("data.txt", "a") as f:
        f.write(str(data) + "\n")

    return {"status": "success"}
@app.route('/api/data')
def get_data():
    with open("data.txt", "r") as f:
        lines = f.readlines()

    data_list = [eval(line.strip()) for line in lines]

    systems = {}

    for entry in data_list:
        node = entry.get("node", "unknown")

        if node == "unknown":
            continue

        if node not in systems:
            systems[node] = []

        systems[node].append(entry)

    return systems

@app.route('/')
def dashboard():
    return """
    <html>
    <head>
        <title>System Dashboard</title>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
            body {
                font-family: Arial;
                background: #f4f6f8;
                text-align: center;
            }
            h1 {
                margin-top: 20px;
            }
            .cards {
                display: flex;
                justify-content: center;
                gap: 20px;
                margin: 20px;
            }
            .card {
                background: white;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                width: 150px;
            }
            canvas {
                margin: 20px auto;
                display: block;
                max-width: 800px;
            }
            .system-box {
                background: white;
                margin: 10px auto;
                padding: 10px;
                border-radius: 10px;
                width: 300px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            }
        </style>
    </head>
    <body>

        <h1>🚀 System Monitoring Dashboard</h1>

        <!-- 🚨 ALERT BOX -->
        <div id="alertBox" style="color:red; font-weight:bold; margin:10px;"></div>

        <!-- 🔽 DROPDOWN -->
        <select id="systemSelect" style="padding:10px; margin:10px;"></select>

        <!-- 🖥 MULTI SYSTEM DISPLAY -->
        <div id="systems"></div>

        <!-- 📊 CARDS -->
        <div class="cards">
            <div class="card">
                <h3>CPU</h3>
                <p id="cpuValue">0%</p>
            </div>
            <div class="card">
                <h3>Memory</h3>
                <p id="memoryValue">0%</p>
            </div>
            <div class="card">
                <h3>Disk</h3>
                <p id="diskValue">0%</p>
            </div>
        </div>

        <!-- 📈 GRAPHS -->
        <canvas id="cpuChart"></canvas>
        <canvas id="memoryChart"></canvas>
        <canvas id="diskChart"></canvas>

        <script>
            const cpuChart = new Chart(document.getElementById('cpuChart').getContext('2d'), {
                type: 'line',
                data: { labels: [], datasets: [{ label: 'CPU', data: [] }] }
            });

            const memoryChart = new Chart(document.getElementById('memoryChart').getContext('2d'), {
                type: 'line',
                data: { labels: [], datasets: [{ label: 'Memory', data: [] }] }
            });

            const diskChart = new Chart(document.getElementById('diskChart').getContext('2d'), {
                type: 'line',
                data: { labels: [], datasets: [{ label: 'Disk', data: [] }] }
            });

            async function fetchData() {
                const res = await fetch('/api/data');
                const systems = await res.json();

                const select = document.getElementById("systemSelect");

                // Fill dropdown once
                if (select.options.length === 0) {
                    for (let node in systems) {
                        const option = document.createElement("option");
                        option.value = node;
                        option.text = node;
                        select.appendChild(option);
                    }
                }

                // Show all systems
                let html = "";
                for (let node in systems) {
                    const data = systems[node];
                    const last = data[data.length - 1];

                    html += `
                        <div class="system-box">
                            <h3>${node}</h3>
                            <p>CPU: ${last.cpu}%</p>
                            <p>Memory: ${last.memory}%</p>
                            <p>Disk: ${last.disk}%</p>
                        </div>
                    `;
                }
                document.getElementById("systems").innerHTML = html;

                // Selected system
                const selectedNode = select.value;
                if (!selectedNode) return;

                const result = systems[selectedNode];

                const labels = result.map((_, i) => i);

                const cpu = result.map(d => d.cpu);
                const memory = result.map(d => d.memory);
                const disk = result.map(d => d.disk);

                cpuChart.data.labels = labels;
                cpuChart.data.datasets[0].data = cpu;

                memoryChart.data.labels = labels;
                memoryChart.data.datasets[0].data = memory;

                diskChart.data.labels = labels;
                diskChart.data.datasets[0].data = disk;

                cpuChart.update();
                memoryChart.update();
                diskChart.update();

                const last = result[result.length - 1];

                // 🚨 ALERT LOGIC
                if (last.cpu > 80) {
                    document.getElementById("alertBox").innerText =
                        "⚠️ High CPU usage on " + selectedNode;
                } else {
                    document.getElementById("alertBox").innerText = "";
                }

                document.getElementById('cpuValue').innerText = last.cpu + "%";
                document.getElementById('memoryValue').innerText = last.memory + "%";
                document.getElementById('diskValue').innerText = last.disk + "%";
            }

            setInterval(fetchData, 3000);
        </script>

    </body>
    </html>
    """

import os
port = int(os.environ.get("PORT", 5005))
app.run(host='0.0.0.0', port=port)