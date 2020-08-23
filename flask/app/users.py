from mongoengine import StringField, ListField, Document, ReferenceField
from screenings import Screenings

class Users(Document):
    email = StringField(required=True, unique=True)
    name = StringField(max_length=50)
    password = StringField(max_length=50)
    category = StringField(max_length=10)
    moviesSeen = ListField(ReferenceField(Screenings))
    mSeenTitles = ListField(StringField())
    
    def json(self):
        user_dict = {
            "email": self.email,
            "name": self.name,
            "password": self.password,
            "category": self.category,
            "moviesSeen":self.moviesSeen,
            "mSeenTitles":self.mSeenTitles
        }
        return json.dumps(user_dict)
    
    meta = {'collection': 'Users'}

