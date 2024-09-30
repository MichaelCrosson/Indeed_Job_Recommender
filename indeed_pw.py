from playwright.sync_api import sync_playwright, Playwright
import pandas as pd

with open('content.html', 'r', encoding='utf-8') as f:
    content = f.read()

from playwright.sync_api import sync_playwright
import pandas as pd

with sync_playwright() as playwright:
    browser = playwright.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto('file://D:/SEO Tanvir BD/AI Projects to publish/P-9 (html_dwonload + parse)/content.html')  # Replace with the actual path or URL

    listings = page.query_selector_all('td.resultContent')

    total_data = []
    for listing in listings:
        title = listing.query_selector('[title]').inner_text()
        company_name = listing.query_selector('[data-testid="company-name"]').inner_text()
        company_location = listing.query_selector('[data-testid="text-location"]').inner_text()
        total_data.append([title, company_name, company_location])

    browser.close()

    df = pd.DataFrame(total_data, columns=["Title", "Company Name", "Company Location"])
    print(df)


    
    # P-9 My own/content.html
    # D:\SEO Tanvir BD\AI Projects to publish\P-9 My own\content.html
