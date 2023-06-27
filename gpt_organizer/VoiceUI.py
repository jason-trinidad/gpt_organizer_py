import os
from threading import Event

import azure.cognitiveservices.speech as speechsdk

from gpt_organizer.OrganizerAgent import OrganizerAgent


class VoiceUI:
    def __init__(self):
        self._create_recognizer()
        self._recognized_text = []
        self._recognition_done = Event()

    # Set self._recognizer to a new recognizer
    def _create_recognizer(self):
        speech_key = os.environ["AZURE_SPEECH_KEY"]
        azure_region = os.environ["AZURE_REGION"]
        speech_config = speechsdk.SpeechConfig(
            subscription=speech_key, region=azure_region
        )
        # Test if config solves bug
        audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
        self._recognizer = speechsdk.SpeechRecognizer(
            speech_config=speech_config, audio_config=audio_config
        )

        # Set up for automatic recognition
        self._recognizer.recognized.connect(self._handle_recognition)
        self._recognizer.session_stopped.connect(self._stop_cb)
        self._recognizer.canceled.connect(self._stop_cb)

    def _handle_recognition(self, evt):
        print(evt.result.text)
        if evt.result.text[-5:].lower() == "over.":  # Code word to end recognition
            self._recognized_text.append(evt.result.text[:-5] + ".")
            self.stop_recognition()
            self._recognition_done.set()
            return

        self._recognized_text.append(evt.result.text)

    def _stop_cb(self, evt):
        print("CLOSING on {}".format(evt))

        if evt.reason == speechsdk.ResultReason.RecognizedSpeech:
            # print("Recognized: {}".format(evt.text))
            pass
        elif evt.reason == speechsdk.ResultReason.NoMatch:
            print("No speech could be recognized: {}".format(evt.no_match_details))
        elif evt.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = evt.cancellation_details
            print("Speech Recognition canceled: {}".format(cancellation_details.reason))
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                print("Error details: {}".format(cancellation_details.error_details))
                print("Did you set the speech resource key and region values?")

    def stop_recognition(self):
        self._recognizer.stop_continuous_recognition()

        # Clear recognizer
        # self._recognizer.session_stopped.disconnect_all()
        # self._recognizer.canceled.disconnect_all()
        # self._recognizer.recognized.disconnect_all()

    def get_response(self) -> str:
        self._recognizer.start_continuous_recognition()
        self._recognition_done.wait()
        self._recognition_done.clear()

        response = " ".join(self._recognized_text)
        self._recognized_text = []
        return response

    def speak(self, text):
        speech_config = speechsdk.SpeechConfig(
            subscription=os.environ["AZURE_SPEECH_KEY"],
            region=os.environ["AZURE_REGION"],
        )
        audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)
        speech_config.speech_synthesis_voice_name = "en-US-JennyNeural"

        speech_synthesizer = speechsdk.SpeechSynthesizer(
            speech_config=speech_config, audio_config=audio_config
        )

        speech_synthesis_result = speech_synthesizer.speak_text_async(text).get()

        if (
            speech_synthesis_result.reason
            == speechsdk.ResultReason.SynthesizingAudioCompleted
        ):
            print("Speech synthesized for text [{}]".format(text))
        elif speech_synthesis_result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = speech_synthesis_result.cancellation_details
            print("Speech synthesis canceled: {}".format(cancellation_details.reason))
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                if cancellation_details.error_details:
                    print(
                        "Error details: {}".format(cancellation_details.error_details)
                    )
                    print("Did you set the speech resource key and region values?")
