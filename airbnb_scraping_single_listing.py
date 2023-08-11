import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import pandas as pd

username='YOUR_BRIGHTDATA_USERNAME'
password='YOUR_BRIGHTDATA_PASSWORD'
auth=f'{username}:{password}'
host = 'YOUR_BRIGHTDATA_HOST'
browser_url = f'wss://{auth}@{host}'

async def scrape_airbnb_listing():
    async with async_playwright() as pw:
        # Launch new browser
        print('connecting')
        browser = await pw.chromium.connect_over_cdp(browser_url)
        print('connected')
        page = await browser.new_page()
        # Go to Airbnb URL
        await page.goto('https://www.airbnb.com/rooms/26300485', timeout=120000)
        print('done, evaluating')
        # Wait for content to load
        await page.wait_for_selector('div.tq51prx.dir.dir-ltr h2')
        # Get the entire HTML content
        html_content = await page.evaluate('()=>document.documentElement.outerHTML')
        # Parse the HTML with Beautiful Soup
        soup = BeautifulSoup(html_content, 'html.parser')

        # Extract host name
        host_div = soup.select_one('div.tq51prx.dir.dir-ltr h2')
        host_name = host_div.text.split("hosted by ")[-1] if host_div else 'N/A'
        print(f'Host name: {host_name}')

        # Extract reviews
        reviews_span = soup.select_one('span._s65ijh7 button')
        reviews = reviews_span.text.split(" ")[0] if reviews_span else 'N/A'
        print(f'Reviews: {reviews}')

        # Close browser
        await browser.close()

        return {
            'host_name': host_name,
            'reviews': reviews,
        }

# Run the scraper and save results to a CSV file
results = asyncio.run(scrape_airbnb_listing())
df = pd.DataFrame([results]) # results is now a dictionary
df.to_csv('scrape_airbnb_listing.csv', index=False)



