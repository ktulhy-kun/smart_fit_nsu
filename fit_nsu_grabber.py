import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from grabber import Base
from grabber import NewsParser


# database prepare
SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URI']
engine = create_engine(SQLALCHEMY_DATABASE_URI, echo=True)
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

DOMAIN = "http://fit.nsu.ru"
NEWS = '/news'


news_p = NewsParser(DOMAIN, NEWS, session)
news_p()
print("Test")
