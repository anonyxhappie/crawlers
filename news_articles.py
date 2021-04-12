import os
import json 
import csv 
# from newsfetch.google import google_search
from newsfetch.news import newspaper

# google = google_search('Alcoholics Anonymous', 'https://timesofindia.indiatimes.com/')

# print('google::', google.urls, google.__dict__)
# print('news::', news.__dict__)

import re
import requests
from bs4 import BeautifulSoup
from constants import TOPICS
import asyncio
from asgiref.sync import sync_to_async


def moneycontrol_links(topic):
    print('in write_links of ', topic)

    link_file_name = 'data/links/moneycontrol_' + topic + '.csv'
    # if os.path.exists(link_file_name) and os.stat(link_file_name).st_size != 0:
    #     print('skipping, link file already exists')
    #     return

    base_url = 'https://www.moneycontrol.com/news/'+topic
    page_no = 2559
    last_url = ''
    with open(link_file_name, 'a+') as link_file: 
        csv_writer = csv.writer(link_file) 
        while page_no < 3940:

            page = requests.get(base_url + '/page-'+ str(page_no) + '/', headers = {'User-agent': 'your bot 0.1'})
            soup = BeautifulSoup(page.content, 'html.parser')
            soup = soup.find(id="cagetory")
            links = soup.find_all("a")

            for link in links:
                url = link.get('href')
                if url == last_url: continue
                print(url)
                csv_writer.writerow([url,])
                last_url = url 
            
            print('page_no', page_no)
            page_no += 1

def write_links(topic):
    print('in write_links of ', topic)

    link_file_name = 'data/links/news_' + topic + '.csv'
    if os.path.exists(link_file_name) and os.stat(link_file_name).st_size != 0:
        print('skipping, link file already exists')
        return

    base_url = 'https://www.google.co.in/search?tbm=nws&q='
    page = requests.get(base_url + topic, headers = {'User-agent': 'your bot 0.1'})
    print('page', page)
    soup = BeautifulSoup(page.content)
    links = soup.find_all("a", href=re.compile("(?<=/url\?q=)(htt.*://.*)"))
    page_no = 0
    
    with open(link_file_name, 'a+') as link_file: 
        csv_writer = csv.writer(link_file) 
        last_url = ''
        while len(links) > 1:
            for link in soup.find_all("a", href=re.compile("(?<=/url\?q=)(htt.*://.*)")):
                url = re.split(":(?=http)",link["href"].replace("/url?q=",""))
                url = url[0].split('&', 1)[0]
                if 'accounts.google.com' in url or url == last_url: continue
                print(url)
                csv_writer.writerow([url,])
                last_url = url 

            page_no += 10
            page = requests.get(base_url + topic + '&start=' + str(page_no), headers = {'User-agent': 'your bot 0.1'})
            print('page', page)
            soup = BeautifulSoup(page.content)
            links = soup.find_all("a", href=re.compile("(?<=/url\?q=)(htt.*://.*)"))

async def prepare_links():
    print('preparing links')
    for topic in TOPICS:
        await sync_to_async(write_links)(topic)
        print('links ready for', topic)

def write_articles(topic):
    # link_file_name = 'data/links/news_' + topic + '.csv'
    link_file_name = 'data/links/moneycontrol_' + topic + '.csv'
    if not os.path.exists(link_file_name) or os.stat(link_file_name).st_size == 0:
        print('skipping, link file does not exist')
        return
    

    with open(link_file_name, 'r') as link_file:
        csv_reader = csv.reader(link_file) 
        link_count = 0
        for row in csv_reader:
            link = row[0]
            link_count += 1
            print(link)
            news = newspaper(link)
            news_dict = news.__dict__
            # print(news_dict['get_dict'])
            if news_dict['get_dict']['headline'] == '': return
            # article_file_name = 'data/articles/articles_' + topic + '.csv'
            article_file_name = 'data/articles/moneycontrol_' + topic + '.csv'
            # if os.path.exists(link_file_name) and os.stat(link_file_name).st_size != 0:
            #     print('skipping, article file already exist')
            #     continue
            
            with open(article_file_name, 'a+') as article_file:
                csv_writer = csv.writer(article_file) 
                if link_count == 1:
                    csv_writer.writerow(news_dict['get_dict'].keys()) 
                
                csv_writer.writerow(news_dict['get_dict'].values()) 
                
        print('total_links', link_count)


async def prepare_articles():
    print('preparing articles')
    for topic in TOPICS:
        await sync_to_async(write_articles)(topic)
        print('articles ready for', topic)

def main():
        
    loop = asyncio.get_event_loop()
    # loop.run_until_complete(prepare_links())
    # loop.run_until_complete(prepare_articles())
    loop.run_until_complete(write_articles('india'))
    loop.close()

if __name__ == '__main__':
    main()
    