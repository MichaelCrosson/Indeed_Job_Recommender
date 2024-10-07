from bs4 import BeautifulSoup
import pandas as pd
import os

files = os.listdir('C:/Users/nosso/OneDrive/Desktop/indeed.com/htmls')
file_count = len([file for file in files if os.path.isfile(os.path.join('C:/Users/nosso/OneDrive/Desktop/indeed.com/htmls', file))])

total_data = []
for i in range(file_count):
  with open(f'C:/Users/nosso/OneDrive/Desktop/indeed.com/htmls/content{i}.html', 'r', encoding='utf-8') as f:
      content = f.read()
      
  soup = BeautifulSoup(content,features="lxml") #here "html.parser"can be used instead of "lxml"

  # listings = soup.select('td.resultContent') #can be written without tag only ".resultContent"
  listings = soup.find_all('td',class_ ='resultContent')

  for i,listing in enumerate(listings):
      
      company_name = listing.select('[itemprop="name"]')[0].get_text()
      
      review = listing.select('[class="css-15r9gu1 eu4oa1w0"]')[0].get_text()

      job = listing.select('[itemprop="author"]')[0].get_text()
      
      total_data.append([company_name, review, job])
      
df = pd.DataFrame(total_data, columns=["Company Name","Review","Job"])
print(df)

  # df.to_excel("d.xlsx",index=False)
  # df.to_csv("d.csv", index= False)
