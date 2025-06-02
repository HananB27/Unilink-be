from neomodel import (
    StructuredNode, StringProperty, RelationshipTo, RelationshipFrom,
    UniqueIdProperty
)

class OfficialAccount(StructuredNode):
    uid = UniqueIdProperty()
    name = StringProperty(unique_index=True)
    email = StringProperty(unique_index=True)

    posted = RelationshipTo('Post', 'POSTED')
    associated_with = RelationshipTo('OfficialAccount', 'ASSOCIATED_WITH')

class Tag(StructuredNode):
    uid = UniqueIdProperty()
    name = StringProperty(unique_index=True)

class Company(OfficialAccount):
    pass

class University(OfficialAccount):
    pass

class Post(StructuredNode):
    uid = UniqueIdProperty()
    post_id = StringProperty(unique_index=True)
    title = StringProperty()
    type = StringProperty()
    content = StringProperty(default=None)

    tagged_with = RelationshipTo('Tag', 'TAGGED_WITH')
    posted_by = RelationshipFrom('User', 'POSTED')
    posted_by_dept = RelationshipFrom('Department', 'POSTED')

class Department(OfficialAccount):
    belongs_to = RelationshipTo('University', 'BELONGS_TO')
    posts = RelationshipTo('Post', 'POSTED')

class User(StructuredNode):
    uid = UniqueIdProperty()
    name = StringProperty()
    role = StringProperty(default='student')
    email = StringProperty(unique_index=True, required=False)

    affiliated_with = RelationshipTo('University', 'AFFILIATED_WITH')
    employed_at = RelationshipTo('Company', 'EMPLOYED_AT')
    interested_in = RelationshipTo('Tag', 'INTERESTED_IN')
    posted = RelationshipTo('Post', 'POSTED')
    connected_with = RelationshipTo('User', 'CONNECTED_WITH')
    works_in_department = RelationshipTo('Department', 'WORKS_IN_DEPARTMENT')
