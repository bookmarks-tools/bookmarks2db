import os

from sqlalchemy import Column, Integer, create_engine, orm, String, DateTime, func, ARRAY, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.orderinglist import ordering_list
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy_mptt import mptt_sessionmaker

from sqlalchemy_mptt.mixins import BaseNestedSets

engine = create_engine(os.environ.get('PG_DATABASE_URL'))
connection = engine.connect()
Base = declarative_base()
Base.metadata.bind = engine


class Folder(Base, BaseNestedSets):
    __tablename__ = "folder_mptt"

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    add_date = Column(DateTime, default=func.now())
    last_modified = Column(DateTime, default=func.now())
    bookmarks = relationship("Bookmark", cascade="all", order_by="Bookmark.position",
                             collection_class=ordering_list('position'))


class Bookmark(Base):
    __tablename__ = 'bookmark_mptt'
    id = Column(Integer, primary_key=True)
    title = Column(String)
    url = Column(String, nullable=False)
    add_date = Column(DateTime, default=func.now())
    icon = Column(String)
    icon_uri = Column(String)
    tags = Column(ARRAY(Integer))
    parent_id = Column(Integer, ForeignKey('folder_mptt.id'))
    position = Column(Integer)


if __name__ == '__main__':
    Session = mptt_sessionmaker(sessionmaker(bind=engine))
    session = Session()

    orm.configure_mappers()

    # Base.metadata.create_all(connection)
    Bookmark.__table__.drop()
    Folder.__table__.drop()
    # Base.metadata.create_all(connection)

