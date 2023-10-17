import os

import speech_recognition as sr

from flask import url_for, request, session
import json

from twilio.twiml.voice_response import VoiceResponse
from twilio.rest import Client

from .models import Survey, Question, Answer

### --------------------------------------------------

account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
auth_token = os.environ.get('TWILIO_AUTH_TOKEN')

VOICE_INSTRUCTIONS = {
    Question.TEXT: 'Press ANY key to continue',
}

### --------------------------------------------------

# # -------------------------------------------------- trello utili --------------------------------------------------


# # create twilio client
def createTwilioClient():
    return Client(account_sid, auth_token)


# # create twili call
def createCall(client, twilio_phone_number, client_phone_number, client_name, webhook_url):
    return client.calls.create(
        to=client_phone_number,
        from_=twilio_phone_number,
        url=f'{webhook_url}?client_name={client_name}'
    )


def extract_content():
    return 'Transcription in progress.'    


def confirmAnswer(question_id, session_id, answer_content):
    response = VoiceResponse()
    print(f'confirmAnswer: {answer_content}')
    response.say('Is your answer really?')
    transcribe_url = url_for('confirm_transcription', question_id=question_id, session_id=session_id, answer_content=answer_content)
    
    response.record(transcribe_callback=transcribe_url)

    return str(response)


def recordAnswer(question, client_name = ''):
    response = VoiceResponse()
    response.say(str(question.content).format(name=client_name))
    response.say(VOICE_INSTRUCTIONS[question.kind])

    action_url = url_for('answer', question_id=question.id)
    transcription_url = url_for('answer_transcription', question_id=question.id)
    response.record(action=action_url, transcribe_callback=transcription_url)
    # response.record(action_url=action_url, transcribe_callback=action_url)
    return str(response)


def goodbye_twiml():
    response = VoiceResponse()
    response.say("Thank you. Good bye.")
    response.hangup()

    if 'question_id' in session:
        del session['question_id']
    return str(response)


def getSessionId():
    return request.values.get('CallSid')


def transcribe_twilio_audio(audio_file):
    recognizer = sr.Recognizer()

    with sr.AudioFile(audio_file) as source:
        audio = recognizer.record(source)

    try:
        # Recognize speech using Google Web Speech API
        text = recognizer.recognize_google(audio)
        return text  # Return the transcription
    except sr.UnknownValueError:
        return "STT API could not understand the audio"
    except sr.RequestError as e:
        return "Could not request results from STT API; {0}".format(e)


# # -------------------------------------------------- parsers for json --------------------------------------------------
def survey_from_json(survey_json_string):
    survey_dict = json.loads(survey_json_string)
    survey = Survey(title=survey_dict['title'])
    survey.questions = questions_from_json(survey_json_string)
    return survey


def questions_from_json(survey_json_string):
    questions = []
    questions_dicts = json.loads(survey_json_string).get('questions')
    for question_dict in questions_dicts:
        content = question_dict['content']
        confirm = question_dict['confirm']
        kind = question_dict['type']
        questions.append(Question(content=content, confirm=confirm, kind=kind))
    return questions


# # -------------------------------------------------- other utils --------------------------------------------------
def storeAnswer(session_id, question_id, content):
    Answer.update_content(session_id=session_id, question_id=question_id, content=content)


def printRequestValues():
    values = request.values.items()
    for key, value in values:
        print(f'{key}: {value}')


def isBeforeSession(question_id):
    return question_id == '0'
