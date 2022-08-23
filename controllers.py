from flask import Flask,render_template,request,redirect,make_response #Normal application making
from application.models import *
from .database import db
from flask import current_app as app
logged_in=''


@app.route('/<uname>/dashboard',methods=['GET','POST'])
def Dashboard(uname):
  global logged_in
  if not logged_in:
    return redirect('/')

  try:
    query=Deck.query.all()
    userdeck={}
    user=User.query.filter_by(username=uname).one()
    deckids=[]
    for q in UserDeck.query.filter_by(user_id=user.id):
      userdeck[q.deck_id]=q
      deckids.append(q.deck_id)
    l=[]
    for deck in query:
      if deck.id in deckids:
        l.append(deck)
    query=l
    return render_template('Dashboard.html',user=user,decks=query,n=len(query),userdeck=userdeck)
  except Exception as e:
    print(e)
    return render_template('Error.html')

def calculateDeckScore(card_id,deck_id,user_id):
  userdeck=UserDeck.query.filter_by(deck_id=deck_id,user_id=user_id).one()
  total=0 
  d={1:0.4,2:0.7,3:1}
  sumtotal=0
  card_ids=[]
  for card in Card.query.filter_by(DeckId=deck_id).all():
    card_ids.append(card.id)
  for id in card_ids:
    usercard=UserCard.query.filter_by(user_id=user_id,card_id=id).one()
    sumtotal+=usercard.score*(d[usercard.difficulty])
    total+=1*(d[usercard.difficulty])
  userdeck.score=round((sumtotal/total)*100,3)
  userdeck.last_reviewed=dt.datetime.now()
  db.session.commit()
  return

@app.route('/<uname>/logout')
def logout(uname):
  global logged_in
  if logged_in==uname:
    logged_in=""
  return redirect('/')
  

@app.route("/<user>/dashboard/<deckid>",methods=['GET','POST'])
def ShowCards(user,deckid):
  global logged_in
  if not logged_in:
    return redirect('/')
  try:
    if request.method=='GET':
      
      result=Card.query.filter_by(DeckId=deckid).all()
      name=Deck.query.filter_by(id=deckid).one()
      user=User.query.filter_by(username=user).one()
      usercard={}
      for q in UserCard.query.filter_by(user_id=user.id):
        usercard[q.card_id]=q
      if not result:
        n=0
      else:
        n=1
      
      return render_template('Cards.html',user=user,cards=result,usercard=usercard,n=n,deckid=deckid,answer='',cardid='')

    elif request.method=='POST':
      form=request.form
      
      if not form:
        return render_template('Error.html')
      question=list(form.keys())[-1]

      c=Card.query.filter_by(id=question).one()
      user=User.query.filter_by(username=user).one()
      answer=form.get(question)
      difficulty= form.get('Difficulty')
      if difficulty=='Hard':
        difficulty=3
      elif difficulty=='Medium':
        difficulty=2
      else:
        difficulty=1
      
      usercard=UserCard.query.filter_by(user_id=user.id,card_id=c.id).one()
      if "".join(answer.lower().split())=="".join(c.back.lower().split()):
        usercard.score=1
        usercard.difficulty=difficulty
      else:
        usercard.difficulty=difficulty
        usercard.score=0
      
      user.last_reviewed=dt.datetime.now()
      usercard.last_reviewed=dt.datetime.now()
      calculateDeckScore(user_id=user.id,card_id=c.id,deck_id=deckid)
      db.session.commit()
      result=Card.query.filter_by(DeckId=deckid).all()
      if not result:
        n=0
      else:
        n=1
      usercard={}
      for q in UserCard.query.filter_by(user_id=user.id):
        usercard[q.card_id]=q
      
      #scoring method and reviewing system
      
      return render_template('Cards.html',user=user,cards=result,usercard=usercard,n=n,deckid=deckid,answer=c.back,cardid=question)
  except Exception as e:
    
    return render_template('Error.html')

@app.route('/<uname>/<deckid>/addcard',methods=['GET','POST'])
def addcard(uname,deckid):
  global logged_in
  if not logged_in:
    return redirect('/')
  try:
    if request.method=='GET':
      user=User.query.filter_by(username=uname).one()
      return render_template('AddCard.html',user=user,deckid=deckid)
    else:
      form=request.form
      front=form['Front']
      back=form['Back']
      user=User.query.filter_by(username=uname).one()
      c=Card.query.filter_by(front=front,back=back,DeckId=deckid).all()
      if not c:
        C=Card(front=front,back=back,DeckId=deckid)
        db.session.add(C)
        db.session.commit()
        c=Card.query.filter_by(front=front,back=back,DeckId=deckid).one()
        ucard=UserCard(user_id=user.id,card_id=c.id,score=0,last_reviewed=dt.datetime.now())
        db.session.add(ucard)
        db.session.commit()
      return redirect(f'/{uname}/dashboard/{deckid}')
    
  except Exception as e:
    print(e)
    return render_template('Error.html')

@app.route('/<uid>/<did>/<cid>/editcard',methods=['GET','POST'])
def editcard(uid,did,cid):
  global logged_in
  if not logged_in:
    return redirect('/')
  try:
    if request.method=='GET':
      user=User.query.filter_by(id=uid).one()
      card=Card.query.filter_by(id=cid).one()
      return render_template('EditCard.html',user=user,uid=uid,did=did,cid=cid,card=card)
    else:
      user=User.query.filter_by(id=uid).one()
      card=Card.query.filter_by(id=cid).one()
      ucard=UserCard.query.filter_by(card_id=cid,user_id=uid).one()
      form=request.form
      card.front=form['Front']
      card.back=form['Back']
      db.session.commit()
      return redirect(f'/{user.username}/dashboard/{did}')
  except Exception as e:
    return render_template('Error.html')

@app.route('/<uid>/<did>/<cid>/deletecard')
def deletecard(uid,did,cid):
  global logged_in
  if not logged_in:
    return redirect('/')
  try:
    c=Card.query.filter_by(id=cid).one()
    user=User.query.filter_by(id=uid).one()
    ucard=UserCard.query.filter_by(user_id=uid,card_id=cid).one()
    db.session.execute(f'delete from usercard where user_id={uid} and card_id={cid};')
    db.session.execute(f'delete from card where id={cid};')
    db.session.commit()
    return redirect(f'/{user.username}/dashboard/{did}')
  except Exception as e:
    print(e)
    return render_template('Error.html')


@app.route('/<string:uname>/AddDeck',methods=['GET','POST'])
def addDeck(uname):
  global logged_in
  if logged_in=='':
    return redirect(f'/')
  if request.method=='GET':
    try:
      user=User.query.filter_by(username=uname).one()
      return render_template('AddDeck.html',user=user)
    except:
      return render_template('Error.html')
  else:
    form=request.form
    user=User.query.filter_by(username=uname).one()
    try:
      name=form['Name']
      description=form['Description']
      try:
        for ud in UserDeck.query.filter_by(user_id=user.id).all():
          
          d=Deck.query.filter_by(id=ud.deck_id).one()
          if d.name==name:

            return redirect('/')
          else:
            continue
        print("COMING HERE")
      except:
        pass
      deck=Deck(name=name,description=description)
      db.session.add(deck)
      #Add to user deck
      deck=Deck.query.filter_by(name=name,description=description).all()
      deck_id=list(deck)[-1].id
      udeck=UserDeck(user_id=user.id,deck_id=deck_id,score=0,last_reviewed=dt.datetime.now())
      db.session.add(udeck)
      db.session.commit()
      #return something
      return redirect(f'/{uname}/dashboard')
    except Exception as e:
      print('ERROR HERE',e) 
      return render_template('Error.html')
    pass

@app.route('/<uid>/<did>/editdeck',methods=['GET','POST'])
def editdeck(uid,did):
  global logged_in
  if logged_in=='':
    return redirect(f'/')
  try:
    if request.method=='GET':
      user=User.query.filter_by(id=uid).one()
      deck=Deck.query.filter_by(id=did).one()
      return render_template('EditDeck.html',user=user,uid=uid,did=did,deck=deck)
    else:
      user=User.query.filter_by(id=uid).one()
      form=request.form
      deck=Deck.query.filter_by(id=did).one()
      deck.name=form['Name']
      deck.description=form['Description']
      
      db.session.commit()
      return redirect(f'/{user.username}/dashboard')
  except Exception as e:
    print(e)
    return render_template('Error.html')
  
@app.route('/<uid>/<did>/deletedeck')
def deletedeck(uid,did):
  global logged_in
  if logged_in=='':
    return redirect(f'/')
  try:
    deck=Deck.query.filter_by(id=did).one()
    user=User.query.filter_by(id=uid).one()
    for card in Card.query.filter_by(DeckId=did):
      db.session.execute(f'delete from usercard where card_id={card.id};')
    db.session.execute(f'delete from card where DeckId={did};')
    db.session.execute(f'delete from userdeck where deck_id={did};')
    db.session.execute(f'delete from deck where id={did};')
    db.session.commit()
    return redirect(f'/{user.username}/dashboard')
  except Exception as e:
    print(e)
    return render_template('Error.html')

@app.route('/register',methods=['GET','POST'])
def register():
  if request.method=='GET':
    return render_template('register.html',uname=False,email=False,unknown=False)
  elif request.method=='POST':
    form=request.form
    email=form.get('email')
    if '@' in email and '.com' in email and email.count('@')==1 and email.count('.com')==1:
      email=email
    else:
      return render_template('register.html',unknown=True,uname=False,email=False)
    user=form.get('Username')
    try:
      User.query.filter_by(email=email).one()
      return render_template('register.html',email=True,uname=False,unknown=False)
    except:
      try:
        User.query.filter_by(username=user).one()
        return render_template('register.html',uname=True,email=False,unknown=False)
      except:
        pass

    try:
      password=form.get('Password')
    except:
      password=''
    try:
      user=User(username=user,password=password,email=email,last_reviewed=dt.datetime.now())
      db.session.add(user)
      
        
      db.session.commit()
      return redirect('/') #Successful user creation    
    except:    
      return render_template('register.html',unknown=True,uname=False,email=False)

      
@app.route('/',methods=['GET','POST'])
def loginView():
  global logged_in
  if logged_in!='':
    return redirect(f'/{logged_in}/dashboard')
  if request.method=='GET':
    return render_template('login.html',value=True)
  elif request.method=='POST':
    form=request.form
    userOrEmail=form.get('Username')

    try:
      password=form.get('Password')
    except:
      password=''
    try:
      result=User.query.filter_by(username=userOrEmail).one()
      if result.password!=password:
        return render_template('login.html',value=False)
      logged_in=result.username
      return redirect(f'/{result.username}/dashboard')
    except:    
      try:
        result=User.query.filter_by(email=userOrEmail).one()
        if result.password!=password:
          return render_template('login.html',value=False)
        logged_in=result.username
        return redirect(f'/{result.username}/dashboard')
      except:
        return redirect('/register')

@app.route('/<uname>/review')
def review(uname):
  if logged_in!=f'{uname}':
    return redirect('/')

  query=Deck.query.all()
  userdeck={}
  user=User.query.filter_by(username=uname).one()
  deckids=[]
  for q in UserDeck.query.order_by(UserDeck.score.asc()).filter_by(user_id=user.id):
    userdeck[q.deck_id]=q
    deckids.append(q.deck_id)
  l=[]
  for deck in query:
    if deck.id in deckids:
      l.append(deck)
  query=l
  return render_template('Review.html',user=user,decks=query,n=len(query),userdeck=userdeck)

@app.route('/<uname>/<deckid>/review',methods=['GET','POST'])
def cardreview(uname,deckid):
  if request.method=='GET':
    result=Card.query.filter_by(DeckId=deckid).all()
    name=Deck.query.filter_by(id=deckid).one()
    user=User.query.filter_by(username=uname).one()
    usercard={}
    for q in UserCard.query.filter_by(user_id=user.id):
      usercard[q.card_id]=q
    if not result:
      n=0
    else:
      n=1
    
    return render_template('CardReview.html',user=user,cards=result,usercard=usercard,n=n,deckid=deckid)
  else:
    form=request.form
    question=list(form.keys())[-1]
    c=Card.query.filter_by(id=question).one()
    user=User.query.filter_by(username=uname).one()
    difficulty= form.get('Difficulty')
    if difficulty=='Hard':
      difficulty=3
    elif difficulty=='Medium':
      difficulty=2
    else:
      difficulty=1
    
    usercard=UserCard.query.filter_by(user_id=user.id,card_id=c.id).one()
    usercard.difficulty=difficulty
    user.last_reviewed=dt.datetime.now()
    usercard.last_reviewed=dt.datetime.now()
    calculateDeckScore(user_id=user.id,card_id=c.id,deck_id=deckid)
    db.session.commit()
    result=Card.query.filter_by(DeckId=deckid).all()
    if not result:
      n=0
    else:
      n=1
    usercard={}
    for q in UserCard.query.filter_by(user_id=user.id):
      usercard[q.card_id]=q
    result=Card.query.filter_by(DeckId=deckid).all()
    name=Deck.query.filter_by(id=deckid).one()
    user=User.query.filter_by(username=uname).one()
    usercard={}
    for q in UserCard.query.filter_by(user_id=user.id):
      usercard[q.card_id]=q
    if not result:
      n=0
    else:
      n=1
    return render_template('CardReview.html',user=user,cards=result,usercard=usercard,n=n,deckid=deckid)
    
