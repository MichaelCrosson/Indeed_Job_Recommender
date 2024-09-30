import pandas as pd
with open('content.html','r', encoding='utf-8') as f:
    content = f.read()

listings = content.split('aria-label="full details of ')[1:]

total_data=[]
for listing in listings:
    title = listing.split('"')[0]
    company_name= listing.split(' data-testid="company-name" ')[1].split('>')[1].split('<')[0]
    company_location = listing.split('data-testid="text-location"')[1].split('>')[1].split('<')[0]
   
    print(f'title name: {title}')
    # print("++++++++++++++++++++++++++++++++++++++++++++++++")
    print(f'company_name : {company_name}')
    # print("***************************************")
    print(f'company_location : {company_location}')
    # print(listing[:1500])
    print("===========================================")
    total_data.append([title,company_name,company_location])
    
df = pd.DataFrame(total_data, columns=["Title","Company Name","Company Location"])
print(df)

# df.to_excel("d.xlsx",index=False)
# df.to_csv("d.csv", index= False)
