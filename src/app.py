import json

from db import db, User, Vinyl, Song, Asset
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


@app.route("/api/vinyls/")
def get_all_vinyls():
    """
    Endpoint to get all vinyls
    """
    vinyls = []
    for vinyl in Vinyl.query.all():
        vinyls.append(vinyl.serialize())
    return success_response({"vinyls": vinyls})



@app.route("/api/vinyls/", methods=["POST"])
def post_vinyl():
    """ 
    Endpoint for creating a single vinyl 
    """

    body = json.loads(request.data)
    name = body.get("name")
    artist = body.get("artist")
    year = body.get("year")
    type = body.get("type")

    if name is None or artist is None or type is None:
        return failure_response("Invalid Input", 400)
    if type != "wishlist" and type != "collection":
        return failure_response("Not A Valid Type", 400)

    new = Vinyl(
        name=name,
        artist=artist,
        year=year,
        type=type,
    )

    db.session.add(new)
    db.session.commit()

    return success_response(new.serialize(), 201)


@app.route("/api/vinyls/many/", methods=["POST"])
def post_many_vinyls():
    """
    Endpoint for adding database of vinyls
    """
    body = json.loads(request.data)
    for vinyl in body:
        name = body[vinyl]["name"]
        artist = body[vinyl]["artist"]
        year = body[vinyl]["year"]
        img = body[vinyl]["image"]
        if name is None or artist is None:
            return failure_response("Invalid Input", 400)
        new = Vinyl(
            name=name,
            artist=artist,
            year=year,
            img =img
        )
        db.session.add(new)
        db.session.commit()

    
    return success_response("all added", 201)


@app.route("/api/users/<int:user_id>/vinyls/add/", methods=["POST"])
def assign_vinyl_to_user(user_id):
    """
    Assigns an already existing vinyl to a users waitlist or collection
    Request takes in vinyl id and type
    """
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return failure_response("User not found")
    body = json.loads(request.data)
    vinyl_id = body.get("vinyl_id")
    type = body.get("type")
    if vinyl_id is None or type is None:
        return failure_response("Don't supply all fields", 400)
    if type != "wishlist" and type != "collection":
        return failure_response("Not a valid type", 400)
    vinyl = Vinyl.query.filter_by(id=vinyl_id).first()
    if vinyl is None:
        return failure_response("Vinyl not found")

    vinyl.type = type
    db.session.commit()
    user.vinyls.append(vinyl)
    db.session.commit()
    return success_response(user.serialize())


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


@app.route("/upload/", methods=["POST"])
def upload():
    """
    Endpoint for uploading an image to AWS given its base64 form,
    then storing/returning the URL of that image
    """
    body = json.loads(request.data)
    image_data = body.get("image_data")
    if image_data is None:
        return failure_response("No Base64 URL")
    asset = Asset(image_data=image_data)
    db.session.add(asset)
    db.session.commit()
    serialized = asset.serialize()

    return success_response(serialized, 201)


@app.route("/upload/<vinyl_id>/", methods=["POST"])
def upload_vinyl_img(vinyl_id):
    """
    Endpoint for uploading an image to AWS given its base64 form,
    then storing/returning the URL of that image and adding as img field in vinyl table
    """
    body = json.loads(request.data)
    image_data = body.get("image_data")
    if image_data is None:
        return failure_response("No Base64 URL")
    asset = Asset(image_data=image_data)
    db.session.add(asset)
    db.session.commit()
    
    serialized = asset.serialize()
    url = serialized["url"]
    vinyl = Vinyl.query.filter_by(id=vinyl_id).first()

    vinyl.img = url
    db.session.commit()

    return success_response(serialized, 201)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
