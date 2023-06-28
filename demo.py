import streamlit as st
from streamlit_chat import message

# import azure.cognitiveservices.speech as speechsdk

import gpt_organizer.prompts as prompts
from gpt_organizer.OrganizerAgent import OrganizerAgent
from gpt_organizer.VoiceUI import VoiceUI
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


def handle_conversation():
    st.session_state["is_conversing"] = True

    while st.session_state["is_conversing"]:
        # Play AI message
        response = st.session_state["agent"].get_response(
            st.session_state["history"],
            st.session_state["prompt"],
            st.session_state["form_prompt"],
        )
        st.session_state["history"].append(response)
        st.session_state["voice_ui"].speak(response)

        # Get user message
        message = st.session_state["voice_ui"].get_response()
        st.session_state["history"].append(message)

        print(f"App sees: {message[:7]}")
        if message[:7].lower() == "penguin":  # Code word to end
            st.session_state["is_conversing"] = False
            break


def main():
    # Initialize state
    if "prompt" not in st.session_state:
        st.session_state["prompt"] = prompts.DEMO_PROMPT

    if "history" not in st.session_state:
        st.session_state["history"] = []

    if "message" not in st.session_state:
        st.session_state["message"] = ""

    if "is_conversing" not in st.session_state:
        st.session_state["is_conversing"] = False

    if "voice_ui" not in st.session_state:
        st.session_state["voice_ui"] = VoiceUI()

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

    # chat, voice = st.tabs(["Chat", "Voice"])

    # Text UI
    # with chat:
    #     # Prompt user
    #     st.text_input(
    #         label="Response",
    #         key="message",
    #         label_visibility="collapsed",
    #         placeholder="I've been thinking about...",
    #         on_change=on_message_change,
    #     )

    #     # Display chat
    #     st.divider()
    #     # Display messages in reverse (i.e. most recent is closest to text input)
    #     if st.session_state["history"]:
    #         num_messages = len(st.session_state["history"])
    #         for i in range(-1, -1 * (num_messages + 1), -1):
    #             msg = st.session_state["history"][i]
    #             is_user = i % 2 == 0  # User speaks first
    #             message(msg, is_user=is_user)

    # with voice:

    st.divider()
    st.write("To end your turn: end your message with the word **'over.'**")
    st.write(
        "To end the conversation: say, **'Penguin, over.'**, or hit the 'End' button"
    )

    if st.button("Start"):
        st.session_state["history"] = []
        handle_conversation()

    if st.button("End"):
        st.session_state["voice_ui"].stop_recognition()
        st.session_state["is_conversing"] = False

    # Display messages in reverse (i.e. most recent is closest to text input)
    if st.session_state["history"]:
        st.write("Chat transcript:")
        num_messages = len(st.session_state["history"])
        for i in range(-1, -1 * (num_messages + 1), -1):
            msg = st.session_state["history"][i]
            is_user = i % 2 == 0
            message(msg, is_user=is_user)


if __name__ == "__main__":
    main()
