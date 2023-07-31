from playwright.sync_api import sync_playwright
import pandas as pd

def run(playwright):
    browser = playwright.chromium.launch()
    context = browser.new_context()

    # Set up proxy
    proxy_username='YOUR_BRIGHTDATA_PROXY_USERNAME'
    proxy_password='YOUR_BRIGHTDATA_PROXY_PASSWORD'
    proxy_host = 'YOUR_BRIGHTDATA_PROXY_HOST'
    proxy_auth=f'{proxy_username}:{proxy_password}'
    proxy_server = f'http://{proxy_auth}@{proxy_host}'

    context = browser.new_context(proxy={
        'server': proxy_server,
        'username': proxy_username,
        'password': proxy_password
    })

    page = context.new_page()
    page.goto('https://www.airbnb.com/s/homes')

    # Wait for the page to load
    page.wait_for_load_state("networkidle")

    # Extract the data
    results = page.eval_on_selector_all('div.g1qv1ctd.c1v0rf5q.dir.dir-ltr', '''(listings) => {
        return listings.map(listing => {
            return {
                property_name: listing.querySelector('div[data-testid="listing-card-title"]')?.innerText || 'N/A',
                location: listing.querySelector('div[data-testid="listing-card-subtitle"]')?.innerText || 'N/A',
                price: listing.querySelector('div._1jo4hgw')?.innerText || 'N/A'
            }
        })
    }''')

    df = pd.DataFrame(results)
    df.to_csv('airbnb_listings_scraping_proxy.csv', index=False)

    # Close the browser
    browser.close()

with sync_playwright() as playwright:
    run(playwright)

