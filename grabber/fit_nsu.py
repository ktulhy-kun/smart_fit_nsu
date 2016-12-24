from traceback import print_stack

from lxml import html
from datetime import datetime

from lxml.html import Element
from lxml.html import HtmlElement

import urllib3

from .db import Category as DBCategory, NewsItem as DBNewsItem

http = urllib3.PoolManager()

POSTGRES_INTEGER_MAX_RANGE = 2147483647


def check_find(l: list):
    if 0 == len(l):
        print("Error while get data from element")
        print_stack()
        return None
    else:
        return l[0]


class NewsParser:
    def __init__(self, domain: str, news: str, session):
        self.categories = []
        self.domain = domain
        self.news_page = self.domain + news
        self.session = session

    def __call__(self):
        print("Get {}".format(self.news_page))
        page = html.parse(self.news_page)
        print("Ok")
        categories_list = page.getroot().find_class('categories-list').pop()
        _ = check_find(categories_list.getchildren())
        if _ is not None:
            categories_list = _.getchildren()
            for li in categories_list:
                self.categories.append(Category(self.domain, li, self.session))

            for category in self.categories:
                category()


class Category:
    def __init__(self, domain: str, li: HtmlElement, session):
        a = li.find(".//a")
        self.href = a.attrib['href']
        self.domain = domain
        self.name = a.text.rstrip().lstrip()  # type: str
        self.items = []
        self.s = session
        self.db_obj = self._work_db()

    def _work_db(self):
        category = self.s.query(DBCategory).filter(self.href == DBCategory.href).all()
        if 0 == len(category):
            category = DBCategory(self.name, self.href)
            self.s.add(category)
            self.s.commit()
        else:
            category = category[0]
        return category

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
            self.items.append(NewsItem(self.domain, tr, self, self.s))

        for item in self.items:
            item()

    def __str__(self):
        return "Category {}({})".format(self.name, self.href)


class NewsItem:
    def __init__(self, domain: str, tr: Element, category: Category, session):
        self.domain = domain
        self.category = category
        a = tr.find(".//a")
        self.head = a.text.rstrip().lstrip()
        self.href = a.attrib['href']
        try:
            self.id = int(self.href.split("/")[-1].split("-")[0])
        except Exception:
            self.id = 100000 + (hash(self.href) % (POSTGRES_INTEGER_MAX_RANGE - 100000))
        el = check_find(tr.find_class('list-date'))
        self.date = None  # type: datetime.date
        if el is not None:
            date = el.text.rstrip().lstrip()
            try:
                self.date = datetime.strptime(date, "%d-%m-%y")
            except ValueError:
                pass
        self.content = None  # type: Element
        self.s = session
        self.need_update = True
        self.db_obj = self._work_db()

    def _work_db(self):
        news_item = self.s.query(DBNewsItem).filter(self.href == DBNewsItem.href).all()
        if 0 == len(news_item):
            news_item = DBNewsItem(
                self.id,
                self.head,
                self.href,
                self.date,
                ""
            )
            news_item.categories.append(self.category.db_obj)
            self.s.add(news_item)
            self.s.commit()
        else:
            news_item = news_item[0]

        if self.date is not None and news_item.date is not None:
            if datetime.date(self.date) <= datetime.date(news_item.date):
                self.need_update = False

        if not self.content:
            self.need_update = True

        return news_item

    def __call__(self):
        print("Get page {}".format(self.href))
        if not self.need_update:
            print("Not need")
            return

        page = html.parse(self.domain + self.href)
        print("Ok")
        content = check_find(page.getroot().find_class('item-page'))  # type: Element
        if content is None:
            return

        h2 = content.find(".//h2")
        dl = check_find(content.find_class("article-info"))  # type: Element
        if dl is not None:
            date_el = check_find(dl.find_class('modified'))
            date = date_el.text.rstrip().lstrip()
            print(date)
            # f.e. 28.07.2016 12:20
            try:
                self.date = datetime.strptime(date[10:], "%d.%m.%Y %H:%M")
                self.db_obj.date = self.date
            except ValueError:
                print("Error while recognize date")
                print_stack()
        nav = check_find(content.find_class('pagenav'))
        try:
            if h2 is not None:
                content.remove(h2)
            if dl is not None:
                content.remove(dl)
            if nav is not None:
                content.remove(nav)
        except Exception:
            print("WTF")
            print_stack()

        for tag in content.iter():  # type: Element
            if 'style' in tag.attrib:
                del tag.attrib['style']
            if 'src' in tag.attrib:
                tag.attrib['src'] = "http://fit.nsu.ru/" + tag.attrib['src']
            if 'href' in tag.attrib:
                tag.attrib['href'] = "http://fit.nsu.ru/" + tag.attrib['href']
            if 'border' in tag.attrib:
                del tag.attrib['border']
            if 'width' in tag.attrib:
                del tag.attrib['width']
            if 'height' in tag.attrib:
                del tag.attrib['height']

        self.content = content
        self.db_obj.content = str(self)
        self.s.commit()

    def __str__(self):
        if self.content is not None:
            return html.tostring(self.content, pretty_print=True, encoding='unicode')
        return "==Content Missing=="
