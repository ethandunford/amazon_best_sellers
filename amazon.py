# -- ---------------------------------------------------------------------------
# --
# -- Title:        Amazon.py
# -- Desc:         Get all of the best selling books from amazon
# -- Author:       Ethan Dunford <github.com/ethandunford>
# -- Date:         25/05/2018
# -- Version:      1
# --
# -- ---------------------------------------------------------------------------
from time import sleep, strftime
from datetime import datetime
from bs4 import BeautifulSoup
import requests
import json
import time 
import re

class Amazon(object):

    def __init__(self):
        self.base_url = 'https://www.amazon.co.uk/gp/bestsellers/books'
        self.soup_obj = None
        self.pages    = {}
        self.data     = []

    def message(self, message):
        print(''.join(('[', strftime("%Y-%m-%d %H:%M:%S"), ']: ', message)))
    
    def write_data(self, data):
        file = open(''.join(('amazon_best_sellers_', strftime('%d%m%Y'), '.txt')), 'w')
        file.write(data)
        file.close()

    def get_pages(self):
        # -- Get list of pages
        if self.soup_obj:
            items = self.soup_obj.findAll('li', {'class': 'zg_page'})
            for i in items:
                _url = i.find('a').get('href')
                page = re.search('pg=[0-9]', _url)
                if page:
                    page = page.group().replace('pg=', '')
                    self.pages[page] = _url

    def get_rank(self, data):
        data = data.find('span', {'class': 'zg_rankNumber'})
        if data:
            return data.text.lstrip().rstrip().replace('.', '')

    def get_title(self, data):
        data = data.find('div', {'class': 'p13n-sc-truncate'})
        if data:
            return data.text.lstrip().rstrip()

    def get_rating(self, data):
        data = data.find('i', {'class': 'a-icon-star'})
        if data:
            data = data.find('span', {'class': 'a-icon-alt'})
            if data:
                return data.text.replace(' out of 5 stars', '')

    def get_url(self, data):
        data =  data.find('div', {'class': 'a-section'})
        if data:
            r = re.search('href=[\'"]?([^\'" >]+)', str(data))
            if r:
                return r.group()

    def get_author(self, data):
        data = data.find('a', {'class': 'a-link-child'})
        if data:
            return data.text

    def get_price(self, data):
        data = data.find('span', {'class': 'p13n-sc-price'})
        if data:
            return data.text

    def get_book_type(self, data):
        data = data.find('span', {'class': 'a-size-small a-color-secondary'})
        if data:
            return data.text

    def page_data(self, soup_obj):
        data = soup_obj.findAll('div', {'class': 'zg_itemImmersion'})
        if data:
            for i in data:
                self.data.append({
                    'rank':          self.get_rank(i),
                    'author':        self.get_author(i),
                    'title':         self.get_title(i),
                    'rating':        self.get_rating(i),
                    'url':           self.get_url(i),
                    'price':         self.get_price(i),
                    'book_type':     self.get_book_type(i)
                })

    def process(self):
        self.message('Getting Amazon best sellers')
        page = requests.get(self.base_url)
        if page.status_code == 200:
            self.soup_obj = BeautifulSoup(page.content, 'html.parser')
            self.get_pages()
            if self.pages:
                self.message(''.join((str(len(self.pages)), ' pages found')))
                for k, v in self.pages.items():
                    self.message(''.join(('Scraping page -> ', v)))
                    page = requests.get(v)
                    if page.status_code == 200:
                        soup_obj = BeautifulSoup(page.content, 'html.parser')
                        self.page_data(soup_obj)
                    else:
                        self.message('Amazon didn\'t return a 200')
                
                if self.data:
                    self.message('Writing data')
                    self.write_data(json.dumps(self.data))
        else:
            self.message('Amazon didn\'t return a 200')


a = Amazon()
a.process()