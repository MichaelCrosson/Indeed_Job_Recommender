from playwright.sync_api import sync_playwright
import time
with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context= browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"
    )
    # page = browser.new_page()
    page = context.new_page() #instead of using browser.new_page we will use browser.new_page as it has user-agent
    page.goto('https://www.indeed.com/jobs?q=datascience&vjk=6808c8f348c5f750')
    time.sleep(3)
    last_height = page.evaluate("document.body.scrollHeight")

    while True:
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(2000)  # Wait for 2 seconds to load new content
        new_height = page.evaluate("document.body.scrollHeight")

        if new_height == last_height:
            break
        last_height = new_height
    
    content = page.content()
    print(content) #this line can be used to study SEO of a website. no need in web scraping
    with open('content.html', 'w', encoding='utf-8') as f:
        f.write(content)
    
    browser.close()
    
    
