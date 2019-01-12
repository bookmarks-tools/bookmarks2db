from py2neo.ogm import GraphObject, Property, RelatedTo, RelatedFrom


class Folder(GraphObject):
    __primarykey__ = "title"

    title = Property()
    add_date = Property()
    last_modified = Property()

    folders = RelatedFrom("Folder", "FOLDER")
    bookmarks = RelatedFrom("Bookmark", "BOOKMARK")


class Bookmark(GraphObject):
    __primarykey__ = "title"

    title = Property()
    url = Property()
    add_date = Property()
    icon = Property()
    icon_uri = Property()
    tags = Property()

    bookmark = RelatedTo(Folder)
