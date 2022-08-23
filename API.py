from .models import *
from .database import db
from flask_restful import Resource,Api
from werkzeug.exceptions import HTTPException

session_logged_in=''
class NormalValidationError(HTTPException):
  def __init__(self,status_code,error_message,error_code):
    message={'error_code':error_code,'error_message':error_message}
    self.response=make_response(json.dumps(message),status_code)

class ResourceCheck:
  def usercheck(user_id=None,username=None,form=None):
    global session_logged_in
    if username!=None:
      try:
        password=form['password']
      except:
        password=''
      try:
        user=User.query.filter_by(username=username).one()
        if user.password==password:
          session_logged_in=username
          return {"user_id":user.id}
        else:
          raise NormalValidationError(404,'User credentials error','USER001')
      except:
        raise NormalValidationError(404,'User does not exist','USER002')
    if user_id!=None:
      if session_logged_in!='':
        try:
          user=User.query.filter_by(username=session_logged_in).one()
          if user.id!=user_id or user.username!=session_logged_in:
            raise NormalValidationError(404,'User credentials error','USER001')
        except:
          raise NormalValidationError(404,'User does not exist','USER002')
      else:
        raise NormalValidationError(404,'User is not logged in a session','USER003')
  
  def deckcheck(deck_id):
    try:
      deck=Deck.query.filter_by(id=deck_id).one()
    except:
      raise NormalValidationError(404,'Deck does not exist','DECK001')
      
class UserAPI(Resource):
  def post(self,username):
    return ResourceCheck.usercheck(username=username,form=request.get_json())


class UserDeckAPI(Resource):

  def get(self,user_id,deck_id):
    ResourceCheck.usercheck(user_id=user_id)
    ResourceCheck.deckcheck(deck_id=deck_id)
    try:
      userdeck=UserDeck.query.filter_by(user_id=user_id,deck_id=deck_id).one()
      deck=Deck.query.filter_by(id=deck_id).one()
      d={}
      d['name']=deck.name
      d['description']=deck.description
      d['score']=userdeck.score
      d['last_reviewed']=userdeck.last_reviewed
      return json.dumps(d)
    except:
      raise NormalValidationError(404,'Deck does not belong to user','DECK002')


  def put(self,user_id,deck_id):
    form=request.get_json()
    ResourceCheck.deckcheck(deck_id=deck_id)
    ResourceCheck.usercheck(user_id=user_id)
    deck=Deck.query.filter_by(id=deck_id).one()
    try:
      deck_name=form['name']
    except:
      deck_name=deck.name
    try:
      deck_description=form['description']
    except:
      deck_description=deck.description
  
    try:
      userdeck=UserDeck.query.filter_by(deck_id=deck_id,user_id=user_id).one()
      deck.name=deck_name
      deck.description=deck_description
      db.session.commit()
      d={}
      return json.dumps({'name':deck.name,'description':deck.description})
    except:
      raise NormalValidationError(404,'Deck does not belong to user','DECK002')
      
  
  def delete(self,user_id,deck_id):
    ResourceCheck.deckcheck(deck_id=deck_id)
    ResourceCheck.usercheck(user_id=user_id)
    
    try:
      userdeck=UserDeck.query.filter_by(user_id=user_id,deck_id=deck_id).one()
    except:
      raise NormalValidationError(404,'Deck does not belong to user','DECK002')
    
    for card in Card.query.filter_by(DeckId=deck_id):
      db.session.execute(f'delete from usercard where card_id={card.id};')
    db.session.execute(f'DELETE FROM card where DeckId={deck_id};')
    db.session.execute(f'DELETE FROM userdeck where user_id={user_id} and deck_id={deck_id};')
    db.session.execute(f'DELETE FROM deck where id={deck_id};')
    db.session.commit()
    return {"status_code":"Successfully deleted"}

  def post(self,user_id):
    
    form=request.get_json()
    ResourceCheck.usercheck(user_id=user_id)
    try:
      name=form['name']
      description=form['description']
    except:
      raise NormalValidationError(404,'Wrong request body','REQUEST001')
    
    try:
      d=Deck.query.filter_by(name=name).one()
      return NormalValidationError(404,'Deck with given name already exists','DECK003')
    except:
      pass
    deck=Deck(name=name,description=description)
    db.session.add(deck)
    deck=Deck.query.filter_by(name=name).one()
    
    udeck=UserDeck(user_id=user_id,deck_id=deck.id,score=0,last_reviewed=dt.datetime.now())
    db.session.add(udeck)
    db.session.commit()
    deck=Deck.query.filter_by(name=name).one()
    return {"name":deck.name,"description":deck.description}


class UserDeckCardAPI(Resource):
  def get(self,user_id,deck_id,card_id):
    ResourceCheck.usercheck(user_id=user_id)
    ResourceCheck.deckcheck(deck_id=deck_id)
    try:
      card=Card.query.filter_by(id=card_id).one()
      if card.DeckId!=deck_id:
        raise NormalValidationError(404,'Card does not belong to deck','CAD002')
    except:
        raise NormalValidationError(404,'Card does not exist','CARD001')
    
    try:
      usercard=UserCard.query.filter_by(card_id=card_id,user_id=user_id).one()
    except:
      raise NormalValidationError(404,'Card and Deck does not belong to user','CARD003')
    d={}
    d['front']=card.front
    d['back']=card.back
    return json.dumps(d)
  
  def put(self,user_id,deck_id,card_id):
    ResourceCheck.usercheck(user_id=user_id)
    ResourceCheck.deckcheck(deck_id=deck_id)
    try:
      card=Card.query.filter_by(id=card_id).one()
      if card.DeckId!=deck_id:
        raise NormalValidationError(404,'Card does not belong to deck','CAD002')
    except:
        raise NormalValidationError(404,'Card does not exist','CARD001')
    
    try:
      usercard=UserCard.query.filter_by(card_id=card_id,user_id=user_id).one()
    except:
      raise NormalValidationError(404,'Card and Deck does not belong to user','CARD003')

    form=request.get_json()
    card.front=form['front']
    card.back=form['back']
    db.session.commit()
    card=Card.query.filter_by(id=card.id).one()
    return json.dumps({"front":card.front,"back":card.back})
  
  def delete(self,user_id,deck_id,card_id):
    ResourceCheck.usercheck(user_id=user_id)
    ResourceCheck.deckcheck(deck_id=deck_id)

    deck=Deck.query.filter_by(id=deck_id).one()
    try:
      card=Card.query.filter_by(id=card_id).one()
      if card.DeckId!=deck_id:
        raise NormalValidationError(404,'Card does not belong to deck','CAD002')
    except:
        raise NormalValidationError(404,'Card does not exist','CARD001')
    
    try:
      usercard=UserCard.query.filter_by(card_id=card_id,user_id=user_id).one()
    except:
      raise NormalValidationError(404,'Card and Deck does not belong to user','CARD003')

    db.session.execute(f'delete from usercard where user_id={user_id} and card_id={card_id};')
    db.session.execute(f'delete from card where id={card_id};')
    db.session.commit()
    return {"status_code":"successfully deleted"}


  def post(self,user_id,deck_id):
    ResourceCheck.usercheck(user_id=user_id)
    ResourceCheck.deckcheck(deck_id=deck_id)
    form=request.get_json()
    
    try:
      userdeck=UserDeck.query.filter_by(user_id=user_id,deck_id=deck_id).one()
    except:
      raise NormalValidationError(404,'Deck does not belong to user','DECK002')
    front=form['front']
    back=form['back']
    card=Card(front=front,back=back,DeckId=deck_id)
    db.session.add(card)
    card=Card.query.filter_by(front=front,back=back,DeckId=deck_id).one()
    ucard=UserCard(user_id=user_id,card_id=card.id,score=0,last_reviewed=dt.datetime.now())
    db.session.add(ucard)
    db.session.commit()
    return json.dumps({"front":card.front,"back":card.back})
