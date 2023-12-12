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


def listingFetchParse(url, headerNumber):
    # Get a random User-Agent string
    response = requests.get(url, headers=headers[headerNumber])
    headerNumberWorked = headerNumber

    while BeautifulSoup(response.text, "html.parser").findAll("title")[0].text == "ShieldSquare Captcha":
        print("gotCaptcha")
        time.sleep(3)
        print("Resuming...")
        headerNumberWorked = headerNumberWorked + 1
        response = requests.get(url, headers=headers[headerNumber])

    if response.status_code == 200:
        # Parse the HTML content of the page using BeautifulSoup
        html_content = response.text
        listingCsvRow = []
        listingjson = {}

        # Save the HTML content to a file
        with open("saved_webpage.html", "w", encoding="utf-8") as file:
            file.write(html_content)
        soup = BeautifulSoup(response.text, "html.parser")
        pricet = soup.findAll("dd")
        for index, price in enumerate(pricet):
            if ("class" in price.attrs):
                if ("ClassifiedDetailSummary-priceDomestic" in price["class"]):
                    print("  ", price.text.rsplit("/")[0].strip())
                    listingCsvRow = listingCsvRow + [price.text.rsplit("/")[0].strip()]
                    listingjson["price"] = price.text.rsplit("/")[0].strip()

        divforscript = soup.findAll("div")
        for index, div in enumerate(divforscript):
            if ("class" in div.attrs):
                if ("content-main" in div["class"]):
                    scripts = div.findAll("script")

        for index, script in enumerate(scripts):
            jsona = script.text.rsplit("app.boot.push(")[1].strip().split(");")[0].strip()
            jsonl = json.loads(jsona)

            if "values" in jsonl.keys() and "mapData" in jsonl["values"].keys() and "defaultMarker" in jsonl["values"]["mapData"].keys():
                defmark = jsonl["values"]["mapData"]["defaultMarker"]
                listingCsvRow = listingCsvRow + [defmark["lat"]]
                listingCsvRow = listingCsvRow + [defmark["lng"]]
                listingjson["lat"] = defmark["lat"]
                listingjson["lng"] = defmark["lng"]
        spans = soup.findAll("span")
        i = 0
        for index, span in enumerate(spans):
            if ("data-qa" in span.attrs):
                if ("location" in span["data-qa"]):
                    print("  ", span.text.rsplit(",")[1].strip())
                    listingCsvRow = listingCsvRow + [span.text.rsplit(",")[1].strip()]
                    listingjson["location"] = span.text.rsplit(",")[1].strip()
                elif ( "flatBuildingType" in span["data-qa"]):
                    print("  ", span.text)
                    listingCsvRow = listingCsvRow + [span.text]
                    listingjson["flatBuildingtype"] = span.text
                elif ("flatFloorCount" in span["data-qa"]):
                    print("  ", span.text)
                    listingCsvRow = listingCsvRow + [span.text]
                    listingjson["flatFloorCount"] = span.text
                elif ("numberOfRooms" in span["data-qa"]):
                    print("  ", span.text)
                    listingCsvRow = listingCsvRow + [span.text]
                    listingjson["numberOfRooms"] = span.text
                elif ("buildingFloorPosition" in span["data-qa"]):
                    print("  ", span.text)
                    listingCsvRow = listingCsvRow + [span.text]
                    listingjson["buildingFloorPosition"] = span.text
                elif ("livingArea" in span["data-qa"]):
                    print("  ", span.text.rsplit(",")[0].strip())
                    listingCsvRow = listingCsvRow + [span.text.rsplit(",")[0].strip()] 
                    listingjson["livingArea"] = span.text.rsplit(",")[0].strip()
            
    else:
        print(f"Failed to fetch the page. Status code: {response.status_code}")
    return listingjson, headerNumberWorked
    


def main():
    # Define the URL you want to crawl
    url = "https://www.njuskalo.hr/prodaja-stanova"
    headerNumber = 470

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
        with open('njuskalo_scrape.csv', 'w', newline='', encoding='utf-8') as csvfile:
            spamwriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            spamwriter.writerow(["price", "lat", "lng", "location", "flatBuildingtype", "flatFloorCount", "numberOfRooms", "buildingFloorPosition", "livingArea", "url"])
            for index, li in enumerate(lis):
                if "data-href" in li.attrs:
                    i += 1
                    if i > 2: 
                        break
                    if headerNumber < 999:
                        headerNumber += 1
                    else:
                        headerNumber = 0
                    print(i, li["data-href"])
                    time.sleep(1)
                    rowToWrite, headerNumber = listingFetchParse("https://www.njuskalo.hr" + li["data-href"], headerNumber)  
                    rowToWrite["url"] = "https://www.njuskalo.hr" + li["data-href"]	
                    rowToWrite = list(rowToWrite.values())
                    if(rowToWrite):
                        spamwriter.writerow(rowToWrite)

    else:
        print(f"Failed to fetch the page. Status code: {response.status_code}")


if __name__ == "__main__":
    main()
    headersfile.close()
