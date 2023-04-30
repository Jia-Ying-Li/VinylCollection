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


class Vinyl(db.Model):
    """
    Vinyl Model
    """
