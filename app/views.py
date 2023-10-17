from . import app
from . import main_view   # view
from flask import render_template
from .models import Question


@app.route('/')
def root():
    questions = Question.query.all()
    return render_template('index.html', questions=questions)
