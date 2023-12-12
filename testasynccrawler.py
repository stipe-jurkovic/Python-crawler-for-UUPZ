import aiohttp
import asyncio

headersfile = open("./user_agents.txt", "r")
headers = headersfile.read()
headers = eval(headers)
#print(headers)

async def fetch(url, session, headerNumber):
    async with session.get(url, headers=headers[headerNumber]) as response:
        return await response.text()
    

async def scrape_websites(urls):
    async with aiohttp.ClientSession() as session:
        tasks = [fetch(url, session, headerNumber=55) for url in urls]
        results = await asyncio.gather(*tasks)
        return results

if __name__ == "__main__":
    # List of URLs to scrape
    websites = ["https://www.njuskalo.hr/prodaja-stanova","https://www.njuskalo.hr/prodaja-stanova?page=2"]

    # Run the event loop
    loop = asyncio.get_event_loop()
    scraped_data = loop.run_until_complete(scrape_websites(websites))

    # Process the scraped data
    for url, data in zip(websites, scraped_data):
        print(f"Data from {url}: {data[:1000]}...")  # Print only the first 100 characters for each URL