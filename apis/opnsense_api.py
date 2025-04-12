import requests
import os
import time
from dotenv import load_dotenv
from requests.auth import HTTPBasicAuth


load_dotenv()

# Replace with your actual OPNsense instance IP or hostname
HOST = "https://192.168.1.1"
# Interface to query
INTERFACE = "wan"

class OPNsense():
    """
    Class to interact with OPNsense API.
    
    Attributes:
        host (str): The OPNsense router IP or hostname.
        api_key (str): The API key for authentication.
        api_secret (str): The API secret for authentication.
    """
    def __init__(self, host="192.168.1.1", api_key=os.getenv("OPNSENSE_KEY"), api_secret=os.getenv("OPNSENSE_SECRET")):

        self.host = f"https://{host}"
        self.api_key = api_key
        self.api_secret = api_secret

    def interface_status(self, interface) -> dict:
        """
        Retrieves the status of a specific interface on the OPNsense router.

        Returns a dictionary with interface status information.
        """
        # Endpoint
        url = f"{HOST}/api/interfaces/overview/interfacesInfo"

        try:
            # Send GET request
            response = requests.get(url, auth=HTTPBasicAuth(self.api_key, self.api_secret), verify=False)

            if response.ok:
                data = response.json()
                for row in data['rows']:
                    if row['identifier'] == interface:
                        return {
                            "status": row['status'],
                            "ip_address": row['addr4'],
                            "gateways": row['gateways']
                        }
            else:
                print("Failed to retrieve interface status.")
                print("Status Code:", response.status_code)
                print("Response:", response.text)
                return None

        except requests.RequestException as e:
            print("Error during API request:", e)
            return None
        except ValueError as e:
            print("Error parsing JSON response:", e)
            return None
        except KeyError as e:
            print("Error accessing JSON data:", e)
            return None
        except Exception as e:
            print("Unexpected error:", e)
            return None
    
    def reboot(self):
        """
        Reboots the OPNsense router.

        Returns True if the reboot command was sent successfully, False otherwise.
        """
        url = f"{self.host}/api/core/firmware/reboot"

        try:
            # Send POST request
            headers = {"Content-Type": "application/json"}
            response = requests.post(url, auth=HTTPBasicAuth(self.api_key, self.api_secret), headers=headers, json={}, verify=False)

            if response.ok:
                print("Reboot command sent successfully.")
                return True
            else:
                print("Failed to send reboot command.")
                print("Status Code:", response.status_code)
                print("Response:", response.text)
                return False

        except requests.RequestException as e:
            print("Error during API request:", e)
            return False
        except Exception as e:
            print("Unexpected error:", e)
            return False

    def fw_status(self):
        """
        Retrieves the status of the OPNsense firmware.

        Returns a dictionary with firmware status information.
        """
        url = f"{HOST}/api/core/firmware/status"

        try:
            # Send GET request
            response = requests.get(url, auth=HTTPBasicAuth(self.api_key, self.api_secret), verify=False)

            if response.ok:
                data = response.json()
                return data
            else:
                print("Failed to retrieve firmware status.")
                print("Status Code:", response.status_code)
                print("Response:", response.text)
                return None

        except requests.RequestException as e:
            print("Error during API request:", e)
            return None
        except ValueError as e:
            print("Error parsing JSON response:", e)
            return None
        except KeyError as e:
            print("Error accessing JSON data:", e)
            return None
        except Exception as e:
            print("Unexpected error:", e)
            return None

    def updatestatus(self, poll_interval=3, timeout=120):
        """
        Polls the OPNsense firmware update status until fully complete or timeout.

        Returns:
            dict: Final response from the firmware status endpoint.
        """
        url = f"{self.host}/api/core/firmware/upgradestatus"
        start_time = time.time()

        try:
            while True:
                response = requests.get(url, auth=HTTPBasicAuth(self.api_key, self.api_secret), verify=False)

                if response.ok:
                    data = response.json()
                    status = data.get("status", "").lower()
                    log = data.get("log", "")

                    # Debug logging
                    print(f"[{time.strftime('%H:%M:%S')}] Status: {status}")
                    print("Partial log tail:", log.strip().splitlines()[-1] if log else "<no log>")

                    # Consider complete only when status is 'done' AND log contains '***DONE***'
                    if status == "done" and "***DONE***" in log:
                        return data
                    elif time.time() - start_time > timeout:
                        print("Timeout waiting for full update check to complete.")
                        return {"status": "timeout", "log": log}
                    else:
                        time.sleep(poll_interval)
                else:
                    print("Failed to retrieve update status.")
                    print("Status Code:", response.status_code)
                    print("Response:", response.text)
                    return None

        except requests.RequestException as e:
            print("Error during API request:", e)
            return None
        except Exception as e:
            print("Unexpected error:", e)
            return None

if __name__ == "__main__":
    # Create an instance of the OPNsense class
    opnsense = OPNsense()
    
    # Get the status of the specified interface
    print(opnsense.updatestatus())