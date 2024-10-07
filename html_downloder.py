from playwright.sync_api import sync_playwright
import time
import os

m = 0
with sync_playwright() as p:
    for i in range(0, 140, 20):
        browser = p.chromium.launch(headless=False)
        context= browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"
        )
        # page = browser.new_page()
        page = context.new_page() #instead of using browser.new_page we will use browser.new_page as it has user-agent
        page.goto(f'https://www.indeed.com/cmp/Ey/reviews?fcountry=ALL&start={i}')
        time.sleep(1)
        last_height = page.evaluate("document.body.scrollHeight")

        while True:
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            page.wait_for_timeout(1000) 
            new_height = page.evaluate("document.body.scrollHeight")

            if new_height == last_height:
                break

            last_height = new_height

        file_name = f'content{m}.html'
        directory = r'C:/Users/nosso/OneDrive/Desktop/indeed.com/htmls'
        file_path = os.path.join(directory, file_name)

        content = page.content()
        print(content) 
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        m += 1
        browser.close()
        
        
