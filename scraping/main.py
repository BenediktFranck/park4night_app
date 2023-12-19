# -*- coding: utf-8 -*-
"""
Created on Fri Oct 27 09:38:34 2023

@author: Bened
"""

from webscraper import soup
import pandas as pd
#import parquet


#Read in data record, if not yet available a new one is created
try:
    df = pd.read_parquet('data_base.parquet')
except FileNotFoundError:
    df = pd.DataFrame(data = [], columns = ['place_id', 'title', 'description', 'place_type', 'height_limit', 'creation_user', 
                                            'creation_date', 'services', 'gps', 'country', 'rating', 'count_ratings', 'comments'])


#Read out the last place ID in the DataFrame to continue there
try:
    last_place_id = int(df['place_id'].iloc[-1])
except IndexError: 
    last_place_id = 0

print(last_place_id)
#how many pages should be scraped?
pages_to_scrape = 100

#For loop to write scraped values into a DataFrame
for soup1 in range(last_place_id+1,last_place_id+pages_to_scrape):
    place_id = soup1
    try:
        soup1 = soup(soup1)
        soup1.search()
        if soup1.page_exists():
            if soup1.title() != 'schöneOrte,Wohnmobilstellplätze,Camping-undParkplätze': #Place type should not be scraped
                print(place_id, 'from', last_place_id+pages_to_scrape)
                data = []
                data.append(place_id)
                data.append(soup1.title())
                data.append(soup1.description())
                data.append(soup1.place_type())
                data.append(soup1.height_limit())
                data.append(soup1.creation_user())
                data.append(soup1.creation_date())
                data.append(soup1.services())
                data.append(soup1.gps())
                data.append(soup1.country())
                data.append(soup1.rating())
                data.append(soup1.count_ratings())
                data.append(soup1.comments())
                df.loc[len(df.index)] = data
    except: 
            print('Fehler!')
            break
        
        
#to be able to save it as parquet, df must be converted to string
df = df.astype(str)
df.to_parquet('data_base.parquet')
