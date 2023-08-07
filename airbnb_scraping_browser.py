import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import pandas as pd

username='YOUR_BRIGHTDATA_USERNAME'
password='YOUR_BRIGHTDATA_PASSWORD'
auth=f'{username}:{password}'
host = 'YOUR_BRIGHTDATA_HOST'
browser_url = f'wss://{auth}@{host}'

async def scrape_airbnb():
    async with async_playwright() as pw:
        # Launch new browser
        print('connecting')
        browser = await pw.chromium.connect_over_cdp(browser_url)
        print('connected')
        page = await browser.new_page()
        # Go to Airbnb URL
        await page.goto('https://www.airbnb.com/s/homes', timeout=120000)
        print('done, evaluating')
        # Get the entire HTML content
        html_content = await page.evaluate('()=>document.documentElement.outerHTML')

        # Parse the HTML with Beautiful Soup
        soup = BeautifulSoup(html_content, 'html.parser')

        # Extract information
        results = []
        listings = soup.select('div.g1qv1ctd.c1v0rf5q.dir.dir-ltr')
        for listing in listings:
            result = {}
            # Property name
            name_element = listing.select_one('div[data-testid="listing-card-title"]')
            result['property_name'] = name_element.text if name_element else 'N/A'
            # Location
            location_element = listing.select_one('div[data-testid="listing-card-subtitle"]')
            result['location'] = location_element.text if location_element else 'N/A'
            # Price
            price_element = listing.select_one('div._1jo4hgw')
            result['price'] = price_element.text if price_element else 'N/A'
            results.append(result)

        # Close browser
        await browser.close()
        
        return results

# Run the scraper and save results to a CSV file
results = asyncio.run(scrape_airbnb())
df = pd.DataFrame(results)
df.to_csv('airbnb_listings_scraping_browser.csv', index=False)