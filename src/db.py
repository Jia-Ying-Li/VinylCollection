from flask_sqlalchemy import SQLAlchemy

# imports for images
import base64
import boto3
import datetime
import io
from io import BytesIO
from mimetypes import guess_extension, guess_type
import os
from PIL import Image
import random
import re
import string

db = SQLAlchemy()

EXTENSIONS = ["png", "gif", "jpg", "jpeg"]
BASE_DIR = os.getcwd()
S3_BUCKET_NAME = os.environ.get("S3_BUCKET_NAME")
# formatted string literal, using for building link
S3_BASE_URL = f"https://{S3_BUCKET_NAME}.s3.us-east-1.amazonaws.com"

# Vinyl Collection Types
# collection_association = db.Table(
#     "collection_association",
#     db.Column("vinyl_id", db.Integer, db.ForeignKey("vinyl.id")),
#     db.Column("user_id", db.Integer, db.ForeignKey("user.id")),
# )
# wishlist_association = db.Table(
#     "wishlist_association",
#     db.Column("vinyl_id", db.Integer, db.ForeignKey("vinyl.id")),
#     db.Column("user_id", db.Integer, db.ForeignKey("user.id")),
# )
association_table = db.Table(
    "association",
    db.Column("vinyl_id", db.Integer, db.ForeignKey("vinyl.id")),
    db.Column("user_id", db.Integer, db.ForeignKey("user.id")),
)


class User(db.Model):
    """
    User Model
    """
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String, nullable=False)
    bio = db.Column(db.String, nullable=True)

    # vinyls = db.relationship(
    #     "Vinyl", secondary=collection_association, back_populates="collections")
    # wishlist = db.relationship(
    #     "Vinyl", secondary=wishlist_association, back_populates="wishlist")
    vinyls = db.relationship(
        "Vinyl", secondary=association_table, back_populates="users")

    # vinyls = db.relationship("Vinyl", cascade="delete")

    def __init__(self, **kwargs):
        """
        Initializes User object
        """
        self.username = kwargs.get("username", "")
        self.bio = kwargs.get("bio", "")

    def serialize(self):
        """
        Serializes a User object
        """
        return {
            "id": self.id,
            "username": self.username,
            "bio": self.bio,
            # "vinyls": [s.serialize() for s in self.vinyls]
            "vinyls": self.get_curr_collection(),
            "wishlist": self.get_wishlist()
        }

    def simple_serialize(self):
        """
        Simple Serializes a User object
        """
        return {
            "id": self.id,
            "username": self.username,
            "bio": self.bio,
            # "vinyls": [s.serialize() for s in self.vinyls]
        }

    def get_wishlist(self):
        """
        Gets list of vinyls with type "wishlist"
        """
        wishlist = []
        for v in self.vinyls:
            if v.type == "wishlist":
                wishlist.append(v.simple_serialize())
        return wishlist

    def get_curr_collection(self):
        """
        Gets list of vinyls with type "collection"
        """
        collection = []
        for v in self.vinyls:
            if v.type == "collection":
                collection.append(v.simple_serialize())
        return collection


class Vinyl(db.Model):
    """
    Vinyl Model
    """
    __tablename__ = "vinyl"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    artist = db.Column(db.String, nullable=False)
    year = db.Column(db.String, nullable=True)
    # user_id = db.Column(db.String, nullable=True)
    # should we get rid of user id??

    # either in collection or in wishlist
    type = db.Column(db.String, nullable=True)
    # collections = db.relationship(
    #     "User", secondary=collection_association, back_populates="vinyls")
    # wishlist = db.relationship(
    #     "User", secondary=wishlist_association, back_populates="wishlist")
    users = db.relationship(
        "User", secondary=association_table, back_populates="vinyls")

    songs = db.relationship("Song", cascade="delete")

    def __init__(self, **kwargs):
        """
        Initialize a Vinyl object
        """
        self.name = kwargs.get("name", "")
        self.artist = kwargs.get("artist", "")
        self.year = kwargs.get("year", "")
        self.type = kwargs.get("type", "")
        # self.user_id = kwargs.get("user_id", "")

    def serialize(self):
        """
        Serializes a Vinyl object
        """
        return {
            "id": self.id,
            "name": self.name,
            "artist": self.artist,
            "year": self.year,
            "songs": [s.simple_serialize() for s in self.songs],
            "users": [u.simple_serialize() for u in self.users]
            # "collections": [c.simple_serialize() for c in self.collections],
            # "wishlist": [w.simple_serialize() for w in self.wishlist]
        }

    def simple_serialize(self):
        """
        Simple Serializes a Vinyl object
        """
        return {
            "id": self.id,
            "name": self.name,
            "artist": self.artist,
            "year": self.year,
        }


class Song(db.Model):
    """
    Song Model
    """
    __tablename__ = "song"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    vinyl_id = db.Column(db.Integer, db.ForeignKey("vinyl.id"), nullable=False)

    def __init__(self, **kwargs):
        """
        Initialize a Song object
        """
        self.name = kwargs.get("name", "")
        self.vinyl_id = kwargs.get("vinyl_id")

    def serialize(self):
        """
        Serializes a Song object
        """
        return {
            "id": self.id,
            "name": self.name,
            "vinyl_id": self.vinyl_id
        }


class Asset(db.Model):
    """
    Asset Model
    """
    __tablename__ = "assets"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    base_url = db.Column(db.String, nullable=True)
    salt = db.Column(db.String, nullable=False)
    extension = db.Column(db.String, nullable=False)
    width = db.Column(db.Integer, nullable=False)
    height = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)

    def __init__(self, **kwargs):
        """
        Initializes asset object
        """
        self.create(kwargs.get("image_data"))

    def serialize(self):
        """
        Serializes an Asset Object
        """
        return {
            "url": f"{self.base_url}/{self.salt}.{self.extension}",
            "created_at": str(self.created_at)
        }

    def create(self, image_data):
        """
        Given img in base64 form:
        1. Rejects image if not supported file type
        2. Generates a random string for image filename
        3. Decodes the image and attempts to upload to AWS
        """
        try:
            ext = guess_extension(guess_type(image_data)[0])[1:]
            if ext not in EXTENSIONS:
                raise Exception(f"Extension {ext} not supported")
            salt = "".join(
                random.SystemRandom().choice(
                    string.ascii_uppercase + string.digits
                )
                for _ in range(16)
            )

            # decoding
            # remove base64 header
            img_str = re.sub("^data:image/.+;base64,", "", image_data)
            img_data = base64.b64decode(img_str)
            img = Image.open(BytesIO(img_data))

            self.base_url = S3_BASE_URL
            self.salt = salt
            self.extension = ext
            self.width = img.width
            self.height = img.height
            self.created_at = datetime.datetime.now()

            img_filename = f"{self.salt}.{self.extension}"
            self.upload(img, img_filename)
        except Exception as e:
            print(f"Error while creating image: {e}")

    def upload(self, img, img_filename):
        """
        Attempt to upload image into S3 buckets
        """
        try:
            # save img temporarily on server
            img_temploc = f"{BASE_DIR}/{img_filename}"
            img.save(img_temploc)

            # upload img to S3
            s3_client = boto3.client("s3")
            s3_client.upload_file(img_temploc, S3_BUCKET_NAME, img_filename)

            # make S3 url public
            s3_resource = boto3.resource("s3")
            object_acl = s3_resource.ObjectAcl(S3_BUCKET_NAME, img_filename)
            object_acl.put(ACL="public-read")

            # remove img from server
            os.remove(img_temploc)

        except Exception as e:
            print(f"Error uploading image: {e}")
