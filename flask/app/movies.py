from mongoengine import StringField, Document


class Movies(Document):
    title = StringField(required=True)
    year = StringField(max_length=4, required=True)
    description = StringField(max_length=2500)

    def json(self):
        movies_dict={
            "tilte":self.title,
            "year": self.year,
            "description": self.description
            
        }
        return json.dumps(movies_dict)
        
        
    meta = {'collection': 'Movies'}
