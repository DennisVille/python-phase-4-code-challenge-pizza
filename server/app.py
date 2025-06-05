#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response
from flask_restful import Api, Resource
from sqlalchemy.exc import IntegrityError
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)


@app.route("/")
def index():
    return "<h1>Code challenge</h1>"

@app.route('/restaurants')
def get_all_restaurants():
    restaurants = []
    for res in Restaurant.query.all():
        res_dict = res.to_dict(only = ('address', 'id', 'name',))
        restaurants.append(res_dict)
    
    return make_response(
        restaurants,
        200,
        {"Content-Type": "application/json"}
    )

@app.route('/restaurants/<int:id>', methods = ['GET', 'DELETE'])
def get_reataurant_by_id(id):
    restaurant = Restaurant.query.filter_by(id = id).first()
    if request.method == "GET":
        if restaurant:
            res_dict = restaurant.to_dict()
            return make_response(res_dict, 200, {'Content-Type': 'application/json'})
        else:
            res_body = {'error': 'Restaurant not found'}
            return make_response(res_body, 404)
        
    elif request.method == "DELETE":
        if restaurant:
            db.session.delete(restaurant)
            db.session.commit()

            res_body = {}
            return make_response(res_body, 204)
        else:
            res_body = {'error': 'Restaurant not found'}
            return make_response(res_body, 404)
        
@app.route('/pizzas', methods = ['GET'])
def get_pizzas():
    pizzas = Pizza.query.all()
    pizzas_dict = [pizza.to_dict(only = ('id', 'ingredients', 'name')) for pizza in pizzas]
    return make_response(pizzas_dict, 200)

@app.route('/restaurant_pizzas', methods=['POST'])
def create_restaurant_pizza():
    data = request.get_json()

    price = data.get('price')
    pizza_id = data.get('pizza_id')
    restaurant_id = data.get('restaurant_id')

    # Validate fields
    if price is None or not pizza_id or not restaurant_id:
        return make_response({"errors": ["validation errors"]}, 400)

    try:
        # Ensure pizza and restaurant exist
        pizza = Pizza.query.filter_by(id=pizza_id).first()
        restaurant = Restaurant.query.filter_by(id=restaurant_id).first()

        if not pizza or not restaurant:
            return make_response({"errors": ["validation errors"]}, 400)

        # Create new RestaurantPizza
        restaurant_pizza = RestaurantPizza(
            price=price,
            pizza_id=pizza_id,
            restaurant_id=restaurant_id
        )

        db.session.add(restaurant_pizza)
        db.session.commit()

        # Prepare full nested response
        response = {
            "id": restaurant_pizza.id,
            "price": restaurant_pizza.price,
            "pizza_id": pizza.id,
            "restaurant_id": restaurant.id,
            "pizza": {
                "id": pizza.id,
                "name": pizza.name,
                "ingredients": pizza.ingredients
            },
            "restaurant": {
                "id": restaurant.id,
                "name": restaurant.name,
                "address": restaurant.address
            }
        }

        return make_response(response, 201)

    except IntegrityError:
        db.session.rollback()
        return make_response({"errors": ["validation errors"]}, 400)

    except Exception:
        db.session.rollback()
        return make_response({"errors": ["validation errors"]}, 400)

if __name__ == "__main__":
    app.run(port=5555, debug=True)
