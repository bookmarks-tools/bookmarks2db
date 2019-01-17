from sqlalchemy import Column, Integer, create_engine, orm, String, DateTime, func, ARRAY, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy_mptt import mptt_sessionmaker

from sqlalchemy_mptt.mixins import BaseNestedSets

engine = create_engine('postgresql://postgres:password@localhost/db')
connection = engine.connect()
Base = declarative_base()


class Folder(Base, BaseNestedSets):
    __tablename__ = "folder_mptt"

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    add_date = Column(DateTime, default=func.now())
    last_modified = Column(DateTime, default=func.now())
    bookmarks = relationship("Bookmark", cascade="all")


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


if __name__ == '__main__':
    Session = mptt_sessionmaker(sessionmaker(bind=engine))
    session = Session()

    orm.configure_mappers()
    session.query(Bookmark).delete()
    session.query(Folder).delete()
    session.commit()

    # Folder.__table__.drop()
    Base.metadata.create_all(connection)
    #
    # node = Folder(title='First level')
    # session.add(node)
    # session.commit()

