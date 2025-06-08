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
from models import db, User, Character
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

@app.route('/users', methods=['GET'])
def get_users():
    try:
        query_results = User.query.all()

        if not query_results:
            return jsonify({'msg': 'No users found'}), 400
        
        results = list(map(lambda item: item.serialize(), query_results))

        response_body = {
            'msg': 'ok',
            'results': results
        }

        return jsonify(response_body), 200
    
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
        
        results = list(map(lambda item: item.serialize(), query_results))
        response_body = {
            'msg': 'ok',
            'results': results
        }
        return jsonify(response_body), 200
    
    except Exception as e:
        return ({
            'msg': f'Internal server error',
            'error': {str(e)}
        }), 500
    
@app.route('/characters/<int:id>', methods=['GET'])
def get_character_id():
    try:
        query_results = Character.query.get(id)

        if not query_results:
            return jsonify({
                'msg': 'Character not found'
            }), 400
        
        results = list(map(lambda item: item.serialize(), query_results))
        response_body = {
            'msg': 'ok',
            'results': results
        }
        return jsonify(response_body)
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
        email = email,
        password = password,
        is_active = is_active
    )
    db.session.add(new_user)

    try:
        db.session.commit()
        return jsonify(new_user.serialize()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'msg': f'Internal Server Error', 'error': {str(e)}}), 500
        

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
