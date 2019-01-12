import bookmarks_parser

from graph.Neo4j.neomodel.model import Folder, Bookmark
from datetime import datetime


def save2db(child, prev=None, obj=None):
    for bookmark in child:
        title = bookmark['title']
        add_date = None
        if bookmark.get('add_date'):
            add_date = datetime.fromtimestamp(int(bookmark['add_date']))
        if bookmark.get('children'):
            last_modified = None
            if bookmark.get('last_modified'):
                last_modified = datetime.fromtimestamp(int(bookmark['add_date']))
            folder = Folder(title=title, add_date=add_date, last_modified=last_modified).save()
            if prev:
                obj.folder.connect(folder)
            if bookmark['children']:
                save2db(bookmark['children'], bookmark, folder)
        elif bookmark['type'] == 'bookmark':
            tags = bookmark.get('tags')
            icon_uri = bookmark.get('icon_uri')
            book = Bookmark(title=title, url=bookmark['url'],
                            add_date=add_date, icon=bookmark['icon'],
                            icon_uri=icon_uri, tags=tags).save()
            book.bookmark.connect(obj)


if __name__ == '__main__':
    bookmarks = bookmarks_parser.parse("/home/andriy/PycharmProjects/bookmarks2db/chrome_bookmarks.html")
    save2db(bookmarks)

    bookmarks_toolbar = Folder.nodes.get(title='First level bookmark bar folder')
    for bookmark in bookmarks_toolbar.bookmark.all():
        print(bookmark.title)
    for folder in bookmarks_toolbar.folder:
        print(folder.title)  # returns nothing???

    # for i in Bookmark.nodes:
    #     i.delete()
    # for i in Folder.nodes:
    #     i.delete()
