from neomodel import (
    StructuredNode, StringProperty, RelationshipTo, RelationshipFrom,
    UniqueIdProperty
)

class Tag(StructuredNode):
    uid = UniqueIdProperty()
    name = StringProperty(unique_index=True)

class Company(StructuredNode):
    uid = UniqueIdProperty()
    name = StringProperty(unique_index=True)

class University(StructuredNode):
    uid = UniqueIdProperty()
    name = StringProperty(unique_index=True)

class Post(StructuredNode):
    uid = UniqueIdProperty()
    title = StringProperty()
    type = StringProperty()
    content = StringProperty(default=None)

    tagged_with = RelationshipTo('Tag', 'TAGGED_WITH')
    posted_by = RelationshipFrom('User', 'POSTED')
    posted_by_dept = RelationshipFrom('Department', 'POSTED')

class Department(StructuredNode):
    uid = UniqueIdProperty()
    name = StringProperty(unique_index=True)

    belongs_to = RelationshipTo('University', 'BELONGS_TO')
    posts = RelationshipTo('Post', 'POSTED')

class User(StructuredNode):
    uid = UniqueIdProperty()
    name = StringProperty()
    role = StringProperty(default='student')
    email = StringProperty(unique_index=True, required=False)

    affiliated_with = RelationshipTo('University', 'AFFILIATED_WITH')
    employed_at = RelationshipTo('Company', 'EMPLOYED_AT')
    represents = RelationshipTo('Company', 'REPRESENTS')
    interested_in = RelationshipTo('Tag', 'INTERESTED_IN')
    posted = RelationshipTo('Post', 'POSTED')
    connected_with = RelationshipTo('User', 'CONNECTED_WITH')
