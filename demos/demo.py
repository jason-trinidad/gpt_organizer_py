import streamlit as st
from streamlit_chat import message

# import azure.cognitiveservices.speech as speechsdk

import gpt_organizer.prompts as prompts
from gpt_organizer.OrganizerAgent import OrganizerAgent
from gpt_organizer.utils import *


def on_message_change():
    # Handle user message
    st.session_state["history"].append(st.session_state["message"])
    st.session_state["message"] = ""

    # Get response
    response = st.session_state["agent"].get_response(
        st.session_state["history"],
        st.session_state["prompt"],
        st.session_state["form_prompt"],
    )
    st.session_state["history"].append(response)


# def record_response(evt):
#     # st.session_state["response"] = evt
#     print(evt)


# def stop_cb(evt):
#     print("CLOSING on {}".format(evt))
#     st.session_state["speech_recognizer"].stop_continuous_recognition()

#     if evt.reason == speechsdk.ResultReason.RecognizedSpeech:
#         print("Recognized: {}".format(evt.text))
#     elif evt.reason == speechsdk.ResultReason.NoMatch:
#         print("No speech could be recognized: {}".format(evt.no_match_details))
#     elif evt.reason == speechsdk.ResultReason.Canceled:
#         cancellation_details = evt.cancellation_details
#         print("Speech Recognition canceled: {}".format(cancellation_details.reason))
#         if cancellation_details.reason == speechsdk.CancellationReason.Error:
#             print("Error details: {}".format(cancellation_details.error_details))
#             print("Did you set the speech resource key and region values?")


# def get_speech_recognizer():
#     Initialize Azure speech recognizer
#     speech_key = os.environ["AZURE_SPEECH_KEY"]
#     azure_region = os.environ["AZURE_REGION"]
#     speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=region)
#     speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config)

#     # Set up for automatic recognition
#     speech_recognizer.recognized.connect(
#         lambda evt: print("RECOGNIZED: {}".format(evt))
#     )
#     speech_recognizer.session_stopped.connect(stop_cb)
#     speech_recognizer.canceled.connect(stop_cb)

#     return speech_recognizer


# def get_user_input():
#     st.session_state["speech_recognizer"].start_continuous_recognition()


def main():
    # Initialize state
    if "prompt" not in st.session_state:
        st.session_state["prompt"] = prompts.DEMO_PROMPT

    if "history" not in st.session_state:
        st.session_state["history"] = []

    if "message" not in st.session_state:
        st.session_state["message"] = ""

    # if "is_recording" not in st.session_state:
    #     st.session_state["is_recording"] = False

    # if "speech_recognizer" not in st.session_state:
    #     st.session_state["speech_recognizer"] = get_speech_recognizer()

    if "form_prompt" not in st.session_state:
        st.session_state["form_prompt"] = prompts.FORM_INSTRUCTIONS

    if "agent" not in st.session_state:
        st.session_state["agent"] = OrganizerAgent()

    st.title("Demo")

    st.divider()
    new_prompt = st.text_area(label="Prompt:", value=st.session_state["prompt"])
    if st.button("Edit"):
        st.session_state["prompt"] = new_prompt
        st.session_state["history"] = []

    st.markdown(st.session_state["prompt"])

    st.divider()
    new_form_prompt = st.text_area(
        label="Form prompt:", value=st.session_state["form_prompt"]
    )
    if st.button("Edit form"):
        st.session_state["form_prompt"] = new_form_prompt

    st.write(st.session_state["form_prompt"])

    chat, voice = st.tabs(["Chat", "Voice"])

    # Text UI
    with chat:
        # Prompt user
        st.text_input(
            label="Response",
            key="message",
            label_visibility="collapsed",
            placeholder="I've been thinking about...",
            on_change=on_message_change,
        )

        # Display chat
        st.divider()
        # Display messages in reverse (i.e. most recent is closest to text input)
        num_messages = len(st.session_state["history"])
        for i in range(-1, -1 * (num_messages + 1), -1):
            msg = st.session_state["history"][i]
            is_user = i % 2 == 0  # User speaks first
            message(msg, is_user=is_user)

    with voice:
        # if st.button("Start"):
        #     # Initial recording start
        #     get_user_input()
        #     # Start recording again once response has been read
        st.write("Check back soon!")


if __name__ == "__main__":
    main()
