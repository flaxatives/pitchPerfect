"""
This sample demonstrates a simple skill built with the Amazon Alexa Skills Kit.
The Intent Schema, Custom Slots, and Sample Utterances for this skill, as well
as testing instructions are located at http://amzn.to/1LzFrj6

For additional samples, visit the Alexa Skills Kit Getting Started guide at
http://amzn.to/1LGWsLG
"""

from __future__ import print_function
from random import choice


# --------------- Helpers that build all of the responses ----------------------

def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': "SessionSpeechlet - " + title,
            'content': "SessionSpeechlet - " + output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }


def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }


def build_note_response(title, output, reprompt_text, should_end_session, note):
    return {
        'outputSpeech': {
            'type': 'SSML',
            'ssml': """
                    <speak>
                        {speaktext}
                        <audio src="{src}" />
                    </speak>
            """.format(speaktext=output, src=get_mp3(note))
        },
        'card': {
            'type': 'Simple',
            'title': "SessionSpeechlet - " + title,
            'content': "SessionSpeechlet - " + output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'SSML',
                'ssml': """
                        <speak>
                            {speaktext}
                            <audio src="{src}" />
                        </speak>
                """.format(speaktext=reprompt_text, src=get_mp3(note))
            }
        },
        'shouldEndSession': should_end_session
    }


# --------------- Functions that control the skill's behavior ------------------

def get_welcome_response():
    """ If we wanted to initialize the session to have some attributes we could
    add those here
    """

    session_attributes = {}
    card_title = "Welcome"
    speech_output = "Do you want to play Easy, Medium, or Hard?" \
    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = speech_output

    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(card_title, 
        speech_output, reprompt_text, should_end_session)
)


def handle_session_end_request():
    card_title = "Session Ended"
    correct = session['attributes']['correct']
    total = session['attributes']['total']

    speech_output = "Your accuracy is {0}% with {1} out of {2}".format(
                    correct // total, correct, total)
    # Setting this to true ends the session and exits the skill.
    should_end_session = True
    return build_response({}, build_speechlet_response(
        card_title, speech_output, None, should_end_session))


def set_difficulty_in_session(intent, session):
    """ Sets the color in the session and prepares the speech to reply to the
    user.
    """

    card_title = intent['name']
    session_attributes = {}
    should_end_session = False

    speechlet_response = None

    if 'Difficulty' in intent['slots']:
        session_difficulty = intent['slots']['Difficulty']['value']
        session_attributes = {"difficulty": session_difficulty}
        session['attributes'] = session_attributes
        

        speech_output = "You have chosen {0}.".format(session_difficulty)
                        
        reprompt_text = speech_output

        # Here's where we start playing notes.
        set_new_note_in_session(intent, session)
        speechlet_response = build_note_response(card_title,
                speech_output, reprompt_text, should_end_session, session['attributes']['note'])

    else:
        speech_output = "Difficulties are Easy, Medium, or Hard." \
                        "Please try again."
        reprompt_text = speech_output
        speechlet_response = build_speechlet_response(session_attributes, card_title,
                speech_output, reprompt_text, should_end_session)

    return build_response(session_attributes, speechlet_response)


def set_new_note_in_session(intent, session):
    difficulties = {
            "easy"   : list("CDE"),
            "medium" : list("CDEFG"),
            "hard"   : list("ABCDEFG")
    }

    session_difficulty = session['attributes']['difficulty'] 
    if session_difficulty not in difficulties:
        return

    session['attributes']['note'] = choice(difficulties[session_difficulty])


def guess_note_in_session(intent, session):
    card_title = intent['name']
    if 'attributes' not in session:
        return get_welcome_response()

    should_end_session = False
    session_attributes = session['attributes']
    session_difficulty = session['attributes']['difficulty']

    if not 'session_difficulty' in session:
        # this shouldn't happen. Exit everything
        print("Something wrong happened.")
        speech_output = "Something wrong happened. Closing."
        reprompt_text = speech_output

    guessed_note = intent['slots']['Note']['value']
    session_note = session['attributes']['note']
    if guessed_note.lower() == session_note.lower():
        speech_output = "Correct!"
        set_new_note_in_session(intent, session)

    else:
        speech_output = "Incorrect. Guess again."

    reprompt_text = "Guess the note."

    speechlet_response = build_note_response(card_title,
            speech_output, reprompt_text, should_end_session, session['attributes']['note'])
    return build_response(session_attributes, speechlet_response)


def get_mp3(note):
    note = note.lower()
    host = "HOSTNAME_HERE"
    return host + "/piano_{0}5.mp3".format(note)




# --------------- Events ------------------

def on_session_started(session_started_request, session):
    """ Called when the session starts """

    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])


def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """

    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # Dispatch to your skill's launch


    return get_welcome_response()


def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """

    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    # Dispatch to your skill's intent handlers
    if intent_name == "StartGame":
        return get_welcome_response()
    elif intent_name == "SelectDifficulty":
        return set_difficulty_in_session(intent, session)
    elif intent_name == "GuessNote":
        return guess_note_in_session(intent, session)
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        raise ValueError("Invalid intent")


def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.

    Is not called when the skill returns should_end_session=true
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # add cleanup logic here


# --------------- Main handler ------------------

def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])

    """
    Uncomment this if statement and populate with your skill's application ID to
    prevent someone else from configuring a skill that sends requests to this
    function.
    """
    # if (event['session']['application']['applicationId'] !=
    #         "amzn1.echo-sdk-ams.app.[unique-value-here]"):
    #     raise ValueError("Invalid Application ID")

    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])
