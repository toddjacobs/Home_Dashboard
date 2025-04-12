from concurrent.futures import ThreadPoolExecutor, as_completed
from flask import Flask, render_template, redirect, url_for
from apis.opnsense_api import OPNsense
import subprocess
import threading
import socket
from apis.arris_api import ArrisModem

router = OPNsense()
router_status = router.interface_status("wan")

app = Flask(__name__)

# Device list
devices = {
    "Arris Modem": {
        "ip": "192.168.100.1",
        "url": "https://192.168.100.1/Login.html",
        "services": {
            "Web Interface": 80
        }
    },
    "OpnSense Router": {
        "ip": "192.168.1.1",
        "url": "https://192.168.1.1/",
        "services": {
            "WAN Status": None
        }
    },
    "Pi-hole DNS": {
        "ip": "192.168.1.2",
        "url": "http://192.168.1.2/admin/",
        "services": {
            "DNS": 53,
            "Web Interface": 80
        }
    },
    "TP-Link AP1": {
        "ip": "192.168.1.3",
        "url": "http://192.168.1.3/"
    },
    "TP-Link AP2": {
        "ip": "192.168.1.4",
        "url": "http://192.168.1.4/"
    },
    "TP-Link Extender": {
        "ip": "192.168.1.5",
        "url": "http://192.168.1.5/"
    },
    "Proxmox": {
        "ip": "192.168.1.21",
        "url": "https://192.168.1.21:8006/",
        "services": {
            "Web Interface": 8006
        }
    },
    "Plex Server": {
        "ip": "192.168.1.22",
        "services": {
            "Plex Web": 32400
        }
    }
}

def is_online(ip):
    try:
        subprocess.check_output(["ping", "-c", "1", ip], stderr=subprocess.STDOUT)
        return True
    except subprocess.CalledProcessError:
        return False

def is_port_open(ip, port, timeout=1):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout)
    try:
        s.connect((ip, port))
        s.shutdown(socket.SHUT_RDWR)
        return True
    except Exception:
        return False
    finally:
        s.close()

@app.route("/")
def dashboard():
    modem = ArrisModem()
    statuses = {}
    update_info = router.updatestatus()

    def get_device_status(device, info):
        ip = info["ip"]
        host_online = is_online(ip)
        device_status = {
            "ip": ip,
            "host": host_online,
            "url": info.get("url")
        }

        if host_online and "services" in info:
            service_statuses = {}
            for svc, port in info["services"].items():
                if svc == "WAN Status":
                    service_statuses[svc] = router_status["status"] == "up"
                    device_status["wan_details"] = router_status
                elif port is not None:
                    service_statuses[svc] = is_port_open(ip, port)
            device_status["services"] = service_statuses
        return device, device_status

    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = [executor.submit(get_device_status, d, info) for d, info in devices.items()]
        for future in as_completed(futures):
            device, result = future.result()
            statuses[device] = result

    # Fetch modem status separately
    if "Arris Modem" in statuses:
        try:
            conn_status = modem.status()
            statuses["Arris Modem"]["conn_state"] = conn_status.get("ConnectivityState", "N/A")
        except Exception as e:
            statuses["Arris Modem"]["conn_state"] = "Error"
            print("Error fetching modem connectivity status:", e)

    statuses["OpnSense Router"]["update_log"] = update_info.get("log", "")
    return render_template("dashboard.html", statuses=statuses, devices=devices)


@app.route("/reboot/arris", methods=["POST"])
def reboot_arris():
    threading.Thread(target=ArrisModem().reboot).start()
    return redirect(url_for('dashboard'))

@app.route("/reboot/opnsense", methods=["POST"])
def reboot_opnsense():
    threading.Thread(target=router.reboot).start()
    return redirect(url_for('dashboard'))

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8080)