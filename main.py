
# Import necessary modules
from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy

# Initialize the Flask app
app = Flask(__name__)

# Configure the database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///algebra.db'
db = SQLAlchemy(app)

# Define the Lesson model
class Lesson(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), unique=True, nullable=False)
    content = db.Column(db.Text, nullable=False)
    is_complete = db.Column(db.Boolean, default=False)

# Define the Quiz model
class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), unique=True, nullable=False)
    questions = db.relationship('Question', backref='quiz', lazy=True)

# Define the Question model
class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(255), nullable=False)
    option1 = db.Column(db.String(255), nullable=False)
    option2 = db.Column(db.String(255), nullable=False)
    option3 = db.Column(db.String(255), nullable=False)
    option4 = db.Column(db.String(255), nullable=False)
    answer = db.Column(db.String(255), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)

# Define the User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    progress = db.relationship('Progress', backref='user', lazy=True)

# Define the Progress model
class Progress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lesson.id'), nullable=False)
    is_complete = db.Column(db.Boolean, default=False)
    score = db.Column(db.Integer, default=0)

# Create the database tables
db.create_all()

# Define the homepage route
@app.route('/')
def homepage():
    return render_template('index.html')

# Define the lessons route
@app.route('/lessons')
def lessons():
    lessons = Lesson.query.all()
    return render_template('lessons.html', lessons=lessons)

# Define the quizzes route
@app.route('/quizzes')
def quizzes():
    quizzes = Quiz.query.all()
    return render_template('quizzes.html', quizzes=quizzes)

# Define the progress tracker route
@app.route('/progress')
def progress():
    user = User.query.filter_by(username=session['username']).first()
    progress = Progress.query.filter_by(user_id=user.id).all()
    return render_template('progress.html', progress=progress)

# Define the mark lesson as complete route
@app.route('/mark-lesson-complete', methods=['POST'])
def mark_lesson_complete():
    lesson_id = request.form['lesson_id']
    user = User.query.filter_by(username=session['username']).first()
    progress = Progress.query.filter_by(user_id=user.id, lesson_id=lesson_id).first()
    progress.is_complete = True
    db.session.commit()
    return redirect(url_for('progress'))

# Define the submit quiz route
@app.route('/submit-quiz', methods=['POST'])
def submit_quiz():
    quiz_id = request.form['quiz_id']
    user = User.query.filter_by(username=session['username']).first()
    quiz = Quiz.query.get(quiz_id)
    score = 0
    for question in quiz.questions:
        answer = request.form.get(f'question-{question.id}')
        if answer == question.answer:
            score += 1
    progress = Progress.query.filter_by(user_id=user.id, quiz_id=quiz_id).first()
    progress.score = score
    db.session.commit()
    return redirect(url_for('progress'))

# Main driver function
if __name__ == '__main__':
    app.run(debug=True)
