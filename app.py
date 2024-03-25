import os
import replicate
from flask import Flask, request, jsonify, redirect, url_for, render_template
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS
from flask_login import LoginManager, logout_user, login_required, current_user,login_user
from flask_login import UserMixin
from datetime import datetime
from dotenv import load_dotenv

load_dotenv() 


app = Flask(__name__, template_folder='C:\\Users\\DELL\\Desktop\\PROJECT\\API\\templates')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:\\Users\\DELL\\Desktop\\PROJECT\\API\\users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
# After creating your Flask app
CORS(app)

app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'default_secret_key')

# initialize LoginManager
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
 


#CHAT 
class Chat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)  # The title of the chat, which is the first query
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Link to the user model
    messages = db.relationship('Message', backref='chat', lazy=True)  # Relationship to messages
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # When the chat was started

    # Relationship to user
    user = db.relationship('User', back_populates='chats')

    def __repr__(self):
        return f'<Chat {self.title}>'

User.chats = db.relationship('Chat', order_by=Chat.id, back_populates='user')

#STORE EACH MESSAGE IN THE CHAT
class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chat_id = db.Column(db.Integer, db.ForeignKey('chat.id'), nullable=False)  # Link to the chat model
    text = db.Column(db.String(1024), nullable=False)  # The text of the message
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # When the message was sent

    def __repr__(self):
        return f'<Message {self.text}>'




@app.route('/send_message', methods=['POST'])
def send_message():
    user_message = request.form.get('message')
    print(f"Received message: {user_message}")
    user_id = current_user.get_id()
    
    if user_message:  # Check if the message is not empty
        # If this is the first message in the chat, create a new chat session
        new_chat = Chat(title=user_message, user_id=user_id)
        db.session.add(new_chat)
        db.session.commit()

        # Add your logic to process the message and generate a response

    # Continue with your response processing and return the response
    return jsonify({'success': 'Message sent', 'message': user_message})


@app.route('/chat_history', methods=['GET'])
@login_required
def chat_history():
    user_chats = current_user.chats.order_by(Chat.created_at.desc()).all()
    chat_history = [{
        'id': chat.id,
        'title': chat.title,
        'created_at': chat.created_at.strftime('%Y-%m-%d %H:%M:%S')
    } for chat in user_chats]
    return jsonify(chat_history)



login_manager.login_view = 'signin'


@app.route('/chat')
@login_required
def chatprofile():
    if not current_user.is_authenticated:
        return redirect(url_for('signin'))  # Redirect to login page if user not logged in
    user = User.query.filter_by(id=current_user.id).first()
    if user:
        user_chats = Chat.query.filter_by(user_id=user.id).order_by(Chat.created_at.desc()).all()
        first_letter = user.username[0].upper()
        return render_template('chat.html', first_letter=first_letter, user_chats=user_chats)
    else:
        print("User not found")
        return "Error: User not found", 404  # Handle user not found error


@app.route('/chat')
@login_required
def chat():
    user_chats = Chat.query.filter_by(user_id=current_user.id).all()
    return render_template('chat.html', user_chats=user_chats)



@app.route('/create_chat', methods=['POST'])
@login_required
def create_chat():
    chat_title = request.json.get('chat_title')  # Retrieve the title from the JSON sent by the AJAX call
    
    if not chat_title.strip():  # Ensuring that the title is not just whitespace
        # Handle the error appropriately
        return jsonify({'status': False, 'message': 'Chat title is required'}), 400
    
    new_chat = Chat(title=chat_title, user_id=current_user.id)
    db.session.add(new_chat)
    db.session.commit()
    
    # Respond with the details of the new chat
    return jsonify({
        'status': True,
        'message': 'Chat created successfully',
        'chat_id': new_chat.id,
        'title': new_chat.title,
        'created_at': new_chat.created_at.strftime('%Y-%m-%d %H:%M:%S')
    }), 201
  

@app.route('/')
def home():
    return render_template('index.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    try:
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            

            if User.query.filter_by(username=username).first():
                return 'Username already exists.', 400
            
            new_user = User(username=username)
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()

            return redirect(url_for('chat'))
    except Exception as e:
        print(f"Error: {e}")
    return render_template('signup.html')

#signin
@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            # Redirect to the chat page after successful login
            return redirect(url_for('chat'))
        else:
            # Provide feedback that login failed
            return 'Invalid username or password.', 401
    
    return render_template('signin.html')


#redirect to signup page to create an account
@app.route('/notreg', methods=['GET', 'POST'])
def notreg():
    return redirect(url_for('signup'))


#redirect to signin page already have an account
@app.route('/reg', methods=['GET', 'POST'])
def reg():
    return redirect(url_for('signin'))


#RESET PASSWORD  
@app.route('/forgotpassword', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        username = request.form.get('username')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        if new_password != confirm_password:
            return jsonify({'status': False, 'message': 'Passwords do not match'}), 400

        user = User.query.filter_by(username=username).first()

        if user:
            user.set_password(new_password)
            db.session.commit()
            return jsonify({'status': True, 'message': 'Password has been updated successfully'}), 200
        else:
            return jsonify({'status': False, 'message': 'User not found'}), 404


#Model
@app.route("/bucc-7b-bot/", methods = ["POST", "GET"])
def llama_2_13b():
    if request.method == "POST":
        # Extracting response from JSON 
        api_json = request.json     

        question = api_json["question"].strip().lower()
        print(question)
        # Specifying AI Info
        context = open("dataset.txt", "r").read()
       
        # # Extracting response.
        response_list = []
        response_string = ""

        output = replicate.run(
            "meta/llama-2-7b-chat:13c3cdee13ee059ab779f0291d29054dab00a47dad8261375654de5540165fb0",
            input={
                "prompt": f"{context} Question: {question}",
                "max_new_tokens" : 60,
                "repetition_penalty" : 3,
                "temperature" : 0.8,
            }
        )


        for item in output:
            response_list.append(item)

        response_string = response_string.join(response_list)
        # Clearing response list for next prompt response.
        response_list.clear()

        # return result
        response = {"response" : response_string}
        response_string = "" # Clearing previous response.
        return jsonify(response)
    # Handling Other kinds of requests.
    else:
        info = "This Software Engineering (BUCC) endpoint can only be accessed using a POST request, provide the right inputs as observed below. Previous prompts don't need to be separated with new line characters, just provide them as a continuous string."
        sample_prompt = {
        "question": "What is BUCC?",
        }
        sample_output = {
            "response":"BUCC stands for Babcock University Computer Club and is a popular name for the school of Computing and Engineering Sciences."
        }
        feedback = {
            "Info": info,
            "sample prompt" : sample_prompt,
            "sample output": sample_output
        }
        return jsonify(feedback)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

 

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Ensure tables are created before querying
        users = User.query.all()  # Now it's safe to query
    app.run(debug=True, host='0.0.0.0', port=8000)




   
