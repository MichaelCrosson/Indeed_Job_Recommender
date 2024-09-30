from bs4 import BeautifulSoup
import pandas as pd
with open('content.html', 'r', encoding='utf-8') as f:
    content = f.read()
    
soup = BeautifulSoup(content,features="lxml") #here "html.parser"can be used instead of "lxml"

# listings = soup.select('td.resultContent') #can be written without tag only ".resultContent"
listings = soup.find_all('td',class_ ='resultContent')

total_data = []
for i,listing in enumerate(listings):
  
    title = listing.select('[title]')[0].get_text()
    # print(i,title)
    
    company_name = listing.select('[data-testid="company-name"]')[0].get_text()
    # print(company_name)
    
    company_location = listing.select('[data-testid="text-location"]')[0].get_text()
    
    total_data.append([title,company_name,company_location])
    
df = pd.DataFrame(total_data, columns=["Title","Company Name","Company Location"])
print(df)

# df.to_excel("d.xlsx",index=False)
# df.to_csv("d.csv", index= False)

  # print("-------------1st method-------------------")
    # title = listing.find('span',{'title':True}).get_text()
    # print(i,title)
    # print("-----------2nd ---------------------")
    # title2 = listing.select(".jobTitle")[0].get_text()
    # print(i,title)
    # print("--------------3rd ------------------")
    # title = listing.select_one('span[title]').get_text()
    # print(i,title)
    # print("-------------4 th -------------------")
    # title = listing.select('span[title]')[0].get_text()
    # print(i,title)
    # print("------------- 5 th -------------------")
    # title = listing.select_one('span[title]:not([title=""])').get_text()
    # print(i,title)
    # print("--------------6rd ------------------")
    # title = listing.select_one('span[title]:not([title= False])').get_text()
    # print(i,title)
    # print("--------------7th ------------------")
    
    # print(company_location)
    # print("--------------8th ------------------")
    # company_location = listing.find('div',{'data-testid':'text-location'}).get_text()
    # print(company_location)
