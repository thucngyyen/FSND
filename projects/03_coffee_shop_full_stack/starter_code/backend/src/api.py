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

'''
@TODO uncomment the following line to initialize the database
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
# db_drop_and_create_all()

## ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route("/drinks", methods = ['GET'])
def get_drinks():
    try:
        all_drinks = Drink.query.all() 
        drinks = []
        for drink in all_drinks:
            drinks.append( drink.short() )
        return jsonify({
            "success": True,
            "drinks": drinks
        })
    except:
        abort(404)

'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route("/drinks-detail", methods=['GET'])
@requires_auth("get:drinks-detail")
def get_drinks_detail(jwt):
    try:
        all_drinks = Drink.query.all() 
        drinks = []
        for drink in all_drinks:
            drinks.append( drink.long() )

        return jsonify({
            "success": True,
            "drinks": drinks
        })
    except:
        abort(404)

'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route("/drinks", methods=['POST'])
@requires_auth("post:drinks")
def post_drinks(jwt):
    body = request.get_json()
    title = body.get('title', None)
    recipe = body.get('recipe', None)

    if (title is None or recipe is None): abort(400)

    try:
        new_drink = Drink( title=title, recipe=json.dumps(recipe) )
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


'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route("/drinks/<int:id>", methods=["PATCH"])
@requires_auth("patch:drinks")
def patch_drinks(jwt, id):
    body = request.get_json()
    title = body.get('title', None)
    #recipe = body.get('recipe', None)

    #Get drink object with corresponding id
    old_drink = Drink.query.get(id)

    if old_drink is None:
        abort(404)

    try:
        old_drink.title = title
        #old_drink.recipe = recipe 
        old_drink.update()
        return jsonify({
            "success": True,
            "drinks": [old_drink.long()]
        })
    except:
        abort(422)
    finally:
        db.session.close()

'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
app.route("/drinks/<int:id>", methods=["DELETE"])
@requires_auth("delete:drinks")
def delete_drink(jwt, id):
    try:
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

## Error Handling
'''
Example error handling for unprocessable entity
'''
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
                    "success": False, 
                    "error": 422,
                    "message": "unprocessable"
                    }), 422

'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False, 
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''
@app.errorhandler(404)
def not_found(error):
    return jsonify({
                    "success": False, 
                    "error": 404,
                    "message": "not found"
                    }), 404

'''
@TODO implement error handler for 404
    error handler should conform to general task above 
'''
@app.errorhandler(400)
def bad_request(error):
    return jsonify({
                    "success": False, 
                    "error": 400,
                    "message": "bad request"
                    }), 400


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above 
'''
# @app.errorhandler(AuthError)
# def unprocessable(error):
#     return jsonify({
#             'success': False,
#             'error': 401,
#             'message': 'unauthorized access'
#     }), 401
