import os
import time
# Must pip install API 
from playwright.sync_api import sync_playwright
import pandas as pd
from bs4 import BeautifulSoup
from googletrans import Translator
from langdetect import detect
translator = Translator()

# Directory containing the HTML files
# 'C:/Users/user/...'
directory = ''

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

# Scrape Indeed.com job reviews to localized html pages for scraping
# Start Playwright web scrape
m = 0
with sync_playwright() as p:
    for company in range(len(companies)):
        # Itterate by 20s due to Indeed layout
        for i in range(0, 100, 20):
            # Initialize the browser and page
            browser = p.chromium.launch(headless=False)
            context= browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"
            )
            # Scroll to load content
            page = context.new_page() 
            page.goto(f'https://www.indeed.com/cmp/{companies[company]}/reviews?fcountry=ALL&start={i}')
            time.sleep(1)
            last_height = page.evaluate("document.body.scrollHeight")

            while True:
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                page.wait_for_timeout(1000) 
                new_height = page.evaluate("document.body.scrollHeight")

                if new_height == last_height:
                    break

                last_height = new_height

            # Save static html page with details 
            file_name = f'content{m}.html'
            # Save to relevant directory
            file_path = os.path.join(directory, file_name)

            # Get page content
            content = page.content()
            print(content) 
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            m += 1
            browser.close()

# Function to extract reviews from a single HTML file
def extract_reviews_from_html(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    soup = BeautifulSoup(content, 'html.parser')
    
    # Extracting the company name from the meta description
    company_meta = soup.find('meta', {'name': 'description'})
    if company_meta:
        description = company_meta.get('content', '')
        if 'reviews from' in description and 'employees' in description:
            company_name = description.split('reviews from')[1].split('employees')[0].strip()
        else:
            company_name = "Unknown"
    else:
        company_name = "Unknown"

    reviews_data = []
    
    # Extract each review block (assuming class 'cmp-Review' for individual reviews)
    reviews = soup.find_all('div', {'data-testid': 'reviews[]'})
    
    for review in reviews:
        # Extract the job title
        job_title = review.find('a', class_='css-1i8sxhj').text if review.find('a', class_='css-1i8sxhj') else "Unknown"
        
        # Extract the review text
        review_text = review.find('span', itemprop='reviewBody').text if review.find('span', itemprop='reviewBody') else "No review text"
        if review_text:
                try:
                    # Detect the language of the review
                    detected_language = detect(review_text)

                    # Translate if the language is not English
                    if detected_language != 'en':
                        translated_review = translator.translate(review_text, dest='en').text
                        review_text = translated_review
                except Exception as e:
                    print(f"Error in translation: {e}")

        # Extract the rating
        rating_meta = review.find('meta', {'itemprop': 'ratingValue'})
        rating = rating_meta['content'] if rating_meta else "No rating"
        
        reviews_data.append({
            'Company': company_name,
            'Job Title': job_title,
            'Rating': rating,
            'Review': review_text
        })
    
    return reviews_data

# Initialize a list to store all reviews
all_reviews = []

# Loop through each HTML file in the folder
for i in range(540):  # 540 htmls
    file_path = os.path.join(directory, f'content{i}.html')
    if os.path.exists(file_path): 
        reviews = extract_reviews_from_html(file_path)
        all_reviews.extend(reviews)

# convert collected reviews into a dataFrame
df_reviews = pd.DataFrame(all_reviews)

# save the dataFrame to csv
df_reviews.to_csv('company_reviews.csv', index=False, encoding='utf-8') 
