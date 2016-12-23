from lxml import html
from datetime import datetime

from lxml.html import HtmlElement
import urllib3

DOMAIN = "http://fit.nsu.ru"
NEWS = '/news'

http = urllib3.PoolManager()


class NewsParser:
    def __init__(self, domain: str, news: str):
        self.categories = []
        self.domain = domain
        self.news_page = self.domain + news

    def __call__(self):
        print("Get {}".format(self.news_page))
        page = html.parse(self.news_page)
        print("Ok")
        categories_list = page.getroot().find_class('categories-list').pop()
        categories_list = categories_list.getchildren()[0].getchildren()
        for li in categories_list:
            self.categories.append(Category(self.domain, li))

        for category in self.categories:
            category()


class Category:
    def __init__(self, domain: str, li: HtmlElement):
        a = li.find(".//a")
        self.href = a.attrib['href']
        self.domain = domain
        self.name = a.text.rstrip().lstrip()  # type: str
        self.items = []

    def __call__(self):
        print("Get category {}".format(self.href))

        r = http.request('POST',
                         self.domain + self.href,
                         fields={'limit': '0'})

        data = r.data.decode('utf-8')
        print("Ok")
        r.release_conn()

        page = html.fromstring(data)

        items_raw = page.find_class('cat-list-row1') + page.find_class('cat-list-row0')

        for tr in items_raw:
            self.items.append(NewsItem(self.domain, tr))

    def __str__(self):
        return "Category {}({})".format(self.name, self.href)


class NewsItem:
    def __init__(self, domain: str, tr):
        self.domain = domain
        a = tr.find(".//a")
        self.head = a.text.rstrip().lstrip()
        self.href = a.attrib['href']
        self.date = tr.find_class('list-date')[0].text.rstrip().lstrip()


news_p = NewsParser(DOMAIN, NEWS)
news_p()
print("Test")