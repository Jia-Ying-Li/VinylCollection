from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Vinyl Collection Types
collection_association = db.Table(
    "collection_association",
    db.Column("vinyl_id", db.Integer, db.ForeignKey("vinyl.id")),
    db.Column("user_id", db.Integer, db.ForeignKey("user.id")),
)
wishlist_association = db.Table(
    "wishlist_association",
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

    vinyls = db.relationship("Vinyl", secondary = collection_association, back_populates = "collections")
    wishlist = db.relationship("Vinyl", secondary = wishlist_association, back_populates = "wishlist")

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
                collection.append(v.serialize())
        return collection


class Vinyl(db.Model):  # each vinyl associated with a user
    """
    Vinyl Model
    """
    __tablename__ = "vinyl"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    artist = db.Column(db.String, nullable=False)
    year = db.Column(db.String, nullable=True)
    user_id = db.Column(db.String, nullable=False)

    # either in collection or in wishlist
    type = db.Column(db.String, nullable=False)
    collections = db.relationship("User", secondary = collection_association, back_populates = "vinyls")
    wishlist = db.relationship("User", secondary = wishlist_association, back_populates = "wishlist")

    songs = db.relationship("Song", cascade="delete")

    def __init__(self, **kwargs):
        """
        Initialize a Vinyl object
        """
        self.name = kwargs.get("name", "")
        self.artist = kwargs.get("artist", "")
        self.year = kwargs.get("year", "")
        self.type = kwargs.get("type", "")
        self.user_id = kwargs.get("user_id")

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
            "collections": [c.simple_serialize() for c in self.collections],
            "wishlist": [w.simple_serialize() for w in self.wishlist]
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
