from flask import Flask, render_template, request
import sqlite3
from datetime import datetime

app = Flask(__name__)


def get_status(value):
    if value <= 60:
        return "Healthy", "green"
    elif value <= 80:
        return "Warning", "orange"
    else:
        return "Critical", "red"


@app.route("/")
def home():

    connection = sqlite3.connect("monitor.db")
    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM system_metrics s1
        WHERE id = (
            SELECT MAX(id)
            FROM system_metrics s2
            WHERE s1.hostname = s2.hostname
        )
        ORDER BY hostname;
    """)

    rows = cursor.fetchall()
    connection.close()

    if len(rows) == 0:
        return "No data available."

    servers = []

    overall_status = "Healthy"
    overall_color = "green"

    for row in rows:

        timestamp = row[1]

        hostname = row[2]
        cpu = row[3]
        ram = row[4]
        disk = row[5]

        last_seen = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
        current_time = datetime.utcnow()
        difference = (current_time - last_seen).total_seconds()

        print(hostname, difference)

        # ----------------------------
        # OFFLINE DETECTION
        # ----------------------------

        if difference > 15:

            status = "Offline"
            color = "gray"

        else:

            cpu_status, cpu_color = get_status(cpu)
            ram_status, ram_color = get_status(ram)
            disk_status, disk_color = get_status(disk)

            if (
                cpu_status == "Critical"
                or ram_status == "Critical"
                or disk_status == "Critical"
            ):

                status = "Critical"
                color = "red"

            elif (
                cpu_status == "Warning"
                or ram_status == "Warning"
                or disk_status == "Warning"
            ):

                status = "Warning"
                color = "orange"

            else:

                status = "Healthy"
                color = "green"

        if status == "Critical":

            overall_status = "Critical"
            overall_color = "red"

        elif status == "Warning" and overall_status != "Critical":

            overall_status = "Warning"
            overall_color = "orange"

        elif status == "Offline" and overall_status == "Healthy":

            overall_status = "Warning"
            overall_color = "orange"

        servers.append({

            "hostname": hostname,
            "cpu": cpu,
            "ram": ram,
            "disk": disk,
            "status": status,
            "color": color,
            "last_seen": timestamp

        })

    return render_template(
        "index.html",
        servers=servers,
        overall_status=overall_status,
        overall_color=overall_color
    )


@app.route("/api/metrics", methods=["POST"])
def receive_metrics():

    data = request.get_json()

    connection = sqlite3.connect("monitor.db")
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO system_metrics(hostname, cpu, ram, disk)
        VALUES (?, ?, ?, ?)
    """, (
        data["hostname"],
        data["cpu"],
        data["ram"],
        data["disk"]
    ))

    connection.commit()
    connection.close()

    return {"message": "Metrics received successfully"}, 200
@app.route("/history/<hostname>")
def history(hostname):

    connection = sqlite3.connect("monitor.db")
    cursor = connection.cursor()

    cursor.execute("""
        SELECT timestamp, cpu, ram, disk
        FROM system_metrics
        WHERE hostname = ?
        ORDER BY id DESC
        LIMIT 20
    """, (hostname,))

    rows = cursor.fetchall()

    connection.close()

    rows.reverse()

    return {
        "timestamps": [r[0] for r in rows],
        "cpu": [r[1] for r in rows],
        "ram": [r[2] for r in rows],
        "disk": [r[3] for r in rows]
    }

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
