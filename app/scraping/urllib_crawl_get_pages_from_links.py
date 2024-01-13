from datetime import datetime
import random
import traceback
import urllib3
import json
import time
from bs4 import BeautifulSoup
import csv
import os

global host
global proxyuser
global proxypass

host = "https://brd.superproxy.io:22225"
proxyuser = "brd-customer-hl_1c53920b-zone-datacenter_proxy1"
proxypass = "u9piqpc08az5"

current_directory = os.getcwd()
folder_name = os.path.basename(current_directory)
print("Current folder name:", folder_name) 
if folder_name == "app":
    os.chdir("..")

current_directory = os.getcwd()
folder_name = os.path.basename(current_directory)
print("Current folder name:", folder_name) 

# Creating a PoolManager instance for sending requests.
default_headers = urllib3.make_headers(proxy_basic_auth=proxyuser+":"+proxypass)
http = urllib3.ProxyManager(host, proxy_headers=default_headers)
headersfile = open("./utils/user_agents.txt", "r")
headers = headersfile.read()
headers = eval(headers)
global filenameread
global filenamewrite
global startLine
    
def random_delay():
    random_delay = random.uniform(1, 5)
    print(f"Sleeping for {random_delay:.2f} seconds...")
    time.sleep(random_delay) 

def fetch(url, headerNumber):
    default_headers = urllib3.make_headers(proxy_basic_auth=proxyuser+":"+proxypass)
    http = urllib3.ProxyManager(host, proxy_headers=default_headers)
    response = http.request("GET", url, headers=headers[headerNumber])

    while BeautifulSoup(response.data.decode("utf-8"), "html.parser").findAll("title")[0].text == "ShieldSquare Captcha":
        print("gotCaptcha")
        default_headers = urllib3.make_headers(proxy_basic_auth=proxyuser+":"+proxypass)
        http = urllib3.ProxyManager(host, proxy_headers=default_headers)
        print("Resuming...")
        if headerNumber < 999:
            headerNumber += 1
        else:
            headerNumber = 0
        response = http.request("GET", url, headers=headers[headerNumber])
    return response, headerNumber

def listingFetchParse(url, headerNumber):
    # Get a random User-Agent string
    headerNumber = headerNumber
    response, headerNumber = fetch(url, headerNumber)

    if response.status == 200:
       listingjson = parseListing(response)
    else:
        print(f"Failed to fetch the page. Status code: {response.status}")
    return listingjson, headerNumber

def getListingInfo(headerNumber, directory):
    last_processed_line = get_last_processed_line(directory)
    with open(file_path, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='|')
        line_count = 0
        for row in reader:
            if line_count == 0:
                line_count += 1
            else:
                if line_count > last_processed_line and row[1].__contains__("https://www.njuskalo.hr/nekretnine/"):
                    try:
                        headerNumber = parseListingsAndToCsv(headerNumber,row[0], row[1])
                    except(Exception):
                        print("error line: ",row[0])
                        traceback.print_exc()
                    print("processed linenum: ",row[0])
                line_count += 1
            update_last_processed_line(directory, line_count - 1)
        print(f'Processed {line_count} lines.')

def get_last_processed_line(directory):
    file_name = f"./data/csvovi/{directory}/last_processed_line_{directory}.txt"
    if os.path.exists(file_name):
        with open(file_name, 'r') as file:
            last_line = file.read()
            return int(last_line) if last_line else 0
    return 0

def update_last_processed_line(directory, line_number):
    file_name = f"./data/csvovi/{directory}/last_processed_line_{directory}.txt"
    with open(file_name, 'w') as file:
        file.write(str(line_number))

def parseListing(response):
    html_content = response.data.decode("utf-8")
    listingjson = {
        "price": "",
        "lat": "",
        "lng": "",
        "county": "",
        "city": "",
        "neighborhood": "",
        "flatBuildingtype": "",
        "flatFloorCount": "",
        "numberOfRooms": "",
        "buildingFloorPosition": "",
        "livingArea": "",
        "url": "",
        "bathrooms with toilet": "",
        "toilets": ""
    }

    soup = BeautifulSoup(response.data.decode("utf-8"), "html.parser")
    pricet = soup.findAll("dd")
    for index, price in enumerate(pricet):
        if ("class" in price.attrs):
            if ("ClassifiedDetailSummary-priceDomestic" in price["class"]):
                listingjson["price"] = price.text.rsplit("\xa0€ /")[0].strip().split(",")[0].strip()
                '\n                                                145.000\xa0€ / 1.092.502,50\xa0kn\n                \n                                    '
                break
    

    divz = soup.findAll("div")
    for index, div in enumerate(divz):
        if ("class" in div.attrs):
            if ("content-main" in div["class"]):
                scripts = div.findAll("script")
            if ("ClassifiedDetailPropertyGroups--standard" in div["class"]):
                grijanje = div.findAll("section")
                for index, grija in enumerate(grijanje):
                    divuli = grija.findAll("div")[0].findAll("ul")[0]
                    if grija.findAll("h3")[0].text == "Kupaonica i WC":
                        listingjson["bathrooms with toilet"] = divuli.findAll("li")[0].text.rsplit(":")[1].strip()
                        if len(divuli.findAll("li"))>1:
                            listingjson["toilets"] = divuli.findAll("li")[1].text.rsplit(":")[1].strip()
    for index, script in enumerate(scripts):
        jsona = script.text.rsplit("app.boot.push(")[1].strip().split(");")[0].strip()
        jsonl = json.loads(jsona)
        if (("values" in jsonl.keys()) and isinstance(jsonl["values"], dict) and 
            ("mapData" in jsonl["values"].keys()) and isinstance(jsonl["values"]["mapData"], dict)
                and ("defaultMarker" in jsonl["values"]["mapData"].keys())):
            
            defmark = jsonl["values"]["mapData"]["defaultMarker"]

            listingjson["lat"] = defmark["lat"]
            listingjson["lng"] = defmark["lng"]
    

    dt_elements = soup.find_all('dt', class_='ClassifiedDetailBasicDetails-listTerm')
    dd_elements = soup.find_all('dd', class_='ClassifiedDetailBasicDetails-listDefinition')

    for index, dt in enumerate(dt_elements):
        if dt.text.__contains__("Lokacija"):
            listingjson["county"] = dd_elements[index].text.rsplit(",")[0].strip()
            listingjson["city"] = dd_elements[index].text.rsplit(",")[1].strip()
            listingjson["neighborhood"] = dd_elements[index].text.rsplit(",")[2].strip()
        elif dt.text.__contains__("Tip stana"):
            listingjson["flatBuildingtype"] = dd_elements[index].text.strip()
        elif dt.text.__contains__("Broj etaža"):
            listingjson["flatFloorCount"] = dd_elements[index].text.strip()
        elif dt.text.__contains__("Broj soba"):
            listingjson["numberOfRooms"] = dd_elements[index].text.strip()
        elif dt.text.__contains__("Kat"):
            listingjson["buildingFloorPosition"] = dd_elements[index].text.strip()
        elif dt.text.__contains__("Stambena površina"):
            listingjson["livingArea"] = dd_elements[index].text.rsplit(",")[0].strip()

    return listingjson

def parseListingsAndToCsv(headerNumber, linenum, url):
    with open(filenamewrite, 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        if headerNumber < 999:
            headerNumber += 1
        else:
            headerNumber = 0
        print(url)
        rowToWrite, headerNumber = listingFetchParse(url, headerNumber)  
        rowToWrite["url"] = url
        rowToWrite = (linenum, rowToWrite["price"], rowToWrite["livingArea"], rowToWrite["lat"], rowToWrite["lng"], rowToWrite["county"], rowToWrite["city"], rowToWrite["neighborhood"], rowToWrite["flatBuildingtype"], rowToWrite["flatFloorCount"], rowToWrite["numberOfRooms"], rowToWrite["bathrooms with toilet"], rowToWrite["toilets"], rowToWrite["buildingFloorPosition"], rowToWrite["url"])
        if(rowToWrite):
            writer.writerow(rowToWrite)
    return headerNumber

def list_directories(directory_path):
    directories = [d for d in os.listdir(directory_path) if os.path.isdir(os.path.join(directory_path, d))]
    return directories

def select_directory(directories):
    print("Select a directory:")
    for index, directory in enumerate(directories, start=1):
        print(f"{index}. {directory}")

    # Prompt the user to select a directory
    selection = int(input("Enter the number of the directory you want to use: ")) - 1

    if 0 <= selection < len(directories):
        return directories[selection]
    else:
        print("Invalid selection.")
        return None

if __name__ == "__main__":
    now = datetime.now()

    directory_path = './data/csvovi/'
    

    directories_list = list_directories(directory_path)
    if directories_list:
        selected_directory = select_directory(directories_list)
    if selected_directory:
        print(f"Selected directory: {selected_directory}")
        # filename = f"listing_links_{selected_directory}.csv"
    else:
        print("No directories found.")

    filename = f"listing_links_{selected_directory}.csv"
    file_path = f"{directory_path}/{selected_directory}/{filename}"

    last_processed_filename = f"{directory_path}/{selected_directory}/last_processed_line_{selected_directory}.txt"

    # dd/mm/YYH:M:S
    dt_string = now.strftime("%d-%m-%Y_%H-%M-%S")
    print("date and time =", dt_string)
    filenamewrite = file_path.split(".csv")[0] + "_scraped"+ dt_string + ".csv"

    with open(filenamewrite, 'a', newline='', encoding='utf-8') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        if os.path.exists(filenamewrite) and os.stat(filenamewrite).st_size == 0:
            spamwriter.writerow(["linenum","price", "livingArea", "lat", "lng", "county", "city", "neighborhood", "flatBuildingtype", "flatFloorCount", "numberOfRooms", "bathrooms with toilet", "toilets", "buildingFloorPosition", "url"])       
    
    getListingInfo(0, selected_directory)
    headersfile.close()
