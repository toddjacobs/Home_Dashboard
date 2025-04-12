# Home Dashboard

Welcome to the **Home Dashboard** project! This repository contains the code and resources for creating a customizable and user-friendly dashboard for managing and monitoring home-related activities. This project is intended to be tailored to the author's home network.

## Features

- **Customizable Widgets**: Add and configure widgets to display the information you need.
- **Real-Time Updates**: Stay up-to-date with live data feeds.
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile devices.
- **Integration Support**: Connect with smart home devices, APIs, and more.

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/your-username/Home_Dashboard.git
    ```
2. Navigate to the project directory:
    ```bash
    cd Home_Dashboard
    ```
3. Install dependencies:
    ```bash
    # For macOS
    brew install python3

    # For Debian/Ubuntu-based Linux
    sudo apt update && sudo apt install python3

    # For Red Hat/CentOS-based Linux
    sudo yum install python3

    # For Fedora
    sudo dnf install python3
    ```
    ```bash
    pip3 install -r requirements.txt
    ```
4. Create secrets:
    ```bash
    nano .env
    ```
    Populate the `.env` file with the following variables:
    ```
    ARRIS_PW=<your_arris_password>
    OPNSENSE_KEY=<your_opnsense_key>
    OPNSENSE_SECRET=<your_opnsense_secret>
    ```
    Replace `<your_arris_password>`, `<your_opnsense_key>`, and `<your_opnsense_secret>` with your actual credentials.
5. Run dashboard.py:
    ```bash
    python3 main.py
    ```
    This exposes 0.0.0.0:8080

## Usage

- Access the dashboard in your browser at `http://localhost:8080`.
- Customize widgets and settings through the configuration panel.

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository.
2. Create a new branch:
    ```bash
    git checkout -b feature-name
    ```
3. Commit your changes:
    ```bash
    git commit -m "Add feature-name"
    ```
4. Push to your branch:
    ```bash
    git push origin feature-name
    ```
5. Open a pull request.

## License

This project is licensed under the [MIT License](LICENSE).

## Future Features

- **Modify content via UI** Project will allow users to modify their specific network settings from the web UI.
- **Greater Pi-Hole Monitoring and actions** Project will take advantage of the PiHole API to offer users greater control and monitoring over their PiHole instance.
- **Greater Plex Monitoring and actions** Project will take advantage of the Plex API to offer users greater control and monitoring over their PiHole instance.
- **Expanded IoT support** support is intended for the following:
- TP-Link APs
- Ring
- Eufy Lock
- Ecobee
- TP-Link Cameras
- Philips Hue
