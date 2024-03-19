"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Planet, Character, Favorite_Planets, Favorite_People
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

# @app.route('/user', methods=['GET'])
# def handle_hello():
#     response_body = {
#         "msg": "Hello, this is your GET /user response "
#     }

#     return jsonify(response_body), 200

#<-----------------------------------------------USERS ROUTES------------------------------------------------------------>
@app.route('/users', methods=['GET'])
def get_user():
    #SELECT * FROM user
    users = User.query.all()  #trae toda la info del usuario en un arreglo
    users_serialized=[]
    
    #DOS FORMAS PARA SERIALIZAR Y DEVOLVER LOS ELEMTOS COMO OBJETOS
    #1 -> Es más corto el código 
    users_seriealized_map = list(map(lambda x: x.serialize(), users))
    #2 -> intera sobre cada uno de los elementos
    for user in users:
        users_serialized.append(user.serialize())

    # print("Sin serializar-->", user.serialize())
    # print("De la tabla-->", users)
    # print("Serializado-->", users_serialized)
    # print("Desde map-->", users_seriealized_map)
    
    response_body = {
       # "msg": "Hello, this is your GET /users response "
        "msg" : "Ok",
        "result" :  users_serialized,
    }

    return jsonify(response_body), 200

@app.route("/users", methods=["POST"])
def add_user():
    body = request.get_json(silent=True)
    if body is None:
        return jsonify("You must send information in the body."), 400
    if "name" not in body:
        return jsonify("The 'name' field is required."), 400
    new_user = User()
    new_user.name = body["name"]
    db.session.add(new_user)
    db.session.commit()
    return jsonify ("User added successfully.")

@app.route("/users/<int:user_id>", methods=["GET"])
def get_single_user(user_id):
    user = User.query.get(user_id)
    return jsonify({"msg" : "ok", "user":user.serialize()})

#<-----------------------------------------------PLANETS ROUTES------------------------------------------------------------>
@app.route("/planets", methods=["GET"])
def get_planets():
    planets = Planet.query.all()
    planets_serialized=[]
    for planet in planets:
        planets_serialized.append(planet.serialize())

    # print(planets)
    return jsonify ({"msg":"ok", "result": planets_serialized}), 200

@app.route("/planets", methods=["POST"])
def add_planet():
    body = request.get_json(silent=True)
    if body is None:
        return jsonify("You must send information in the body."), 400
    if "name" not in body:
        return jsonify("The 'name' field is required."), 400
    new_planet = Planet()
    new_planet.name = body["name"]
    db.session.add(new_planet)
    db.session.commit()
    return jsonify ("Planet added successfully")

@app.route("/planets/<int:id>", methods=["GET"])
def get_single_planet(id):
    planet = Planet.query.get(id)
    print(planet)
    return jsonify({"msg" : "ok", "planet":planet.serialize()})

#<-----------------------------------------------PEOPLE ROUTES------------------------------------------------------------>

@app.route("/people", methods=["GET"])
def get_people():
    people = Character.query.all()
    people_serialized=[]
    for character in people:
        people_serialized.append(character.serialize())
    return jsonify ({"msg":"ok", "result":people_serialized}), 200

@app.route("/people", methods=["POST"])
def add_character():
    body = request.get_json(silent=True)
    if body is None:
        return jsonify("You must send information in the body."), 400
    if "name" not in body:
        return jsonify("The 'name' field is required."), 400
    new_character = Character()
    new_character.name = body["name"]
    db.session.add(new_character)
    db.session.commit()
    return jsonify ("Character added successfully.")

@app.route("/people/<int:id>", methods=["GET"])
def get_single_people(id):
    character = Character.query.get(id)
    return jsonify({"msg" : "ok", "character":character.serialize()})

#<-----------------------------------------------FAVORITES ROUTES------------------------------------------------------------>
@app.route("/user/favorites", methods=["GET"])

def favorites_user():
    body = request.get_json(silent=True)
    if body is None:
        return jsonify({'msg': 'You must send information in the body'}), 400
    if 'user_id' not in body:
        return jsonify({'msg': 'The user_id field is required'}), 400
    user = User.query.get(body['user_id'])
    if user is None:
        return jsonify({'msg': "The user with ID: {} doesn't exist".format(body['user_id'])}), 404
    
    favorite_planets = db.session.query(Favorite_Planets, Planet).join(Planet).filter(Favorite_Planets.user_id == body['user_id']).all()
    favorite_people = db.session.query(Favorite_People, Character).join(Character).filter(Favorite_People.user_id == body['user_id']).all()
    favorite_planets_serialized = []
    favorite_people_serialized = []
    for favorite_item, planet_item in favorite_planets:
        favorite_planets_serialized.append({'favorite_planet_id': favorite_item.id, 'planet': planet_item.serialize()})
    for favorite_item, people_item in  favorite_people:
       favorite_people_serialized .append({'favorite_people_id': favorite_item.id, 'character': people_item.serialize()})
    return jsonify({'msg':'ok', 'results': {'favorite_planets': favorite_planets_serialized, 'favorite_people': favorite_people_serialized}})

@app.route("/favorite/planet/<int:planet_id>", methods=["POST"])
def add_favorite_planet(planet_id):
    body = request.get_json(silent=True)
    planet = Planet.query.get(planet_id)
    if body is None:
        return jsonify("You must send information in the body."), 400
    if planet is None:
        return jsonify("The planet not found."), 404

    new_favorite_planet = Favorite_Planets(planet_id=planet_id)
    db.session.add(new_favorite_planet)
    db.session.commit()

    return jsonify("Favorite planet added successfully.")

@app.route("/favorite/people/<int:people_id>", methods=["POST"])
def add_favorite_people(people_id):
    body = request.get_json(silent=True)
    if body is None:
        return jsonify("You must send information in the body."), 400
    
    character = Character.query.get(people_id)
    if character is None:
        return jsonify("The character not found."), 404

    favorite_people = Favorite_People(character_id=people_id)
    db.session.add(favorite_people)
    db.session.commit()
    return jsonify("Favorite character added successfully.")

@app.route("/favorite/planet/<int:planet_id>", methods=["DELETE"])
def delete_favorite_planet(planet_id):
    favorite = Favorite_Planets.query.filter_by(planet_id=planet_id).first()
    if favorite:
        db.session.delete(favorite)
        db.session.commit()
        return jsonify("Favorite planet removed successfully.")
    else:
        return jsonify("No favorite planet was found for the specified ID."), 404

@app.route("/favorite/people/<int:people_id>", methods=["DELETE"])
def delete_favorite_people(people_id):
    favorite_people = Favorite_People.query.filter_by(character_id=people_id).first()
    if favorite_people:
        db.session.delete(favorite_people)
        db.session.commit()
        return jsonify("Favorite character removed successfully.")
    else:
        return jsonify("No favorite character was found for the specified ID."), 404

