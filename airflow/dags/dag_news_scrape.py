from datetime import datetime, timedelta
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.decorators import dag, task

from bs4 import BeautifulSoup
import requests
import csv
import os

# Set the TRANSFORMERS_CACHE environment variable
os.environ['TRANSFORMERS_CACHE'] = '.'

from transformers import pipeline

default_args = {
    'owner': 'matea',
    'retries': 5,
    'retry_delay': timedelta(minutes=2)
}

@dag(
    dag_id='dag_diplomski',
    description='dag for news classification with taskflow',
    default_args=default_args,
    start_date=datetime(2024,9,15,4),
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
    
    @task()
    def classification(to_classify: dict) -> dict:
        res = dict()
        for pred, text in zip(pipeline("text-classification", model="Lukiccc/my_awesome_model")(list(to_classify.values())), list(to_classify.values())):
            res[text] = pred
        return res
    
    @task()
    def save_to_csv(to_save: dict):
        with open(f"mycsvfile_{datetime.now()}.csv", "a", newline="") as f:
            w = csv.DictWriter(f, to_save.keys())
            w.writeheader()
            w.writerow(to_save)
    
    @task()
    def create_insert_string(to_insert: dict) -> str:
        res: str = ''
        starting_item = 0
        today = datetime.today().date()
        to_replace_first = "'"
        to_replace_second = '"'
        replacement = ""

        for i, (key, value) in enumerate(to_insert.items()):
            text = key.replace(to_replace_first, replacement)
            text = text.replace(to_replace_second, replacement)
            label = value['label']

            if i == starting_item:
                res += f"('{today}', '{i}', '{text}', '{label}')"
            else:
                res += f",('{today}', '{i}', '{text}', '{label}')"
    
        return res
    
    @task()
    def insert_data(insert_string: dict, db_created: bool) -> str:
        if not db_created:
            raise ValueError("db is not created")
        PostgresOperator(
            task_id='insert_into_table',
            postgres_conn_id='postgres_localhost',
            sql=f'''
                insert into news(dt, news_id, text, label) values {insert_string};
                '''
        )

    @task
    def create_database_task():
        PostgresOperator(
            task_id='create_postgres_table',
            postgres_conn_id='postgres_localhost',
            sql='''
                create table if not exists news(
                    dt date,
                    news_id character varying,
                    primary key (dt, news_id),
                    text character varying,
                    label character varying
                )
                '''
            )
        return True

    db_created = create_database_task()    
    scraped_text = scrape()
    soup = get_soup(scraped_text)
    clean_text = clean_scraped(soup)
    res_dict = make_dict(clean_text)
    classified = classification(res_dict)
    insert_data(create_insert_string(classified), db_created)
    save_to_csv(classified)

news_scraper_etl()

