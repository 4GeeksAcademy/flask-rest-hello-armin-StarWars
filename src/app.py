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
from models import db, User, Planet, People, Favorite

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

# Endpoint para listar todos los personajes


@app.route('/people', methods=['GET'])
def get_all_people():
    people = People.query.all()
    serialized_people = [person.serialize() for person in people]

    return jsonify(serialized_people), 200

# Endpoint para mostrar un personaje específico


@app.route('/people/<int:people_id>', methods=['GET'])
def get_one_person(people_id):
    person = People.query.get(people_id)

    if person is None:
        return jsonify({"error": "Person not found"}), 404

    return jsonify(person.serialize()), 200

# Endpoint para listar todos los planetas


@app.route('/planets', methods=['GET'])
def get_all_planets():
    planets = Planet.query.all()
    serialized_planets = [planet.serialize() for planet in planets]

    return jsonify(serialized_planets), 200

# Endpoint para mostrar un planeta específico


@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_one_planet(planet_id):
    planet = Planet.query.get(planet_id)

    if planet is None:
        return jsonify({"error": "Planet not found"}), 404

    return jsonify(planet.serialize()), 200

# Endpoint para listar todos los usuarios


@app.route('/users', methods=['GET'])
def get_all_users():
    users = User.query.all()
    serialized_users = [user.serialize() for user in users]

    return jsonify(serialized_users), 200

# Endpoint para listar favoritos del usuario actual (simulado con user_id=1)


@app.route('/users/favorites', methods=['GET'])
def get_user_favorites():
    # En un sistema real, obtendríamos el usuario desde la autenticación
    # Para este ejemplo, usaremos el usuario con ID=1
    current_user_id = 1

    # Verificar que el usuario existe
    user = User.query.get(current_user_id)
    if user is None:
        return jsonify({"error": "User not found"}), 404

    # Obtener todos los favoritos del usuario
    favorites = Favorite.query.filter_by(user_id=current_user_id).all()

    result = []
    for favorite in favorites:
        if favorite.favorite_type == "planet":
            planet = Planet.query.get(favorite.favorite_id)
            if planet:
                item = planet.serialize()
                item["favorite_type"] = "planet"
                result.append(item)
        elif favorite.favorite_type == "people":
            person = People.query.get(favorite.favorite_id)
            if person:
                item = person.serialize()
                item["favorite_type"] = "people"
                result.append(item)

    return jsonify(result), 200

# Endpoint para añadir un planeta a favoritos


@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
def add_planet_favorite(planet_id):
    # En un sistema real, obtendríamos el usuario desde la autenticación
    current_user_id = 1

    # Verificar que el usuario existe
    user = User.query.get(current_user_id)
    if user is None:
        return jsonify({"error": "User not found"}), 404

    # Verificar que el planeta existe
    planet = Planet.query.get(planet_id)
    if planet is None:
        return jsonify({"error": "Planet not found"}), 404

    # Verificar si ya existe el favorito
    existing_favorite = Favorite.query.filter_by(
        user_id=current_user_id,
        favorite_id=planet_id,
        favorite_type="planet"
    ).first()

    if existing_favorite:
        return jsonify({"message": "Planet already in favorites"}), 200

    # Crear nuevo favorito
    new_favorite = Favorite(
        user_id=current_user_id,
        favorite_id=planet_id,
        favorite_type="planet"
    )

    db.session.add(new_favorite)
    try:
        db.session.commit()
        return jsonify({"message": "Planet added to favorites successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# Endpoint para añadir un personaje a favoritos


@app.route('/favorite/people/<int:people_id>', methods=['POST'])
def add_people_favorite(people_id):
    # En un sistema real, obtendríamos el usuario desde la autenticación
    current_user_id = 1

    # Verificar que el usuario existe
    user = User.query.get(current_user_id)
    if user is None:
        return jsonify({"error": "User not found"}), 404

    # Verificar que el personaje existe
    person = People.query.get(people_id)
    if person is None:
        return jsonify({"error": "Person not found"}), 404

    # Verificar si ya existe el favorito
    existing_favorite = Favorite.query.filter_by(
        user_id=current_user_id,
        favorite_id=people_id,
        favorite_type="people"
    ).first()

    if existing_favorite:
        return jsonify({"message": "Person already in favorites"}), 200

    # Crear nuevo favorito
    new_favorite = Favorite(
        user_id=current_user_id,
        favorite_id=people_id,
        favorite_type="people"
    )

    db.session.add(new_favorite)
    try:
        db.session.commit()
        return jsonify({"message": "Person added to favorites successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# Endpoint para eliminar un planeta de favoritos


@app.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])
def delete_planet_favorite(planet_id):
    # En un sistema real, obtendríamos el usuario desde la autenticación
    current_user_id = 1

    # Buscar el favorito
    favorite = Favorite.query.filter_by(
        user_id=current_user_id,
        favorite_id=planet_id,
        favorite_type="planet"
    ).first()

    if favorite is None:
        return jsonify({"error": "Favorite not found"}), 404

    # Eliminar el favorito
    db.session.delete(favorite)
    try:
        db.session.commit()
        return jsonify({"message": "Planet removed from favorites successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# Endpoint para eliminar un personaje de favoritos


@app.route('/favorite/people/<int:people_id>', methods=['DELETE'])
def delete_people_favorite(people_id):
    # En un sistema real, obtendríamos el usuario desde la autenticación
    current_user_id = 1

    # Buscar el favorito
    favorite = Favorite.query.filter_by(
        user_id=current_user_id,
        favorite_id=people_id,
        favorite_type="people"
    ).first()

    if favorite is None:
        return jsonify({"error": "Favorite not found"}), 404

    # Eliminar el favorito
    db.session.delete(favorite)
    try:
        db.session.commit()
        return jsonify({"message": "Person removed from favorites successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
