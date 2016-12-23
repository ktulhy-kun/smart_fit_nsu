from lxml import etree
from lxml import html
from datetime import datetime

from lxml.html import Element
from lxml.html import HtmlElement
import urllib3

DOMAIN = "http://fit.nsu.ru"
NEWS = '/news'

http = urllib3.PoolManager()


def check_find(l: list):
    if 0 == len(l):
        return None
    else:
        return l[0]


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
        _ = check_find(categories_list.getchildren())
        if _ is not None:
            categories_list = _.getchildren()
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

        for item in self.items:
            item()

    def __str__(self):
        return "Category {}({})".format(self.name, self.href)


class NewsItem:
    def __init__(self, domain: str, tr: Element):
        self.domain = domain
        a = tr.find(".//a")
        self.head = a.text.rstrip().lstrip()
        self.href = a.attrib['href']
        el = check_find(tr.find_class('list-date'))
        if el is not None:
            self.date = el.text.rstrip().lstrip()
        self.content = None  # type: Element

    def __call__(self):
        print("Get page {}".format(self.href))
        page = html.parse(self.domain + self.href)
        print("Ok")
        content = check_find(page.getroot().find_class('item-page'))  # type: Element
        if content is not None:
            return

        h2 = content.find(".//h2")
        dl = check_find(content.find_class("article-info"))  # type: Element
        if dl is not None:
            date_el = check_find(dl.find_class('modified'))
            date = date_el.text.rstrip().lstrip()
            print(date)
            # f.e. 28.07.2016 12:20
            self.date = datetime.strptime(date[10:], "%d.%m.%Y %H:%M")
        content.remove(h2)
        if dl is not None:
            content.remove(dl)
        for tag in content.iter():  # type: Element
            if 'style' in tag.attrib:
                del tag.attrib['style']

        self.content = content

    def __str__(self):
        if self.content:
            return etree.tostring(self.content, pretty_print=True)
        return "==Content Missing=="


news_p = NewsParser(DOMAIN, NEWS)
news_p()
print("Test")
