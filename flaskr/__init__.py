import os

from flask import Flask
from flask import render_template
from flask_sqlalchemy import SQLAlchemy
from jinja2 import Environment

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
db = SQLAlchemy(app)


jinja_env = Environment(extensions=['jinja2.ext.autoescape'])


association_table = \
    db.Table('association', db.Model.metadata,
             db.Column('category_id', db.Integer, db.ForeignKey('category.id')),
             db.Column('newsitem_id', db.Integer, db.ForeignKey('newsitem.id'))
             )


class DBCategory(db.Model):
    __tablename__ = "category"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    href = db.Column(db.String, unique=True)
    news = db.relationship(
        "DBNewsItem",
        secondary=association_table,
        back_populates="categories"
    )

    def __init__(self, name, href):
        self.name = name
        self.href = href


class DBNewsItem(db.Model):
    __tablename__ = "newsitem"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    href = db.Column(db.String, unique=True)
    date = db.Column(db.DateTime)
    content = db.Column(db.String)
    categories = db.relationship(
        "DBCategory",
        secondary=association_table,
        back_populates="news"
    )

    def __init__(self, _id: int, name: str, href: str, date, content: str):
        self.id = _id
        self.name = name
        self.href = href
        self.date = date
        self.content = content


@app.route('/')
def index():
    news = db.session.query(DBNewsItem).filter(DBNewsItem.date.isnot(None)).order_by(DBNewsItem.date.desc()).limit(20).all()
    categories = db.session.query(DBCategory).all()
    print(categories)
    return render_template('index.html',
                           news_list=news,
                           categories=categories)


@app.route('/tag/<int:_id>')
def tag(_id):
    category = db.session.query(DBCategory).get(_id)  # type: DBCategory

    news = category.news  # type: list<DBNewsItem>

    return render_template(
        'index.html',
        news_list=sorted(news, key=lambda n: n.date)[20:]
    )
