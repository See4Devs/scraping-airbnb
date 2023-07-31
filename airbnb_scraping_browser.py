import asyncio
from playwright.async_api import async_playwright
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
        # Extract information
        results = []
        listings = await page.query_selector_all('div.g1qv1ctd.c1v0rf5q.dir.dir-ltr')
        for listing in listings:
            result = {}
            # Property name
            name_element = await listing.query_selector('div[data-testid="listing-card-title"]')
            if name_element:
                result['property_name'] = await page.evaluate("(el) => el.textContent", name_element)
            else:
                result['property_name'] = 'N/A'
            # Location
            location_element = await listing.query_selector('div[data-testid="listing-card-subtitle"]')
            result['location'] = await location_element.inner_text() if location_element else 'N/A'
            # Price
            price_element = await listing.query_selector('div._1jo4hgw')
            result['price'] = await price_element.inner_text() if price_element else 'N/A'
            results.append(result)
        
        # Close browser
        await browser.close()
        
        return results
# Run the scraper and save results to a CSV file
results = asyncio.run(scrape_airbnb())
df = pd.DataFrame(results)
df.to_csv('airbnb_listings_scraping_browser.csv', index=False)
