import json

from db import db, User, Vinyl, Song
from flask import Flask
from flask import request
from flask import jsonify
import os


db_filename = "collection.db"
app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_filename}"
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

# User #
# ==============================================================================#


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
        username=body.get("username"),
        bio=body.get("bio")
    )
    db.session.add(new_user)
    db.session.commit()
    return success_response(new_user.serialize(), 201)


@app.route("/api/users/<int:user_id>/", methods=["DELETE"])
def delete_user(user_id):
    """ 
    Endpoint for deleting a user by ID
    """
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return failure_response("User Not Found")
    db.session.delete(user)
    db.session.commit()
    return success_response(user.serialize(), 200)

# Vinyl #
# ==============================================================================#


# @app.route("/")
@app.route("/api/users/<int:user_id>/vinyls/")
def get_vinyls(user_id):
    """
    Endpoint for getting vinyls by user id
    """
    vinyls = None
    for user in User.query.all():
        if user.id == user_id:
            vinyls = user.vinyls

    if vinyls == None:
        return failure_response("User Not Found")
    return success_response(vinyls, 200)


@app.route("/api/users/<int:user_id>/vinyls/", methods=["POST"])
def post_vinyl(user_id):
    """ 
    Endpoint for creating a vinyl
    """
    user = User.query.filter_by(id=user_id).first()

    if user is None:
        return failure_response("User Not Found")

    body = json.loads(request.data)
    name = body.get("name")
    artist = body.get("artist")
    year = body.get("year")
    type = body.get("type")
    if name is None or artist is None or type is None:
        return failure_response("Invalid Input", 400)
    if type != "wishlist" and type != "collection":
        return failure_response("Not a valid type", 400)

    new = Vinyl(
        name=name,
        artist=artist,
        year=year,
        type=type,
        user_id=user_id
    )

    db.session.add(new)
    user.vinyls.append(new)
    db.session.commit()

    return success_response(new.serialize(), 201)


# commenting out for now because won't really work with one to many
# @app.route("/api/vinyls/many/", methods=["POST"])
# def post_many_vinyls():
#     body = json.loads(request.data)
#     for vinyl in body:
#         name = body.get("name")
#         artist = body.get("artist")
#         year = body.get("year")
#         if name is None or artist is None:
#             return failure_response("Invalid Input", 400)
#         new = Vinyl(
#             name=name,
#             artist=artist,
#             year=year,
#         )
#         db.session.add(new)
#         db.session.commit()

#     return success_response("all added", 201) #should I actually dump all of them


@app.route("/api/users/<int:user_id>/vinyls/", methods=["DELETE"])
def delete_vinyl(user_id, vinyl_id):
    """ 
    Endpoint for deleting a vinyl by ID
    """
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return failure_response("User Not Found")

    vinyl = Vinyl.query.filter_by(id=vinyl_id).first()
    if vinyl is None:
        return failure_response("Vinyl Not Found")

    db.session.delete(vinyl)
    db.session.commit()
    return success_response(user.serialize(), 200)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
