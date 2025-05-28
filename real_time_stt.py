import pyaudio
from six.moves import queue
from google.cloud import speech
from google.cloud import translate_v2 as translate
import sys
import re

# Audio recording parameters
RATE = 16000
CHUNK = int(RATE / 10)  # 100ms

class MicrophoneStream:
    def __init__(self, rate, chunk):
        self._rate = rate
        self._chunk = chunk
        self._buff = queue.Queue()
        self.closed = True

    def __enter__(self):
        self._audio_interface = pyaudio.PyAudio()
        self._audio_stream = self._audio_interface.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=self._rate,
            input=True,
            frames_per_buffer=self._chunk,
            stream_callback=self._fill_buffer,
        )

        self.closed = False
        return self

    def __exit__(self, type, value, traceback):
        self._audio_stream.stop_stream()
        self._audio_stream.close()
        self.closed = True
        self._buff.put(None)
        self._audio_interface.terminate()

    def _fill_buffer(self, in_data, frame_count, time_info, status_flags):
        self._buff.put(in_data)
        return None, pyaudio.paContinue

    def generator(self):
        while not self.closed:
            chunk = self._buff.get()
            if chunk is None:
                return
            data = [chunk]

            while True:
                try:
                    chunk = self._buff.get(block=False)
                    if chunk is None:
                        return
                    data.append(chunk)
                except queue.Empty:
                    break
            yield b"".join(data)

def listen_print_loop(responses, translate_client, target_languages):
    num_chars_printed = 0
    for response in responses:
        if not response.results:
            continue
        result = response.results[0]
        if not result.alternatives:
            continue
        transcript = result.alternatives[0].transcript

        # Display interim results, but with a carriage return at the end of the
        # line, so subsequent lines will overwrite them.
        #
        # If the previous result was longer than this one, we need to print
        # some extra spaces to overwrite the previous result
        overwrite_chars = " " * (num_chars_printed - len(transcript))

        if not result.is_final:
            sys.stdout.write(transcript + overwrite_chars + "\r")
            sys.stdout.flush()
            num_chars_printed = len(transcript)
        else:
            detected_language_code = result.language_code
            print(f"Transcript ({detected_language_code}): {transcript}{overwrite_chars}")

            # Translate and print for each target language
            for lang_code, lang_name in target_languages.items():
                try:
                    # If the detected language is the same as the target language, skip translation
                    if detected_language_code.split('-')[0] == lang_code:
                        print(f"(Already in {lang_name}) ") # Indicate it's already in the target language
                        continue

                    translation_result = translate_client.translate(
                        transcript, 
                        target_language=lang_code,
                        source_language=detected_language_code # Specify source language for translation
                    )
                    translated_text = translation_result["translatedText"]
                    print(f"Translation ({lang_name} - {lang_code}): {translated_text}")
                except Exception as e:
                    print(f"Error translating to {lang_name} from {detected_language_code}: {e}")

            # Exit recognition if any of the transcribed phrases could be
            # one of our keywords.
            if re.search(r"\b(exit|quit)\b", transcript, re.I):
                print("Exiting...")
                break
            num_chars_printed = 0

def main():
    client = speech.SpeechClient()
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=RATE,
        language_code="kn-IN",  # Primary language code
        alternative_language_codes=["hi-IN", "en-US", "ta-IN", "te-IN"], # Adjusted to 4 alternatives
        model="latest_long",
        enable_automatic_punctuation=True,
    )

    streaming_config = speech.StreamingRecognitionConfig(
        config=config,
        interim_results=True,
    )

    # Setup the translation client and target languages
    translate_client = translate.Client()
    target_languages = {
        "en": "English",
        "hi": "Hindi",
        "kn": "Kannada",
        "ta": "Tamil",
        "te": "Telugu",
        "ml": "Malayalam",
    }

    with MicrophoneStream(RATE, CHUNK) as stream:
        audio_generator = stream.generator()
        requests = (
            speech.StreamingRecognizeRequest(audio_content=content)
            for content in audio_generator
        )

        responses = client.streaming_recognize(streaming_config, requests)

        # Now, put the transcription responses to use.
        listen_print_loop(responses, translate_client, target_languages)

if __name__ == "__main__":
    main()
