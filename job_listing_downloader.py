# Must pip install API 
from playwright.sync_api import sync_playwright
import time
import os
from bs4 import BeautifulSoup
import pandas as pd

# Save to relevant directory
# 'C:/Users/user/...'
csv_output_path = '/job_listings.csv' # CSV save path - add name of csv
html_directory = ''  # Directory to save HTML files

# Define companies
companies = [ "Walmart", "Amazon", "Apple", "CVS Health", "UnitedHealth Group",
                "Exxon Mobil", "Berkshire Hathaway", "Alphabet", "McKesson",
                "AmerisourceBergen", "Costco Wholesale", "Cigna", "Microsoft",
                "Cardinal Health", "Chevron", "Home Depot", "Walgreens Boots Alliance",
                "Marathon Petroleum", "Elevance Health", "Kroger", "Ford Motor",
                "Verizon", "JPMorgan Chase", "General Motors", "Centene",
                "Meta Platforms", "Comcast", "Phillips 66", "Valero Energy",
                "Dell Technologies", "Tesla", "PepsiCo", "ADM", "Fannie Mae",
                "IBM", "Johnson & Johnson", "State Farm Insurance",
                "Archer Daniels Midland", "Procter & Gamble", "Raytheon Technologies",
                "Humana", "Freddie Mac", "General Electric", "Target", "Boeing",
                "Caterpillar", "Pfizer", "Lockheed Martin", "Intel", "MetLife",
                "UPS", "Goldman Sachs", "Morgan Stanley", "Wells Fargo", "Lowe's",
                "AIG", "HCA Healthcare", "Cisco Systems", "Disney", "Merck",
                "Coca-Cola", "AbbVie", "ConocoPhillips", "Best Buy", "Dow",
                "Charter Communications", "Energy Transfer", "New York Life Insurance",
                "Deere", "American Express", "T-Mobile US", "Honeywell",
                "Northrop Grumman", "Travelers", "Oracle", "Thermo Fisher Scientific",
                "TJX", "Johnson Controls", "HP", "General Dynamics",
                "Publix Super Markets", "USAA", "3M", "Exelon", "Dollar General",
                "Union Pacific", "Liberty Mutual Insurance", "Abbott Laboratories",
                "Bristol-Myers Squibb", "Truist Financial", "Micron Technology",
                "Progressive", "Enterprise Products", "Nationwide", "Nike",
                "Stryker", "Marriott International", "Halliburton", "Eli Lilly",
                "Paccar", "Altria", "Starbucks", "Cummins", "PNC Financial Services",
                "Qualcomm", "Plains GP Holdings", "Applied Materials", "Kraft Heinz" ]

# Scrape Indeed.com job postings to localized html pages for scraping - run company review_bs4 after
m = 0
listdf = []
# Start Playwright web scrape
with sync_playwright() as p:
    for j in companies:
        for i in range(0, 150, 150):
            # Initialize the browser and page
            browser = p.chromium.launch(headless=False)
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"
            )
            page = context.new_page() 
            page.goto(f'https://www.indeed.com/cmp/{j}/jobs?q=&l=#cmp-skip-header-mobile&start={i}')
            time.sleep(1)
            
            # Scroll to load content
            last_height = page.evaluate("document.body.scrollHeight")
            while True:
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                page.wait_for_timeout(500) 
                new_height = page.evaluate("document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height
            
            # Get page content
            content = page.content()
            browser.close()
            
            # Save the HTML file of the main job listing
            with open(os.path.join(html_directory, f'content_jobs_{m}.html'), 'w', encoding='utf-8') as f:
                f.write(content)
            m += 1

            # Webscraping ####################################################################################

            # Parse the content using BeautifulSoup
            soup = BeautifulSoup(content, features="html.parser")
            
            # Find job listings using a tag that contains 'data-jk'
            listings = soup.find_all('a', attrs={'data-jk': True})
            links = [list.get('data-jk') for list in listings if list.get('data-jk')]

            # Visiting ####################################################################################
            
            # Visit each job listing individually
            for x in links[:150]:
                browser = p.chromium.launch(headless=False)
                context = browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"
                )
                page = context.new_page()
                page.goto(f'https://www.indeed.com/cmp/{j}/jobs?jk={x}&q=&l=&start=0')
                time.sleep(1)
                
                # Get the job details content
                content = page.content()
                browser.close()

                # Save the HTML file of the job details
                with open(os.path.join(html_directory, f'content_jobs_details_{m}.html'), 'w', encoding='utf-8') as f:
                    f.write(content)
                m += 1

                # Webscraping ####################################################################################
                
                # Parse job details page
                soup = BeautifulSoup(content, 'html.parser')
                
                title_tag = soup.find('span', class_='css-1avvf63 e1wnkr790')
                if title_tag:
                    title = title_tag.get_text()
                else:
                    title = "N/A"

                location_tag = soup.find('span', class_='css-1vmtjbe e1wnkr790')
                if location_tag:
                    location = location_tag.get_text()
                else:
                    location = "N/A"

                wage_tag = soup.find('span', class_='css-1difit4 e1wnkr790')
                if wage_tag:
                    wage = wage_tag.get_text()
                else:
                    wage = "N/A"

                description_tag = soup.find('div', {'data-testid': 'jobDetailDescription', 'class': 'css-1bh0oyf eu4oa1w0'})
                if description_tag:
                    description = ''.join(description_tag.stripped_strings)
                else:
                    description = "N/A"

                # Append to list
                listdf.append([j, title, location, wage, description])

    # Convert list to DataFrame
    df = pd.DataFrame(listdf, columns=["Company Name", "Title", "Company Location", "Wage", "Description"])
    print(listdf)
    
    # Save DataFrame to CSV
    df.to_csv(csv_output_path, index=False, encoding='utf-8')
