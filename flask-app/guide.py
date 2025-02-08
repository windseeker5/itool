import os
import requests
import gzip
import xml.etree.ElementTree as ET
from flask import Flask, send_from_directory
import schedule
import time
from threading import Thread

# Store credentials securely (use environment variables or a config file)
USERNAME = os.getenv("XMLTV_USERNAME", "c8bb0d2998")  # Change accordingly
PASSWORD = os.getenv("XMLTV_PASSWORD", "297afed6ea")  # Change accordingly
XMLTV_URL = f"http://cf.1575-cdn.me/xmltv.php?username={USERNAME}&password={PASSWORD}"

ToKeep = ["TVASports.ca",
    "TVA.ca",
    "TVASports2.ca",
    "RDS.ca",
    "RDS2.ca",
    "RDSInfo.ca",
    "SuperEcran2.ca",
    "SuperEcran4.ca",
    "SuperEcran.ca",
    "SuperEcran3.ca",
    "Crave1.ca",
    "Crave2.ca",
    "Crave3.ca",
    "Crave4.ca",
    "CanalVie.ca",
    "Noovo.ca",
    "CanalEvasion.ca",
    "RDINews.ca",
    "ICIRadioCanadaMontreal.ca"]

# Download and save the XMLTV guide
def download_xmltv(url, output_file="guide.xml.gz"):
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        content_type = response.headers.get('Content-Type')
        if 'application/gzip' in content_type:
            with open(output_file, "wb") as f:
                f.write(response.content)
            print("Download complete.")
            return output_file
        else:
            with open("guide.xml", "wb") as f:
                f.write(response.content)
            print("Downloaded file is not gzipped. Saved as guide.xml.")
            return "guide.xml"
    else:
        print(f"Failed to download XMLTV (HTTP {response.status_code})")
        return None

# Extract GZipped XML
def extract_gz(input_file="guide.xml.gz", output_file="guide.xml"):
    try:
        with gzip.open(input_file, "rb") as f_in:
            with open(output_file, "wb") as f_out:
                f_out.write(f_in.read())
        print("Extraction complete.")
        return output_file
    except gzip.BadGzipFile:
        print(f"{input_file} is not a valid gzipped file.")
        return None

# Filter XML and save to new file
def filter_xml(xml_file="guide.xml", output_file="smallGuide.xml"):
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()

        # Filter channels
        for channel in root.findall('channel'):
            channel_id = channel.get('id')
            if channel_id not in ToKeep:
                root.remove(channel)

        # Filter programmes
        for programme in root.findall('programme'):
            channel_id = programme.get('channel')
            if channel_id not in ToKeep:
                root.remove(programme)

        # Save filtered XML
        tree.write(output_file)
        print(f"Filtered XML saved to {output_file}")
        return output_file

    except ET.ParseError:
        print(f"Failed to parse {xml_file}. The file may be corrupted or not a valid XML.")
        return None

# Start micro web server
def start_server(directory, filename):
    app = Flask(__name__)

    @app.route('/xmltv')
    def serve_file():
        return send_from_directory(directory, filename)

    def run_server():
        app.run(host='0.0.0.0', port=8000)

    server_thread = Thread(target=run_server)
    server_thread.start()

# Run the process
def run_process():
    downloaded_file = download_xmltv(XMLTV_URL)
    if downloaded_file == "guide.xml.gz":
        extracted_file = extract_gz(downloaded_file)
        if extracted_file:
            filtered_file = filter_xml(extracted_file)
            if filtered_file:
                start_server(os.path.dirname(filtered_file), os.path.basename(filtered_file))
    elif downloaded_file == "guide.xml":
        filtered_file = filter_xml(downloaded_file)
        if filtered_file:
            start_server(os.path.dirname(filtered_file), os.path.basename(filtered_file))

# Schedule the process to run every 6 hours
schedule.every(6).hours.do(run_process)

# Start the initial process
run_process()

# Keep the script running to maintain the schedule
while True:
    schedule.run_pending()
    time.sleep(1)