from datetime import datetime

import bookmarks_parser
from py2neo import Graph

from graph.Neo4j.py2neo.model import Folder, Bookmark

graph = Graph(password="password")


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

            folder = Folder()
            folder.title = title
            folder.add_date = add_date
            folder.last_modified = last_modified
            if prev:
                obj.folders.add(folder)
                graph.push(obj)
            graph.push(folder)
            if bookmark['children']:
                save2db(bookmark['children'], bookmark, folder)
        elif bookmark['type'] == 'bookmark':
            tags = bookmark.get('tags')
            icon_uri = bookmark.get('icon_uri')

            book = Bookmark()
            book.title = title
            book.url = bookmark['url']
            book.add_date = add_date
            book.icon = bookmark['icon']
            book.icon_uri = icon_uri
            book.tags = tags
            book.bookmark.add(obj)
            graph.push(book)


if __name__ == '__main__':
    graph.delete_all()
    bookmarks = bookmarks_parser.parse("/home/andriy/PycharmProjects/bookmarks2db/chrome_bookmarks.html")
    save2db(bookmarks)

    # bookmark remove
    bookmark = Bookmark.match(graph).where("_.url = 'https://github.com/'").first()
    graph.delete(bookmark)

    # remove folder with all nested bookmarks and folders
    def delete_folder(folder):
        for bookmark in folder.bookmarks:
            print('delete {} bookmark from {} folder'.format(bookmark.title, folder.title))
            graph.delete(bookmark)
        for f in folder.folders:
            if f.folders or f.bookmarks:
                delete_folder(f)
        graph.delete(folder)
    bookmarks_bar = Folder.match(graph, "Bookmarks bar").first()
    delete_folder(bookmarks_bar)

    # move folder with all nested bookmarks and folders
    def move_folder(from_folder, folder, dst):
        from_folder.folders.remove(folder)
        graph.push(from_folder)
        dst.folders.add(folder)
        graph.push(dst)

    bookmarks_bar = Folder.match(graph, "Bookmarks bar").first()
    first_level_folder = Folder.match(graph, "First level bookmark bar folder").first()
    folder_on_other = Folder.match(graph, "folder on other").first()
    move_folder(bookmarks_bar, first_level_folder, folder_on_other)
