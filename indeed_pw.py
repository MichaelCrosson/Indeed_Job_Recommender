from playwright.sync_api import sync_playwright, Playwright
import pandas as pd

with open('content.html', 'r', encoding='utf-8') as f:
    content = f.read()

# print(str(content).split('data-testid="company-name"')[1])

with sync_playwright() as playwright:
    browser = playwright.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto('file://C:/Users/nosso/OneDrive/Desktop/indeed.com')  

    listings = page.query_selector_all('td.resultContent')

    total_data = [[1,2,3]]
    for listing in listings:
        title = listing.query_selector('[title]').inner_text()
        company_name = listing.query_selector('data-testid="company-name"').inner_text()
        company_location = listing.query_selector('[data-testid="text-location"]').inner_text()
        total_data.append([title, company_name, company_location])

    browser.close()

    df = pd.DataFrame(total_data, columns=["Title", "Company Name", "Company Location"])
    print(df)
