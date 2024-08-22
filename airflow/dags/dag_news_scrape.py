from airflow import DAG
from datetime import datetime, timedelta
from airflow.operators.python import PythonOperator
from airflow.decorators import dag, task

from bs4 import BeautifulSoup
import requests

default_args = {
    'owner': 'matea',
    'retries': 5,
    'retry_delay': timedelta(minutes=2)
}

@dag(
    dag_id='dag_diplomski_v2',
    description='second dag for news classification with taskflow',
    default_args=default_args,
    start_date=datetime(2024,8,21,4),
    schedule_interval='@daily')
def news_scraper_etl():

    @task()
    def scrape():
        html_data = requests.get('https://feeds.bbci.co.uk/news/rss.xml')
        return html_data
    
    @task()
    def get_soup(scraped_text: str) -> BeautifulSoup:
        soup = BeautifulSoup(scraped_text.text, "xml")	
        return soup

    @task()
    def clean_scraped(soup: BeautifulSoup) -> str:
        articles = soup.find_all('item')
        res = []
        current_item = 0
        while current_item < len(articles):
            article_headline = articles[current_item].title.text
            article_description = ["".join(article_part + " " for article_part in articles[current_item].text.split("\n")[:-5])][0] 
            res.append(f"{article_headline} {article_description[len(article_headline)+2:]}")
            current_item += 1
        return res

    @task()
    def make_dict(clean_text: str) -> dict:
        res_dict = dict()
        for i,x in enumerate(clean_text):
            res_dict[str(i)] = x
        print(res_dict)
        return res_dict
    
    scraped_text = scrape()
    soup = get_soup(scraped_text)
    clean_text = clean_scraped(soup)
    res_dict = make_dict(clean_text)

news_scraper_etl()

