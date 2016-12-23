from lxml import html
from datetime import datetime

from lxml.html import HtmlElement

DOMAIN = "http://fit.nsu.ru"
NEWS = '/news'


class NewsParser:
    def __init__(self, domain: str, news: str):
        self.categories = []
        self.domain = domain
        self.news_page = self.domain + news

    def __call__(self):
        page = html.parse(self.news_page)
        categories_list = page.getroot().find_class('categories-list').pop()
        categories_list = categories_list.getchildren()[0].getchildren()
        for li in categories_list:
            self.categories.append(Category(li))


class Category:
    def __init__(self, li: HtmlElement):
        a = li.find(".//a")
        self.href = a.attrib['href']
        self.name = a.text.rstrip().lstrip()  # type: str

    def __str__(self):
        return "Category {}({})".format(self.name, self.href)


news = NewsParser(DOMAIN, NEWS)
news()
print(news.categories)
