from custom_classes.fetch_data import FetchData

class News:
    def fetch_news(self):
        url = f'https://feeds.bbci.co.uk/news/rss.xml'
        FetchData(url=url, file_name=f'news').run()


if __name__ == '__main__':
    News().fetch_news()