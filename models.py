from .database import db
import datetime as dt

class Deck(db.Model):
  __tablename__='deck'
  id=db.Column(db.Integer,primary_key=True,autoincrement=True)
  name=db.Column(db.Integer,nullable=False)
  description=db.Column(db.String)


class Card(db.Model):
  __tablename__='card'
  id=db.Column(db.Integer,primary_key=True,autoincrement=True)
  front=db.Column(db.String,nullable=False)
  back=db.Column(db.String,nullable=False)
  DeckId=db.Column(db.Integer,db.ForeignKey('deck.id'),nullable=False)
  

class User(db.Model):
  __tablename__='user'
  id=db.Column(db.Integer,primary_key=True,autoincrement=True)
  email=db.Column(db.String,unique=True,nullable=False)
  username=db.Column(db.String,unique=True,nullable=False)
  password=db.Column(db.String)
  last_reviewed=db.Column(db.String)

class UserCard(db.Model):
  __tablename__='usercard'
  user_id=db.Column(db.Integer,db.ForeignKey('user.id'),primary_key=True,nullable=False)
  card_id=db.Column(db.Integer,db.ForeignKey('card.id'),primary_key=True,nullable=False)
  score=db.Column(db.Float,nullable=False)
  difficulty=db.Column(db.Integer)
  last_reviewed=db.Column(db.String)

class UserDeck(db.Model):
  __tablename__='userdeck'
  user_id=db.Column(db.Integer,db.ForeignKey('user.id'),primary_key=True,nullable=False)
  deck_id=db.Column(db.Integer,db.ForeignKey('deck.id'),primary_key=True,nullable=False)
  score=db.Column(db.Float,nullable=False)
  last_reviewed=db.Column(db.String)
