import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink, db
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)


# db_drop_and_create_all()

# ROUTES

@app.route("/drinks", methods=['GET'])
def get_drinks():
    try:
        all_drinks = Drink.query.all()
        drinks = [i.short() for i in all_drinks]

        return jsonify({
            "success": True,
            "drinks": drinks
        })
    except Exception as i:
        print(i)
        abort(404)


@app.route("/drinks-detail", methods=['GET'])
@requires_auth("get:drinks-detail")
def get_drinks_detail(jwt):
    try:
        all_drinks = Drink.query.all()
        drinks = []
        for drink in all_drinks:
            drinks.append(drink.long())

        return jsonify({
            "success": True,
            "drinks": drinks
        })
    except:
        abort(404)


@app.route("/drinks", methods=['POST'])
@requires_auth("post:drinks")
def post_drinks(jwt):
    title = request.json['title']
    recipe = request.json['recipe']

    if (not title or not recipe):
        abort(400)

    try:
        new_drink = Drink(title=title, recipe=json.dumps(recipe))
        new_drink.insert()

        return jsonify({
            "success": True,
            "drinks": [new_drink.long()]
        })
    except:
        db.session.rollback()
        abort(404)
    finally:
        db.session.close()


@app.route("/drinks/<int:id>", methods=["PATCH"])
@requires_auth("patch:drinks")
def patch_drinks(jwt, id):
    body = request.get_json()
    title = body.get('title', None)
    old_drink = Drink.query.get(id)

    if old_drink is None:
        abort(404)

    try:
        old_drink.title = title
        old_drink.update()
        return jsonify({
            "success": True,
            "drinks": [old_drink.long()]
        })
    except:
        abort(422)
    finally:
        db.session.close()


@app.route("/drinks/<int:id>", methods=["DELETE"])
@requires_auth("delete:drinks")
def delete_drink(jwt, id):
    try:
        print('test')
        drink = Drink.query.get(id)
        print(drink)
        drink.delete()
        return jsonify({
            "success": True,
            "delete": id
        })
    except:
        abort(404)
    finally:
        db.session.close()

# Error Handling


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
                    "success": False,
                    "error": 422,
                    "message": "unprocessable"
                    }), 422


@app.errorhandler(404)
def not_found(error):
    return jsonify({
                    "success": False,
                    "error": 404,
                    "message": "not found"
                    }), 404


@app.errorhandler(400)
def bad_request(error):
    return jsonify({
                    "success": False,
                    "error": 400,
                    "message": "bad request"
                    }), 400


@app.errorhandler(AuthError)
def authentication_error(error):
    return jsonify({
            'success': False,
            'error': 401,
            'message': 'unauthorized access'
    }), 401
