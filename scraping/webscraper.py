# -*- coding: utf-8 -*-
"""
Created on Thu Oct 19 15:56:06 2023

@author: Bened
"""

import requests
from bs4 import BeautifulSoup

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36"}
base_url = 'https://park4night.com/de/place/'
class soup:
    
    def __init__(self, place_id):
        self.place_id = place_id
        self.soup1 = None
        self.error = None
    
    
    def search(self):
        page = requests.get(base_url+str(self.place_id), headers=headers)
        error = page.status_code
        soup1 = BeautifulSoup(page.text, features='lxml')
        self.soup1 = soup1
        self.error = error
        return soup1
    
    def page_exists(self):
        '''
        Checks if place exists.
    
    
            Returns:
                boolean: True if place exists, False if not.
        '''
        if self.error == 404:
            return False
        else: 
            return True
        
    def title(self):
        '''
        Scrapes the place title.
    
        Returns:
            title (str): Title of the place.
        '''
        title = self.soup1.title.text
        title = ''.join(title.split()[3:])
        return title
    
    def description(self):
        '''
        Scrapes the place description.
    
        Returns:
            description (str): Description of the place.
        '''
        try:
            description = self.soup1.find(class_="place-info-description mt-4")
            description = description.find_all(class_="")[0].text
            return description
        except:
            return None
        
    def place_type(self):
        '''
        Scrapes the place type.
    
        Returns:
            place_type (str): Place Type of the place.
        '''
        place_type = self.soup1.find(class_="place-specs py-5")
        place_type = place_type.find_all(class_="place-specs-type tag text-secondary")[0].text
        place_type = "".join([i for i in place_type if not i.isdigit()])
        place_type = place_type.strip('#')[3:]
        return place_type
    
    def height_limit(self):
        '''
        Scrapes the height limit
    
        Returns:
            height_limit (bool): If height limit exists then true, else false.
        '''
        height_limit = self.soup1.find(class_="place-info-details mt-4").text
        height_limit = 'Höhe begrenzt auf' in height_limit
        return height_limit
        
    def creation_date(self):
        '''
        Scrapes the creation date of the place.
    
        Returns:
            creation_date (str): Creation date of the place.
        '''
        created_by = self.soup1.find(class_="place-header-creation caption text-gray").text.split()
        creation_date = created_by[2]
        return creation_date
    
    def creation_user(self):
        '''
        Scrapes the user who created the place.
    
        Returns:
            creation_user (str): User who created the place.
        '''
        created_by = self.soup1.find(class_="place-header-creation caption text-gray").text.split()
        creation_user = created_by[-1]
        return creation_user
        
    def rating(self):
        '''
        Scrapes the place rating.
    
        Returns:
            rating (float): Rating of the place.
        '''
        rating = self.soup1.find_all(class_="place-feedback-average mt-3 mb-3")[0].text.split()[-1].split('/')[-2]
        if rating == '':
            rating = None
        else: 
            float(rating)
        return rating
    
    def count_ratings(self):
        '''
        Scrapes the amount of given ratings.
    
        Returns:
            rating_count (float): Amount of given ratings.
        '''
        rating_count = self.soup1.find_all(class_="place-feedback-average mt-3 mb-3")[0].find('strong')
        rating_count = rating_count.text.split('(')[1].split()[0]
        try:
            rating_count = int(rating_count)
        except:
            rating_count = 0
        return rating_count
        
    def services(self):
        '''
        Scrapes the services of the place.
    
        Returns:
            list : List with all services.
        '''
        try:
            services = self.soup1.find("div", class_="col d-flex")
            services = services.find_all('li')
            services_list = []
            for i in services:
               services_list.append(i.find('img')['title'])
            return services_list
        except:
            return [None]
        
    def gps(self):
        '''
        Scrapes the gps position of the place.
    
        Returns:
            tuple : Tuple with latitude and longitude.
        '''        
        results = self.soup1.find_all(class_="place-info-location mt-5 mb-4")
        gps = results[0]('span')
        gps = gps[0].text.split()
        lat = gps[0].strip(',')
        lng = gps[1]
        return (lat,lng)
        
    def country(self): 
        '''
        Scrapes the country of the place.
    
        Returns:
            country (str): Country of the place.
        '''
        results = self.soup1.find(class_="place-info-location mt-5 mb-4")
        country = results.find_all('p')
        country = country[1].text.split(',')[-1].strip()
        return country
    
    def comments(self):  
        '''
        Scrapes all comments of the place, including additional informations.
    
        Returns:
            comment_list (list) : List with all comments, including comment date, comment user, comment rating.
        '''
        try:
            results = self.soup1.find_all('li', {'class': 'col-12 col-lg-6'})
            comment_list = []
            for cmt in results:
                comments = []
                comment = cmt.find(class_="mt-4").text
                comments.append(comment)
                comment_date = cmt.find(class_="caption text-gray").text.replace('/','.')
                comments.append(comment_date)
                try:
                    comment_rating = cmt.find(class_="rating-note").text.split('/')[0]
                    comment_rating = int(comment_rating)
                except:
                    comment_rating = None
                comments.append(comment_rating)
                user = cmt.find(class_="d-flex direction-column").find_all('strong')[0].text
                comments.append(user)
                comment_list.append(comments)
            return comment_list
        except:
            return [None]
        
        
        
        
        
        
        
        
        
        
        
        
        