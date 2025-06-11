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
from models import db, User, Character, Planet, Vehicle, Fav_character, Fav_planet, Fav_vehicle
# from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace(
        "postgres://", "postgresql://")
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


@app.route('/users', methods=['GET'])
def get_users():
    try:
        query_results = User.query.all()

        if not query_results:
            return jsonify({'msg': 'No users found'}), 400

        users = list(map(lambda item: item.serialize(), query_results))

        response_body = {
            'msg': 'ok',
            'results': users
        }

        return jsonify(response_body), 200

    except Exception as e:
        return jsonify({
            'msg': f'Internal server error',
            'error': {str(e)}
        }), 500

@app.route('/users/<int:id>/favorites', methods=['GET'])
def get_favorites(id):
    try:
        query_result = User.query.get(id)

        if not query_result:
            return jsonify({'msg': 'No user found'}), 404
        

        return jsonify(query_result.serialize_with_favorites()), 200

    except Exception as e:
        return jsonify({
            'msg': f'Internal server error',
            'error': {str(e)}
        }), 500

@app.route('/characters', methods=['GET'])
def get_characters():
    try:
        query_results = Character.query.all()

        if not query_results:
            return jsonify({'msg': 'No characters found'}), 400

        characters = list(map(lambda item: item.serialize(), query_results))
        response_body = {
            'msg': 'ok',
            'results': characters
        }
        return jsonify(response_body), 200

    except Exception as e:
        return ({
            'msg': f'Internal server error',
            'error': {str(e)}
        }), 500


@app.route('/characters/<int:character_id>', methods=['GET'])
def get_character_id(character_id):
    try:
        character = Character.query.get(character_id)

        if not character:
            return jsonify({
                'msg': 'Character not found'
            }), 400

        response_body = {
            'msg': 'ok',
            'result': character.serialize()
        }
        return jsonify(response_body)
    except Exception as e:
        return jsonify({
            'msg': f'Internal server error',
            'error': {str(e)}
        }), 500


@app.route('/planets', methods=['GET'])
def get_planets():
    try:
        query_results = Planet.query.all()

        if not query_results:
            return jsonify({'msg': 'No planets found'}), 400

        planets = list(map(lambda item: item.serialize(), query_results))
        response_body = {
            'msg': 'ok',
            'results': planets
        }
        return jsonify(response_body), 200

    except Exception as e:
        return ({
            'msg': f'Internal server error',
            'error': {str(e)}
        }), 500


@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_planet_id(planet_id):
    try:
        planet = Planet.query.get(planet_id)

        if not planet:
            return jsonify({
                'msg': 'Planet not found'
            }), 400

        response_body = {
            'msg': 'ok',
            'result': planet.serialize()
        }
        return jsonify(response_body), 200
    except Exception as e:
        return jsonify({
            'msg': f'Internal server error',
            'error': {str(e)}
        }), 500


@app.route('/user', methods=['POST'])
def create_user():
    data = request.get_json()
    if not data:
        return jsonify({'msg': 'No data was sent'}), 400
    email = data.get('email')
    password = data.get('password')
    is_active = data.get('is_active', False)

    created_user = User.query.filter_by(email=email).first()
    if created_user:
        return jsonify({'msg': 'Email is assigned to a created user already'}), 409

    new_user = User(
        email=email,
        password=password,
        is_active=is_active
    )
    db.session.add(new_user)

    try:
        db.session.commit()
        return jsonify(new_user.serialize()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'msg': f'Internal Server Error', 
            'error': {str(e)}
            }), 500
    
@app.route('/users/<int:user_id>/favorite/planet/<int:planet_id>', methods=['POST'])
def add_favorite_planet(user_id, planet_id):
    try:
        user = User.query.get(user_id)
        planet = Planet.query.get(planet_id)
        if not user or not planet:
            return jsonify({"msg": "user or planet not found"}), 404
        
        existing_favorite = Fav_planet.query.filter_by(user_id=user_id, planet_id=planet_id).first()
        if existing_favorite:
            return jsonify({
                "msg": "Favorite already added"
            }), 409
        
        new_fav_planet = Fav_planet(user_id=user_id, planet_id=planet_id)
        db.session.add(new_fav_planet)
        db.session.commit()

        return jsonify(new_fav_planet.serialize()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'msg': f'Internal Server Error', 
            'error': {str(e)}
            }), 500
    
@app.route('/users/<int:user_id>/favorite/character/<int:character_id>', methods=['POST'])
def add_favorite_character(user_id, character_id):
    try:
        user = User.query.get(user_id)
        character = Character.query.get(character_id)
        if not user or not character:
            return jsonify({"msg": "user or planet not found"}), 404
        
        existing_favorite = Fav_character.query.filter_by(user_id=user_id, character_id=character_id).first()
        if existing_favorite:
            return jsonify({
                "msg": "Favorite already added"
            }), 409
        
        new_fav_character = Fav_character(user_id=user_id, character_id=character_id)
        db.session.add(new_fav_character)
        db.session.commit()

        return jsonify(new_fav_character.serialize()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'msg': f'Internal Server Error', 'error': {str(e)}}), 500
    
@app.route('/users/<int:user_id>/favorite/planet/<int:planet_id>', methods=['DELETE'])
def remove_favorite_planet(user_id, planet_id):
    try:
        user = User.query.get(user_id)
        planet = Planet.query.get(planet_id)
        if not user or not planet:
            return jsonify({'msg': 'user or planet not found'}), 404
        
        favorite_planet = Fav_planet.query.filter_by(user_id=user_id, planet_id=planet_id).first()
        if not favorite_planet:
            return jsonify({'msg': 'Favorite planet not found'}), 404
        db.session.delete(favorite_planet)
        db.session.commit()
        return jsonify({'msg': 'Favorite planet removed succesfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'msg': f'Internal Server Error', 'error': {str(e)}}), 500
    
@app.route('/users/<int:user_id>/favorite/character/<int:character_id>', methods=['DELETE'])
def remove_favorite_character(user_id, character_id):
    try:
        user = User.query.get(user_id)
        character = Character.query.get(character_id)
        if not user or not character:
            return jsonify({'msg': 'user or character not found'}), 404
        
        favorite_character = Fav_character.query.filter_by(user_id=user_id, character_id=character_id).first()
        if not favorite_character:
            return jsonify({'msg': 'Favorite character not found'}), 404
        db.session.delete(favorite_character)
        db.session.commit()
        return jsonify({'msg': 'Favorite character removed succesfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'msg': f'Internal Server Error', 'error': {str(e)}}), 500


# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
