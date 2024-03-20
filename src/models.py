from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship

db = SQLAlchemy()

class User(db.Model):
    __tablename__ ="users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    is_active = db.Column(db.Boolean(), unique=False, nullable=False)
 

    def __repr__(self):
        #DOS MANERAS DE GUARDAR STRING
        #1
        #return '<User %r>' % self.email
        #2
        return f"User with id {self.id} and email: {self.email}"

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            "is_active":self.is_active,
            # do not serialize the password, its a security breach
        }     
    
class Planet(db.Model):
    __tablename__ = "planets"
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column (db.String(20), nullable = False) 
    population = db.Column(db.Integer, nullable = True) #Opcional el dejarlo en blanco

    def __repr__(self):
        return "Planet {} with name {}".format(self.id, self.name)
    
    def serialize(self):
        return {
            "id": self.id,
            "name" : self.name,
            "population" : self.population
        }
    
class Character(db.Model):
    __tablename__="people"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column (db.String(25), nullable=False)
    gender= db.Column (db.String(25), nullable=True)
    eye_color = db.Column (db.String(20), nullable=True)
     

    def __repr__(self):
        return "Person {} with name {}".format(self.id, self.name)
    
    def serialize(self):
        return {
            "id":self.id,
            "name":self.name,
            "gender": self.gender,
            "eye_color":self.eye_color,
        }
    

class Favorite_Planets (db.Model):
    __tablename__ = 'favorite_planets'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user_relationship = db.relationship(User)
    planet_id = db.Column(db.Integer, db.ForeignKey('planets.id'), nullable=False)
    planet_relationship = db.relationship(Planet)


    def __repr__(self):
        return f"Favorite {self.id} with user_id {self.user_id} planet_id {self.planet_id}"

    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "planet_id": self.planet_id,
        }


class Favorite_People(db.Model):
    __tablename__ = "favorite_people"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user_relationship = db.relationship(User)
    character_id = db.Column(db.Integer, db.ForeignKey('people.id'), nullable=False)
    character_relationship = db.relationship(Character)

    def __repr__ (self):
        return "Al usuario {} le gusta el personaje {}".format(self.user_id, self.character_id)

    def serialize(self):
        return {
            "id":self.id,
            "user_id":self.user_id,
            "character_id": self.character_id
        }

