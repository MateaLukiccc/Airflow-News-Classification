import requests
import os
os.environ['no_proxy'] = '*'

class FetchData:
    def __init__(self, url: str, file_name: str) -> None:
        if not url:
            raise Exception('You have not provided a url to fetch data')

        self.web_link = url
        self.file_name = file_name

    def fetch(self):
        html_data = requests.get(self.web_link).content
        return html_data
    
    def run(self):
        data = self.fetch()
        with open(f'{self.file_name}.html', 'wb') as file:
            file.write(data)


if __name__ == '__main__':
    FetchData('https://feeds.bbci.co.uk/news/rss.xml', 'test').run()

        