import os
import urllib
import requests
import datetime as dt
import dateutil.parser as dparser
import numpy as np
import pandas as pd
pd.set_option('display.max_columns',100)
pd.set_option('display.max_rows',1000)

# Get links from website
html = requests.get("https://bescom.karnataka.gov.in/new-page/Planned%20Outages%20-%20BESCOM%20Works/en").text
try: 
    from BeautifulSoup import BeautifulSoup
except ImportError:
    from bs4 import BeautifulSoup
soup = BeautifulSoup(html)
links = [link.get('href').strip().replace(" ", "%20") for link in soup.find_all('a',href=True) if '.xlsx' in link.get('href') and 'Outage' in link.get('href')]
print(links)

# Save files from links
file_path_list = []
for link in links:
    try:
        filename = link.split("/")[-1]
        urllib.request.urlretrieve(link, filename)
        file_path_list.append(filename)
        print(f"{filename} collected!")
    except Exception as e:
        print(f"{link} link broken?")
        print(f"{repr(e)}")
        
# Fetch files
dfs = {}
for file in file_path_list:
    df = pd.read_excel(file)
    print(f"{file}  {len(df)} {len(df.keys())}")
    dfs[file] = df
    
dfs_list = list(dfs.values())

# Mergability check
# assert all([len(dfs_list[0].columns.intersection(df.columns)) == dfs_list[0].shape[1] for df in dfs_list])

# Merge 
final_df = pd.concat(dfs_list, ignore_index=True).astype(str)
final_df.columns = final_df.columns.str.lower()
final_df.dropna(axis=0, how='all', inplace=True)

#Filter columns
important_columns = []
important_words = ['to', 'from', 'unit', 'date', 'feeder', 'nomen', 'area'
]
for col in final_df.columns:
    if any(important_word in col for important_word in important_words):
        important_columns.append(col)
        
final_df = final_df[important_columns]
specific_df = final_df[(final_df.values=='Marathalli').any(1)]
mask = np.column_stack([specific_df[col].str.contains("F10-TULASI-THEATER-ROAD", na=False) for col in specific_df])
specific_df = specific_df.loc[mask.any(axis=1)]
specific_df['date_date'] = None

for col in specific_df.columns:
    if 'date' in col:
        try:
            specific_df['date_date'] = specific_df[col].apply(lambda x: dparser.parse(x,fuzzy=True).strftime('%Y-%m-%d'))
        except:
            continue
print(specific_df['date_date'])
tomorrow = dt.datetime.now().date() + dt.timedelta(days=1)

if str(tomorrow) in list(specific_df['date_date'].astype(str)):
    dummy_variable = input("\n\t\t\tALERT ALERT ALERT ALERT - POWER FUCKING GOES OUT TOMORROW, GET FUCKED\n\n\n")
else:
    dummy_variable = input("\n\t\t\tNO power cut tomorrow\n\n\n")