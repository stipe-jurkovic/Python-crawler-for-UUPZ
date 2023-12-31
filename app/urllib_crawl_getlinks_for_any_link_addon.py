import os
import random
import urllib3
import json
import time
from bs4 import BeautifulSoup
import csv
from datetime import datetime




host = "https://brd.superproxy.io:22225"
proxyuser = "brd-customer-hl_9d5c0427-zone-data_center"
proxypass = "mhz69dt2jqyc"

# Creating a PoolManager instance for sending requests.
default_headers = urllib3.make_headers(proxy_basic_auth=proxyuser+":"+proxypass)
http = urllib3.ProxyManager(host, proxy_headers=default_headers)
headersfile = open("./user_agents.txt", "r")
headers = headersfile.read()
headers = eval(headers)

linenum = 1

def random_delay():
    random_delay = random.uniform(1, 5)
    print(f"Sleeping for {random_delay:.2f} seconds...")
    time.sleep(random_delay)

def fetch(url, headerNumber):
    flag = 0
    default_headers = urllib3.make_headers(proxy_basic_auth=proxyuser+":"+proxypass)
    http = urllib3.ProxyManager(host, proxy_headers=default_headers)
    response = http.request("GET", url, headers=headers[headerNumber])

    while BeautifulSoup(response.data.decode("utf-8"), "html.parser").findAll("title")[0].text == "ShieldSquare Captcha":
        print("gotCaptcha")
        default_headers = urllib3.make_headers(proxy_basic_auth=proxyuser+":"+proxypass)
        http = urllib3.ProxyManager(host, proxy_headers=default_headers)    
        print("Resuming...")
        headerNumber= headerNumber + 1
        response = http.request("GET", url, headers=headers[headerNumber])

    ps = BeautifulSoup(response.data.decode("utf-8"), "html.parser").findAll("p")
    for index, p in enumerate(ps):
        if p.text == "Trenutno nema oglasa koji zadovoljavaju postavljene kriterije pretrage.":
            print("no more listings")
            flag =1
            return response, headerNumber, flag
    divs = BeautifulSoup(response.data.decode("utf-8"), "html.parser").findAll("div")
    for index, div in enumerate(divs):
        if div.text == "Trenutno nema oglasa koji zadovoljavaju postavljene kriterije pretrage.":
            print("no more listings")
            flag =1
            return response, headerNumber, flag
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

def getpartoflink():
    exit_loop = False
    while not exit_loop:
        print("Enter suffix (example /dubrovacko-neretvanska): ")
        inputzupanija = input()
        urlinitial = "https://www.njuskalo.hr/prodaja-stanova"+ inputzupanija
        response, headerNumber, flag = fetch(urlinitial, 0)
        soup = BeautifulSoup(response.data.decode("utf-8"), "html.parser")
        lis = soup.findAll("li")
        exit_loop = True
        for index, li in enumerate(lis):
            if li.text == "Provjeri da adresa nije krivo napisana, jer možda ti se omakla pogreška u tipkanju.":
                print("Provjeri da adresa nije krivo napisana, jer možda ti se omakla pogreška u tipkanju.")
                exit_loop = False
    return inputzupanija

if __name__ == "__main__":
    # datetime object containing current date and time
    now = datetime.now()


    # dd/mm/YYH:M:S
    dt_string = now.strftime("_%d-%m-%Y_%H-%M-%S")
    print("date and time =", dt_string)
    zupanija = getpartoflink()
    
    urlinitial = "https://www.njuskalo.hr/prodaja-stanova"+ zupanija
    
    global filename
    try:
        path = "./csvovi"+zupanija
        os.mkdir(path)
        print("Folder %s created!" % path)
    except FileExistsError:
        print("Folder %s already exists" % path)
    filename = 'csvovi'+zupanija+'/njuskalo_scrape_listing_links_'+zupanija.split("/")[1].strip()+dt_string+'.csv'

    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        spamwriter.writerow(["linenum","url"])
    i=1
    headerNumber = 0
    while True:
        if headerNumber < 999:
            headerNumber += 1
        else:
            headerNumber = 0
        print("\n"+urlinitial+"?page="+str(i)+"\n")
        if (getListingUrls(urlinitial+"?page="+str(i), headerNumber)):
            print("reached the end")
            break
    
        i+=1
    headersfile.close()
