# park4night App (Data Science Project)

# Project Overview 
* This project is a result of my final thesis at the [Data Science. Institute by Fabian Rappert](https://github.com/mwaskom/seaborn/blob/master/seaborn/utils.py).
* Scraped almost 300000 places and over 2.7 million comments from [park4night](https://park4night.com/) using python.
* Created a mySQL database.
* Created a [Streamlit](https://streamlit.io/)  App for searching and filtering places.
* Made a Data Analyses with Tableau on the scraped data.

## Code and Resources Used 
**Python Version:** 3.11  
**Packages:** requests, BeautifulSoup, pandas

## Web Scraping
Every place has a unique place ID and with that an own web-address accessible with the base-url: https://park4night.com/en/place/ followed by the place ID.
For example: https://park4night.com/en/place/88726 
The following pictures shows where to find the scraped data.

<img width="1124" alt="Bildschirmfoto 2023-12-19 um 13 34 59" src="https://github.com/BenediktFranck/park4night_app/assets/150929764/7667a04c-5bcb-4911-97b1-c7b2fb896a02">
<img width="1104" alt="Bildschirmfoto 2023-12-19 um 13 39 16" src="https://github.com/BenediktFranck/park4night_app/assets/150929764/e855b8f9-6a2b-4e94-a253-bfd88623dff2">


The webscraping uses requests and beautifulsoup. 
To save the scraped data, parquet will be used.
You can select how many pages you want to scrape with the variable 'pages_to_scrape'.
By default the main program starts at the last scraped place ID if there already exists an 'data_base.parquet' file. If not a new pandas DataFrame will created.

The DataFrame looks like this:
![df](https://github.com/BenediktFranck/park4night_app/assets/150929764/9c24666a-952e-4bb2-964d-e623bc5e725b)

## Data Cleaning
After scraping the data, I needed to clean it up so that I could create a mySQL database. Therefore I created a Jupyter Notebook.

...to be continued
