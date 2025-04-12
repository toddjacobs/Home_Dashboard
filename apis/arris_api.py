# arris_api.py
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv
import traceback
import os

load_dotenv()

class ArrisModem:
    """
    A class to interact with the Arris modem using Selenium WebDriver.
    This class provides methods to log in, retrieve connection status,
    and reboot the modem.
    """

    def __init__(self, url="192.168.100.1", username="admin", password=os.getenv("ARRIS_PW")):
        self.username = username
        self.password = password
        self.url = url
        self.chrome_options = Options()
        self.chrome_options.add_argument("--headless")
        self.chrome_options.add_argument("--disable-gpu")
        self.chrome_options.add_argument("--no-sandbox")
        self.chrome_options.add_argument("--ignore-certificate-errors")
        self.driver = webdriver.Chrome(options=self.chrome_options)
        self.wait = WebDriverWait(self.driver, 20)

    
    def login(self):
        """
        Performs the login process on the Arris router.
        Loads the Login page, enters credentials, and clicks the login button.
        Assumes the login page URL is https://192.168.100.1/Login.html.
        """
        login_url = f"https://{self.url}/Login.html"
        self.driver.get(login_url)
        
        # Wait for the login fields to be present
        username_field = self.wait.until(EC.presence_of_element_located((By.ID, "loginUsername")))
        password_field = self.wait.until(EC.presence_of_element_located((By.ID, "loginWAP")))
        
        username_field.clear()
        username_field.send_keys(self.username)
        password_field.clear()
        password_field.send_keys(self.password)
        
        # Click the login button.
        login_button = self.driver.find_element(By.ID, "login")
        login_button.click()
        
        # Wait until the Device Status button is clickable to assume login was successful.
        self.wait.until(EC.element_to_be_clickable((By.ID, "DeviceStatus")))
    
    
    def status(self):
        """
        Logs into the Arris router and retrieves connectivity status from the
        connection status page (https://192.168.100.1/Cmconnectionstatus.html).
        
        Returns a dictionary with connection status information. For example:
          {
             "ConnectivityState": "Connected",
             "BootStatus": "...",
             "ConfigurationFileStatus": "...",
             "SecurityStatus": "...",
             "NetworkAccess": "...",
             "SystemUpTime": "..."
          }
        
        Adjust the keys and element IDs as needed.
        """
        
        connectivity_status = {}
        
        try:
            # Log in to the router.
            self.login()
            
            # After login, navigate to the connection status page.
            conn_status_url = f"https://{self.url}/Cmconnectionstatus.html"
            self.driver.get(conn_status_url)
            
            # Wait until one or more key elements are loaded. In this example we wait for the Connectivity State.
            connectivity_elem = self.wait.until(EC.visibility_of_element_located((By.ID, "CustomerConnConnectivityStatus")))
            connectivity_value = connectivity_elem.text.strip()
            connectivity_status["ConnectivityState"] = connectivity_value
            
            # (Optional) Extract additional fields from the table.
            try:
                boot_status = self.driver.find_element(By.ID, "CustomerConnBootStatus").text.strip()
                connectivity_status["BootStatus"] = boot_status
            except Exception:
                connectivity_status["BootStatus"] = "N/A"
            
            try:
                config_file_status = self.driver.find_element(By.ID, "CustomerConnConfigurationFileStatus").text.strip()
                connectivity_status["ConfigurationFileStatus"] = config_file_status
            except Exception:
                connectivity_status["ConfigurationFileStatus"] = "N/A"
            
            try:
                security_status = self.driver.find_element(By.ID, "CustomerConnSecurityStatus").text.strip()
                connectivity_status["SecurityStatus"] = security_status
            except Exception:
                connectivity_status["SecurityStatus"] = "N/A"
            
            try:
                network_access = self.driver.find_element(By.ID, "CustomerConnNetworkAccess").text.strip()
                connectivity_status["NetworkAccess"] = network_access
            except Exception:
                connectivity_status["NetworkAccess"] = "N/A"
            
            try:
                system_time = self.driver.find_element(By.ID, "CustomerConnSystemUpTime").text.strip()
                connectivity_status["SystemUpTime"] = system_time
            except Exception:
                connectivity_status["SystemUpTime"] = "N/A"
                
        except Exception as e:
            print("Error retrieving connectivity status:", e)
            print("Page title:", self.driver.title)
            print("Current URL:", self.driver.current_url)
            print("Page source snippet:", self.driver.page_source[:1000])
            traceback.print_exc()
        
        finally:
            self.driver.quit()
        
        return connectivity_status
    
    
    def reboot(self):
        """
        Logs into the Arris router and reboots it.
        Navigates to the configuration page and clicks the Reboot button,
        handling the confirmation alert.
        """
        
        try:
            self.login()
            
            # Navigate to the configuration page.
            config_url = f"https://{self.url}/Cmconfiguration.html"
            self.driver.get(config_url)
            
            # Wait for the Reboot button to appear.
            reboot_button = self.wait.until(EC.presence_of_element_located((By.ID, "Reboot")))
            reboot_button.click()
            
            # Wait for the confirmation alert and accept it.
            try:
                alert = self.wait.until(EC.alert_is_present())
                alert.accept()
            except Exception as alert_ex:
                return {"error" : f"No alert present or error handling alert: {alert_ex}"}
            
            self.wait.until(EC.presence_of_element_located((By.ID, "RebootMsg")))
        
        except Exception as e:
            print("Error rebooting Arris router:", e)
            print("Page title:", self.driver.title)
            print("Current URL:", self.driver.current_url)
            print("Page source snippet:", self.driver.page_source[:1000])
            traceback.print_exc()
        
        finally:
            self.driver.quit()
    

if __name__ == '__main__':
    # For testing, call get_connectivity_status() to see the output.
    arris = ArrisModem()
    print("Fetching connectivity status...")
    status = arris.status()
    print(status.get("ConnectivityState", "N/A"))
    
    # To test rebooting the router, uncomment the following line:
    # reboot_arris_router()