import sqlalchemy as sa
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy_utils import LtreeType, URLType

engine = create_engine('postgresql://postgres:18091997@localhost/olimp')
connection = engine.connect()
Base = declarative_base()


class Folder(Base):
    __tablename__ = 'folder'
    id = sa.Column(sa.Integer, autoincrement=True, primary_key=True)
    title = sa.Column(sa.String, nullable=False)
    add_date = sa.Column(sa.DateTime, default=sa.func.now())
    last_modified = sa.Column(sa.DateTime, default=sa.func.now())
    path = sa.Column(LtreeType)
    bookmarks = relationship("Bookmark", backref="folder")


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


if __name__ == '__main__':
    sa.orm.configure_mappers()
    Base.metadata.create_all(connection)

    Session = sessionmaker(bind=engine)
    session = Session()
    session.query(Bookmark).delete()
    session.query(Folder).delete()
    session.commit()

    Base.metadata.create_all(connection)
