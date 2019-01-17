from datetime import datetime
import os

import bookmarks_parser
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy_mptt import mptt_sessionmaker

from SQL.sqlalchemy.mptt.model import Folder, Bookmark

engine = create_engine(os.environ.get('PG_DATABASE_URL'))
Session = mptt_sessionmaker(sessionmaker(bind=engine))
session = Session()


def save2db(child, prev_db_folder=None):
    for bookmark in child:
        title = bookmark['title']
        add_date = None
        if bookmark.get('add_date'):
            add_date = datetime.fromtimestamp(int(bookmark['add_date']))
        if bookmark.get('children'):
            last_modified = None
            if bookmark.get('last_modified'):
                last_modified = datetime.fromtimestamp(int(bookmark['add_date']))
            if prev_db_folder:
                folder = Folder(title=title, add_date=add_date, last_modified=last_modified, parent_id=prev_db_folder.id)
            else:
                folder = Folder(title=title, add_date=add_date, last_modified=last_modified)
            session.add(folder)
            session.commit()
            if bookmark['children']:
                save2db(bookmark['children'], folder)
        elif bookmark['type'] == 'bookmark':
            tags = bookmark.get('tags')
            icon_uri = bookmark.get('icon_uri')
            book = Bookmark(title=title, url=bookmark['url'],
                            add_date=add_date, icon=bookmark['icon'],
                            icon_uri=icon_uri, tags=tags)
            prev_db_folder.bookmarks.append(book)
            session.add(book)
            session.commit()


if __name__ == '__main__':
    bookmarks = bookmarks_parser.parse("/home/andriy/PycharmProjects/bookmarks2db/chrome_bookmarks.html")
    save2db(bookmarks)

    # move folder with all nested bookmarks and folders to other folder and set position
    def move_folder(folder, dest_folder):
        f = session.query(Folder).filter(Folder.title == folder).one()
        dest = session.query(Folder).filter(Folder.title == dest_folder).one()
        f.move_after(dest.id)
        session.commit()
    move_folder('folder on other', 'First level bookmark bar folder')

    # move bookmark between folder and position
    def move_bookmark_before(bookmark_title, folder_title, before_bookmark_title):
        bookmark = session.query(Bookmark).filter(Bookmark.title == bookmark_title).one()
        folder = session.query(Folder).filter(Folder.title == folder_title).one()
        after_bookmark = session.query(Bookmark).filter(Bookmark.title == before_bookmark_title).one()
        folder.bookmarks.insert(after_bookmark.position, bookmark)
        session.commit()

    move_bookmark_before('reddit: the front page of the internet', 'Second level bookmark bar folder', 'Google Перекладач')

    # remove folder with all nested bookmarks and folders
    node = session.query(Folder).filter(Folder.title == 'First level bookmark bar folder').one()
    session.delete(node)
    session.commit()
