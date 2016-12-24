from sqlalchemy import Column,  Integer, String
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

association_table = \
    Table('association', Base.metadata,
          Column('category_id', Integer, ForeignKey('category.id')),
          Column('newsitem_id', Integer, ForeignKey('newsitem.id'))
          )


class DBCategory(Base):
    __tablename__ = "category"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    href = Column(String, unique=True)
    news = relationship(
        "NewsItem",
        secondary=association_table,
        back_populates="categories"
    )

    def __init__(self, name, href):
        self.name = name
        self.href = href


class DBNewsItem(Base):
    __tablename__ = "newsitem"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    href = Column(String, unique=True)
    date = Column(DateTime)
    content = Column(String)
    categories = relationship(
        "Category",
        secondary=association_table,
        back_populates="news"
    )

    def __init__(self, _id: int, name: str, href: str, date, content: str):
        self.id = _id
        self.name = name
        self.href = href
        self.date = date
        self.content = content
