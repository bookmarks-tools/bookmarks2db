import os
from datetime import datetime

import bookmarks_parser
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import Ltree

from SQL.sqlalchemy.postgresql_ltree.model import Folder, Bookmark, Base
from slugify import slugify

engine = create_engine(os.environ.get('PG_DATABASE_URL'))
Base.metadata.bind = engine

Session = sessionmaker(bind=engine)
session = Session()


def save2db(child, prev_dict_folder=None, prev_db_folder=None):
    for bookmark in child:
        title = bookmark['title']
        add_date = None
        if bookmark.get('add_date'):
            add_date = datetime.fromtimestamp(int(bookmark['add_date']))
        if bookmark.get('children'):
            last_modified = None
            if bookmark.get('last_modified'):
                last_modified = datetime.fromtimestamp(int(bookmark['add_date']))
            if prev_dict_folder:
                bookmark['path'] = '{}.{}'.format(prev_dict_folder['path'], slugify(bookmark['title'], separator="_"))
            else:
                bookmark['path'] = slugify(bookmark['title'], separator="_")
            folder = Folder(title=title, add_date=add_date, last_modified=last_modified, path=Ltree(bookmark['path']))
            if prev_db_folder:
                prev_db_folder.folders.append(folder)

            session.add(folder)
            session.commit()
            if bookmark['children']:
                save2db(bookmark['children'], bookmark, folder)
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

    # move folder with all nested bookmarks and folders to other folder aster certain position
    folder_on_other = session.query(Folder).filter(Folder.title == 'folder on other').one()
    index = folder_on_other.path.index(folder_on_other.path[-1])
    move_to_first_level_folder = session.query(Folder).filter(Folder.title == 'First level bookmark bar folder').one()

    first_level_folders = session.query(Folder).filter(Folder.path.descendant_of(folder_on_other.path)).all()
    for folder in first_level_folders:
        path = folder.path[index:]
        folder.path = move_to_first_level_folder.path + path
        session.add(folder)

    first_level_parent = session.query(Folder).filter(Folder.id == move_to_first_level_folder.parent_id).one()
    first_level_parent.folders.insert(move_to_first_level_folder.position + 1, folder_on_other)
    session.commit()

    # move bookmark to other folder and certain position
    def move_bookmark_before(bookmark_title, folder_title, after_bookmark_title):
        bookmark = session.query(Bookmark).filter(Bookmark.title == bookmark_title).one()
        folder = session.query(Folder).filter(Folder.title == folder_title).one()
        after_bookmark = session.query(Bookmark).filter(Bookmark.title == after_bookmark_title).one()
        folder.bookmarks.insert(after_bookmark.position, bookmark)
        session.commit()

    move_bookmark_before('reddit: the front page of the internet', 'Second level bookmark bar folder', 'Google Перекладач')

    # remove folder with all nested bookmarks and folders
    first_level_folder = session.query(Folder).filter(Folder.title == 'First level bookmark bar folder').one()
    first_level_folders = session.query(Folder).filter(Folder.path.descendant_of(first_level_folder.path)).all()
    for folder in first_level_folders:
        session.delete(folder)
    session.commit()
