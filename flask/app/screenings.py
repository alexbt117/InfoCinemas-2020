from mongoengine import StringField, Document, ReferenceField, IntField
from movies import Movies

class Screenings(Document):
    movieId = ReferenceField(Movies)
    scrTime = StringField()
    available = IntField(max_value=50, min_value=0)
    movieTitle= StringField()

    def json(self):
        screenings_dict={
            "movieId":self.movieId,
            "scrTime":self.dateTime,
            "available":50,
            "movieTitle":self.movieTitle
        }
        return json.dumps(screenings_dict)
    
    meta = {'collection': 'Screenings'}