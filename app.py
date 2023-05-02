import json

from db import db, User, Vinyl
from flask import Flask
from flask import request
import os


db_filename = ""  # add
app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///%s" % db_filename
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True

db.init_app(app)
with app.app_context():
    db.create_all()


# generalized response formats
def success_response(data, code=200):
    """
    Generalized success response function
    """
    return json.dumps(data), code

def failure_response(message, code=404):
    """
    Generalized failure response function
    """
    return json.dumps({"error": message}), code

@app.route("/")
@app.route("/api/users/")
def get_users():
    """
    Endpoint for getting all users
    """
    users = []
    for user in User.query.all():
        users.append(user.serialize())
    return success_response({"users": users})

@app.route("/api/users/", methods={"POST"})
def create_user():
    """ 
    Endpoint for creating a new user
    """
    body = json.loads(request.data)
    if (body.get("username") == None):
        return failure_response("Invalid Input", 400)
    
    new_user = User(
        username = body.get("username"),
        bio = body.get("bio"),
        vinyls = []
        )
    db.session.add(new_user)
    db.session.commit()
    return success_response(new_user.serialize(), 201)

@app.route("/api/courses/<int:user_id>/", methods=["DELETE"])
def delete_user(user_id):
    """ 
    Endpoint for deleting a user by ID
    """
    user = User.query.filter_by(id = user_id).first() 
    if user is None:
        return failure_response("User Not Found")
    db.session.delete(user)
    db.session.commit()
    return success_response(user.serialize(), 200)