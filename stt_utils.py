import pyaudio
import queue
from google.cloud import speech

RATE = 16000
CHUNK = int(RATE / 10)
audio_queue = queue.Queue()

def mic_stream():
    audio_interface = pyaudio.PyAudio()
    stream = audio_interface.open(format=pyaudio.paInt16,
                                  channels=1,
                                  rate=RATE,
                                  input=True,
                                  frames_per_buffer=CHUNK)
    for _ in range(200):
        data = stream.read(CHUNK)
        audio_queue.put(data)
        yield speech.StreamingRecognizeRequest(audio_content=data)

def recognize_speech():
    speech_client = speech.SpeechClient()
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=RATE,
        language_code='en-US',
        alternative_language_codes=['hi-IN', 'kn-IN', 'ta-IN'],
    )
    streaming_config = speech.StreamingRecognitionConfig(config=config, interim_results=False)
    responses = speech_client.streaming_recognize(streaming_config, mic_stream())

    for response in responses:
        for result in response.results:
            if result.is_final:
                return result.alternatives[0].transcript
