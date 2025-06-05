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



class Restaurants(Resource):
    #get all restaurants or one restaurant
    def get(self, id= None):
        if id == None:
            restuarants = [res.to_dict(rules = ('-restaurant_pizzas',)) for res in Restaurant.query.all()]
            return make_response(restuarants, 200)
        
        else:
            restaurant = Restaurant.query.filter_by(id = id).first()
            if restaurant:
                return make_response(restaurant.to_dict(), 200) 

            else:
                body = {'error': 'Restaurant not found'}
                return make_response(body, 404)
        
    #delete a restaurant
    def delete(self, id):
        restaurant = Restaurant.query.filter_by(id = id).first()

        if restaurant:
           db.session.delete(restaurant)
           db.session.commit()

           return make_response({}, 204) 

        else:
            body = {'error': 'Restaurant not found'}
            return make_response(body, 404)
        
api.add_resource(Restaurants, '/restaurants', '/restaurants/<int:id>')

class Pizzas(Resource):
    #get all pizzas
    def get(self):
        pizzas = [pizza.to_dict(rules = ('-restaurant_pizzas',)) for pizza in Pizza.query.all()]
        return make_response(pizzas, 200)
    
api.add_resource(Pizzas, '/pizzas')

class Restaurant_Pizzas(Resource):
    def post(self):
        data = request.get_json()

        #check if rastaurant and pizza exist
        res = Restaurant.query.filter_by(id = data['restaurant_id']).first()
        pizz = Pizza.query.filter_by(id = data['pizza_id']).first()

        if not res or not pizz or data['price'] is None :
            body = {'errors': ['valization errors']}
            return make_response(body, 404)
        
        #if 0 >= data['price'] > 30:
         #   body = {'errors': ['valization errors']}
          #  return make_response(body, 404)
        
        #create res_pizza
        try:
            new_obj = RestaurantPizza(price = data['price'], pizza_id = data['pizza_id'], restaurant_id = data['restaurant_id'])
            db.session.add(new_obj)
            db.session.commit()

            return_dict = new_obj.to_dict(rules=('-pizza.restaurant_pizzas', '-restaurant.restaurant_pizzas',))
            return make_response(return_dict, 201)
        
        except IntegrityError:
            db.session.rollback()
            return make_response({'errors': ['validation errors']}, 400)
        
        except Exception:
            db.session.rollback()
            return make_response({"errors": ["validation errors"]}, 400)
    
api.add_resource(Restaurant_Pizzas, '/restaurant_pizzas')

if __name__ == "__main__":
    app.run(port=5555, debug=True)
