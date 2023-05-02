from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    """
    User Model
    """
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String, nullable=False)
    bio = db.Column(db.String, nullable=True)
    vinyls = db.relationship("Vinyl", cascade="delete")
    # wishlist

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
            "vinyls": [s.seriealize() for s in self.vinyls],
        }


class Vinyl(db.Model):  # each vinyl associated with a user
    """
    Vinyl Model
    """
    __tablename__ = "vinyl"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    artist = db.Column(db.String, nullable=False)
    songs = db.relationship("Song", cascade="delete")
    # images
    user_id = db.Column(db.Integer, db.ForeignKey(
        "user.id"), nullable=False)

    def __init__(self, **kwargs):
        """
        Initialize a Vinyl object
        """
        self.name = kwargs.get("name", "")
        self.artist = kwargs.get("artist", "")
        self.user_id = kwargs.get("user_id")

    def serialize(self):
        """
        Serializes a Vinyl object
        """
        return {
            "id": self.id,
            "name": self.name,
            "artist": self.artist,
            "songs": [s.seriealize() for s in self.songs],
            "user_id": self.user_id
        }


class Song(db.Model):
    """
    Song Model
    """
    __tablename__ = "song"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    vinyl_id = db.Column(db.Integer, db.ForeignKey(
        "vinyl.id"), nullable=False)

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
