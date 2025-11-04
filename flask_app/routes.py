from flask import current_app as app
from flask import render_template, redirect, request, session, url_for, copy_current_request_context
from flask_socketio import SocketIO, emit, join_room, leave_room, close_room, rooms, disconnect
from .utils.database.database  import database
from werkzeug.datastructures   import ImmutableMultiDict
from pprint import pprint
import json
import random
import functools
from . import socketio
db = database()


#######################################################################################
# AUTHENTICATION RELATED
#######################################################################################
def login_required(func):
    @functools.wraps(func)
    def secure_function(*args, **kwargs):
        if "email" not in session:
            return redirect(url_for("login", next=request.url))
        return func(*args, **kwargs)
    return secure_function

def getUser():
	return session['email'] if 'email' in session else 'Unknown'

@app.route('/login')
def login():
	return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('email', default=None)
    return redirect('/')

@app.route('/processsignup', methods = ["POST","GET"])
def processsignup():
	# Extract email and password from the POST request
    form_fields = {key: request.form.get(key) for key in request.form.keys()}
    email = form_fields.get("email")
    password = form_fields.get("password")

    if len(email) == 0 or len(password) == 0:
        status = {'success': False, 'message': "Please enter an email and password"}
        return json.dumps(status)
    
    # Create user
    result = db.createUser(email=email, password=password, role='guest')
    if result['success']:
        status = {'success': True, 'message': "Signup successful"}
    else:
        status = {'success': False, 'message': result['message']}
    
    # Return status as a JSON response
    return json.dumps(status)

@app.route('/processlogin', methods = ["POST","GET"])
def processlogin():
	# Extract email and password from the POST request
    form_fields = {key: request.form.get(key) for key in request.form.keys()}
    email = form_fields.get("email")
    password = form_fields.get("password")
    
    # Authenticate user
    result = db.authenticate(email=email, password=password)
    if result['success']:
        # Update the session with an encrypted version of the email
        # session['email'] = db.reversibleEncrypt('encrypt', email)
        session['email'] = email
        status = {'success': True, 'message': "Login successful"}
    else:
        status = {'success': False, 'message': "Invalid credentials"}
    
    # Return status as a JSON response
    return json.dumps(status)


#######################################################################################
# CHATROOM RELATED
#######################################################################################
@app.route('/chat')
@login_required
def chat():
    return render_template('chat.html', user=getUser())

@socketio.on('joined', namespace='/chat')
def joined(message):
    join_room('main')
    user = getUser()
    if user == "owner@email.com":
        emit('status', {'msg': user + ' has entered the room.', 'style': 'width: 100%;color:blue;text-align: right'}, room='main')
    else:
        emit('status', {'msg': user + ' has entered the room.', 'style': 'width: 100%;color:gray;text-align: left'}, room='main')

@socketio.on('text', namespace='/chat')
def text(message):
    user = getUser()
    message_str = user.split('@')[0] + " said: " + message['msg']
    sender_type = "owner" if "owner" in user else "guest"
    emit('message', {'msg': message_str, 'sender': sender_type}, room='main')

@socketio.on('left', namespace='/chat')
def left(message):
    user = getUser()
    sender_style = 'width: 100%; color: blue; text-align: right' if "owner" in user else 'width: 100%; color: gray; text-align: left'
    leave_room('main')
    emit('status', {'msg': f'{user} has left the room.', 'style': sender_style}, room='main')





#######################################################################################
# OTHER
#######################################################################################
@app.context_processor
def inject_user():
    # Retrieve the user's email from the session if logged in
    user = session.get('email', 'Unknown')
    return {'user': user}

@app.route('/')
def root():
	return redirect('/home')

@app.route('/home')
def home():
	x = random.choice(['React','TypeScript','JavaScript','Adaptability','Algorithms',
                        'Data Structures','Data Analysis','SQL','MongoDB','REST','OOP',
                        'Artificial Intelligence','Tenacity','Computer Security', 
                        'Mobile Apps','NodeJs','NestJs','NextJs','Git','ML','DevOps',
                        'Systems', 'Entity-Relationships', 'QA', 'Python', 'Pair Programming',
                        'AWS', 'scrum', 'HTML', 'Fast Learner', 'CSS', 'coachable'])
	return render_template('home.html', user=getUser(), skill = x)

@app.route('/resume')
def resume():
	resume_data = db.getResumeData()
	pprint(resume_data)
	return render_template('resume.html', resume_data = resume_data)

@app.route('/projects')
def projects():
	return render_template('projects.html')

@app.route('/piano')
def piano():
	return render_template('piano.html')

@app.route('/processfeedback', methods=['POST'])
def processfeedback():
    feedback_dict = {
        "name": request.form.get("name"),
        "email": request.form.get("email"),
        "comment": request.form.get("comment")
    }
    # Insert feedback into the database feedback table
    table='feedback'
    columns_str = ', '.join(['name', 'email', 'comment'])
    placeholders = ', '.join(['%s'] * 3)

    query = f'INSERT INTO {table} ({columns_str}) VALUES ({placeholders})'

    db.query(query, (feedback_dict["name"], feedback_dict["email"], feedback_dict["comment"]))
    # db.execute("INSERT INTO feedback (name, email, comment) VALUES (%s, %s, %s)",
    #            (feedback["name"], feedback["email"], feedback["comment"]))
    
    # Retrieve all feedback to display
    feedback_data = db.query("SELECT * FROM feedback")
    return render_template("processfeedback.html", feedback=feedback_data)