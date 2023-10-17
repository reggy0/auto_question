import os
from flask import request, redirect, flash, url_for
from sqlalchemy import and_

from . import app, db, utils
from .models import Question, Answer

### --------------------------------------------------

twilio_phone_number = '+18886732419'
webhook_url = '{app_url}/answer/0'.format(app_url=os.environ['APP_URL'])

client = utils.createTwilioClient()

### --------------------------------------------------


# # start calling
@app.route('/start-call', methods=['POST'])
def start_call():
    try:
        client_phone_number = request.values['phone_number']
        client_name = request.values['name']

        print(f'calling to: {client_phone_number} {client_name}')
        utils.createCall(client, twilio_phone_number, client_phone_number, client_name, webhook_url)
        
        flash('A call has been created successfully. please refresh this page to see updated response.', 'info')
    except Exception as e:
        print(str(e))
        flash('A call attempt failed, please try again.', 'danger')

    return redirect(url_for('root'))        

# # hook to handle answers
@app.route('/answer/<question_id>', methods=['POST'])
def answer(question_id):
    # # prepare session
    if utils.isBeforeSession(question_id):
        first_question = Question.query.first()        
        if first_question:
            client_name = request.args.get('client_name')
            return utils.recordAnswer(first_question, client_name)
        else:
            return utils.goodbye_twiml()
    # # real session
    else:
        print(f'---------- answer response {question_id} ----------')
        # utils.printRequestValues()           

        question = Question.query.get(question_id)
        session_id = utils.getSessionId()
        answer = Answer.query.filter(and_(Answer.question_id == question_id, Answer.session_id == session_id)).first()

        if answer is None:
            db.save(
                Answer(
                    content=utils.extract_content(), question=question, session_id=utils.getSessionId()
                )
            )

        # status = utils.getTranscriptionStatus()
        # if status == 'completed':
        next_question = question.next()

        if next_question: 
            # content = utils.getTranscriptionText()                
            # return utils.confirmAnswer(question_id, session_id, content)
            # return ''
            # utils.storeAnswer(session_id, question_id, content)        
            return utils.recordAnswer(next_question)
        else:
            return utils.goodbye_twiml()

    return ''


# # hook handle to transcribe audio to text
@app.route('/answer/transcription/<question_id>', methods=['POST'])
def answer_transcription(question_id):
    print('---------- received transcription -----------')
    utils.printRequestValues()
    
    session_id = utils.getSessionId()

    # Get the audio file URL from Twilio's request
    audio_url = request.values.get('RecordingUrl')

    # Download the audio and transcribe it using your custom function
    transcription = utils.transcribe_twilio_audio(audio_url)

    # Store the transcription in the database or process it as needed
    utils.storeAnswer(session_id, question_id, transcription)

    return ''



# @app.route('/answer/confirm/transcription/<question_id>/<session_id>/<answer_content>', methods=['POST'])
# def confirm_transcription(question_id, session_id, answer_content):
#     question = Question.query.get(question_id)
#     next_question = question.next()

#     confirm_content: str = utils.getTranscriptionText()
#     confirm_content = confirm_content.strip()

#     print('Question: {}'.format(question.content))
#     print(f'Answer: {answer_content}')
#     print(f'Confirm: {confirm_content}')

#     if 'yes' in confirm_content:
#         utils.storeAnswer(session_id, question_id, answer_content)   
#         return utils.recordAnswer(next_question)
#     else:
#         return utils.recordAnswer(question)
