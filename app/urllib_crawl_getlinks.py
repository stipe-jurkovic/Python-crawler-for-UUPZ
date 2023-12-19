import random
import urllib3
import json
import time
from bs4 import BeautifulSoup
import csv
from torpy.http.requests import TorRequests


# Creating a PoolManager instance for sending requests.
default_headers = urllib3.make_headers(proxy_basic_auth='brd-customer-hl_9d5c0427-zone-data_center:mhz69dt2jqyc')
http = urllib3.ProxyManager("https://brd.superproxy.io:22225", proxy_headers=default_headers)
headersfile = open("./user_agents.txt", "r")
headers = headersfile.read()
headers = eval(headers)
filename = 'csvovi/njuskalo_scrape_listing_links.csv'

linenum = 0

def random_delay():
    random_delay = random.uniform(1, 5)
    print(f"Sleeping for {random_delay:.2f} seconds...")
    time.sleep(random_delay)

def fetch(url, headerNumber):
    flag = 0
    default_headers = urllib3.make_headers(proxy_basic_auth='brd-customer-hl_9d5c0427-zone-data_center:mhz69dt2jqyc')
    http = urllib3.ProxyManager("https://brd.superproxy.io:22225", proxy_headers=default_headers)
    response = http.request("GET", url, headers=headers[headerNumber])
    ps = BeautifulSoup(response.data.decode("utf-8"), "html.parser").findAll("p")
    for index, p in enumerate(ps):
        if p.text == "Trenutno nema oglasa koji zadovoljavaju postavljene kriterije pretrage.":
            print("no more listings")
            flag =1
            return response, headerNumber, flag

    while BeautifulSoup(response.data.decode("utf-8"), "html.parser").findAll("title")[0].text == "ShieldSquare Captcha":
        print("gotCaptcha")
        default_headers = urllib3.make_headers(proxy_basic_auth='brd-customer-hl_9d5c0427-zone-data_center:mhz69dt2jqyc')
        http = urllib3.ProxyManager("https://brd.superproxy.io:22225", proxy_headers=default_headers)
        print("Resuming...")
        headerNumber= headerNumber + 1
        response = http.request("GET", url, headers=headers[headerNumber])
    return response, headerNumber, flag

def getListingUrls(url, headerNumber):
    response, headerNumber, flag = fetch(url, headerNumber)
    if flag:
        return flag
    if response.status == 200:
        parseListOfListingsAndTolist(response)
    else:
        print(f"Failed to fetch the page. Status code: {response.status}")
    return flag


def parseListOfListingsAndTolist(response):
    global linenum
    soup = BeautifulSoup(response.data.decode("utf-8"), "html.parser")
    EntityListItems = soup.findAll(class_="EntityList--Regular")
    lis = EntityListItems[0].findAll("li")
    i = 0
    with open(filename, 'a', newline='', encoding='utf-8') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for index, li in enumerate(lis):
            if "data-href" in li.attrs:
                i += 1
                print(linenum, li["data-href"])
                rowToWrite = (linenum,"https://www.njuskalo.hr" + li["data-href"])
                linenum = linenum + 1
                spamwriter.writerow(rowToWrite)



if __name__ == "__main__":
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        spamwriter.writerow(["linenum","url"])
    
    getListingUrls("https://www.njuskalo.hr/prodaja-stanova", 0)
    i=0
    headerNumber = 0
    while True:
        print("page: ", i)
        if headerNumber < 999:
            headerNumber += 1
        else:
            headerNumber = 0
        if (getListingUrls("https://www.njuskalo.hr/prodaja-stanova?page="+str(i), headerNumber)):
            print("reached the end")
            break
    
        i+=1
    headersfile.close()
