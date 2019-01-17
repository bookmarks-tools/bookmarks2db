from datetime import datetime

import bookmarks_parser
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy_mptt import mptt_sessionmaker

from SQL.sqlalchemy.mptt.model import Folder, Bookmark

engine = create_engine('postgresql://postgres:password@localhost/olimp')
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

    # move folder with all nested bookmarks and folders
    def move(folder, dest_folder):
        f = session.query(Folder).filter(Folder.title == folder).one()
        print(f.id)
        dest = session.query(Folder).filter(Folder.title == dest_folder).one()
        print(dest.id)
        f.move_inside(dest.id)
        session.commit()
    move('First level bookmark bar folder', 'folder on other')

    # remove folder with all nested bookmarks and folders
    node = session.query(Folder).filter(Folder.title == 'First level bookmark bar folder').one()
    session.delete(node)
    session.commit()
