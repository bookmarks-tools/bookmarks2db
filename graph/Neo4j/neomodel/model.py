from neomodel import (config, StructuredNode, StringProperty,
                      Relationship, RelationshipFrom, DateTimeProperty,
                      ArrayProperty, RelationshipTo)

config.DATABASE_URL = 'bolt://neo4j:password@localhost:7687'


class Folder(StructuredNode):
    title = StringProperty(unique_index=True, required=True)
    add_date = DateTimeProperty(default_now=True)
    last_modified = DateTimeProperty(default_now=True)
    folder = RelationshipFrom('Folder', 'FOLDER')
    bookmark = RelationshipFrom('Bookmark', 'BOOKMARK')


class Bookmark(StructuredNode):
    title = StringProperty(unique_index=True)
    url = StringProperty(required=True)
    add_date = DateTimeProperty(default_now=True)
    icon = StringProperty()
    icon_uri = StringProperty()
    tags = ArrayProperty(StringProperty())
    bookmark = RelationshipTo(Folder, 'BOOKMARK')
