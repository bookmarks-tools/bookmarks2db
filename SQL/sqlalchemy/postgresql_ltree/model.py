import os

import sqlalchemy as sa
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.orderinglist import ordering_list
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy_utils import LtreeType, URLType

engine = create_engine(os.environ.get('PG_DATABASE_URL'))
connection = engine.connect()
Base = declarative_base()


class Folder(Base):
    __tablename__ = 'folder'
    id = sa.Column(sa.Integer, autoincrement=True, primary_key=True)
    title = sa.Column(sa.String, nullable=False)
    add_date = sa.Column(sa.DateTime, default=sa.func.now())
    last_modified = sa.Column(sa.DateTime, default=sa.func.now())
    path = sa.Column(LtreeType)
    position = sa.Column(sa.Integer)
    parent_id = sa.Column(sa.Integer, sa.ForeignKey('folder.id'))
    folders = relationship("Folder", cascade="all", order_by="Folder.position",
                           collection_class=ordering_list('position'))
    bookmarks = relationship("Bookmark", cascade="all", order_by="Bookmark.position",
                             collection_class=ordering_list('position'))


class Bookmark(Base):
    __tablename__ = 'bookmark'
    id = sa.Column(sa.Integer, primary_key=True)
    title = sa.Column(sa.String)
    url = sa.Column(URLType, nullable=False)
    add_date = sa.Column(sa.DateTime, default=sa.func.now())
    icon = sa.Column(sa.String)
    icon_uri = sa.Column(URLType)
    tags = sa.Column(sa.ARRAY(sa.Integer))
    parent_id = sa.Column(sa.Integer, sa.ForeignKey('folder.id'))
    position = sa.Column(sa.Integer)


if __name__ == '__main__':
    sa.orm.configure_mappers()
    Base.metadata.create_all(connection)

    Session = sessionmaker(bind=engine)
    session = Session()
    session.query(Bookmark).delete()
    session.query(Folder).delete()
    session.commit()

    Base.metadata.create_all(connection)
