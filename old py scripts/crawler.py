import asyncio
import json
import requests
import time
from bs4 import BeautifulSoup
import os
import re
import csv

headersfile = open("./user_agents.txt", "r")
headers = headersfile.read()
headers = eval(headers)
#print(headers)


def sanitize_filename(filename):
    # Remove any characters that are not alphanumeric or spaces
    filename = re.sub(r"[^\w\s-]", "", filename)

    # Replace spaces with underscores
    filename = filename.replace(" ", "_")

    # Remove leading and trailing spaces
    filename = filename.strip()

    return filename


def imgDownload(url, name):
    name = sanitize_filename(name)
    # Send a request to get the image data
    response = requests.get(url)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Get the content of the response (image data)
        image_data = response.content

        # Specify the file path where you want to save the image
        os.makedirs("./downloaded_images/", exist_ok=True)
        file_path = os.path.join("downloaded_images/" + name + ".jpg")

        # Write the image data to a file
        with open(file_path, "wb") as file:
            file.write(image_data)

        print(f"Image downloaded and saved to {file_path}")
    else:
        print(f"Failed to download image. Status code: {response.status_code}")
filename = 'njuskalo_scrapefirst50.csv'

def listingFetchParse(url, headerNumber):
    
    # Get a random User-Agent string
    response = requests.get(url, headers=headers[headerNumber]	)
    headerNumberWorked = headerNumber

    while BeautifulSoup(response.text, "html.parser").findAll("title")[0].text == "ShieldSquare Captcha":
        print("gotCaptcha")
        time.sleep(3)
        print("Resuming...")
        headerNumberWorked = headerNumberWorked + 1
        
        response = requests.get(url, headers=headers[headerNumberWorked])

    if response.status_code == 200:
        html_content = response.text
        listingjson = {
            "price": "",
            "lat": "",
            "lng": "",
            "flatBuildingtype": "",
            "flatFloorCount": "",
            "numberOfRooms": "",
            "buildingFloorPosition": "",
            "livingArea": "",
            "url": "",
            "bathrooms with toilet": "",
            "toilets": ""
        }

        with open("saved_webpage.html", "w", encoding="utf-8") as file:
            file.write(html_content)
        soup = BeautifulSoup(response.text, "html.parser")
        pricet = soup.findAll("dd")
        for index, price in enumerate(pricet):
            if ("class" in price.attrs):
                if ("ClassifiedDetailSummary-priceDomestic" in price["class"]):
                    listingjson["price"] = price.text.rsplit("/")[0].strip().split(",")[0].strip()
        

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
        
        spans = soup.findAll("span")
        i = 0
        for index, span in enumerate(spans):
            if ("data-qa" in span.attrs):
                if ("location" in span["data-qa"]):
                    listingjson["location"] = span.text.rsplit(",")[1].strip()
                elif ( "flatBuildingType" in span["data-qa"]):
                    listingjson["flatBuildingtype"] = span.text
                elif ("flatFloorCount" in span["data-qa"]):
                    listingjson["flatFloorCount"] = span.text
                elif ("numberOfRooms" in span["data-qa"]):
                    listingjson["numberOfRooms"] = span.text
                elif ("buildingFloorPosition" in span["data-qa"]):
                    listingjson["buildingFloorPosition"] = span.text
                elif ("livingArea" in span["data-qa"]):
                    listingjson["livingArea"] = span.text.rsplit(",")[0].strip()
            
    else:
        print(f"Failed to fetch the page. Status code: {response.status_code}")
    return listingjson, headerNumberWorked
    


def main(url):
    # Define the URL you want to crawl
    headerNumber = 250

    # Send an HTTP GET request to the URL
    response = requests.get(url, headers=headers[headerNumber])
    while BeautifulSoup(response.text, "html.parser").findAll("title")[0].text == "ShieldSquare Captcha":
        print("gotCaptcha")
        headerNumber= headerNumber + 1
        response = requests.get(url, headers=headers[headerNumber])

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Parse the HTML content of the page using BeautifulSoup
        soup = BeautifulSoup(response.text, "html.parser")
        EntityListItems = soup.findAll(class_="EntityList--Regular")
        lis = EntityListItems[0].findAll("li")
        i = 0
        with open(filename, 'a', newline='', encoding='utf-8') as csvfile:
            spamwriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            for index, li in enumerate(lis):
                if "data-href" in li.attrs:
                    i += 1
                    if headerNumber < 999:
                        headerNumber += 1
                    else:
                        headerNumber = 0
                    print(i, li["data-href"])
                    time.sleep(1)
                    rowToWrite, headerNumber = listingFetchParse("https://www.njuskalo.hr" + li["data-href"], headerNumber)  
                    rowToWrite["url"] = "https://www.njuskalo.hr" + li["data-href"]	
                    rowToWrite = (rowToWrite["price"], rowToWrite["lat"], rowToWrite["lng"], rowToWrite["location"], rowToWrite["flatBuildingtype"], rowToWrite["flatFloorCount"], rowToWrite["numberOfRooms"], rowToWrite["buildingFloorPosition"], rowToWrite["livingArea"], rowToWrite["url"], rowToWrite["bathrooms with toilet"], rowToWrite["toilets"])
                    if(rowToWrite):
                        spamwriter.writerow(rowToWrite)

    else:
        print(f"Failed to fetch the page. Status code: {response.status_code}")


if __name__ == "__main__":
    with open(filename, 'a', newline='', encoding='utf-8') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        #spamwriter.writerow(["price", "lat", "lng", "location", "flatBuildingtype", "flatFloorCount", "numberOfRooms", "buildingFloorPosition", "livingArea", "url", "bathrooms with toilet", "toilets"])       
    i=2
    main("https://www.njuskalo.hr/prodaja-stanova")
    while i<50:
        print("page: ", i)
        main("https://www.njuskalo.hr/prodaja-stanova?page="+str(i))
        i+=1
    headersfile.close()
