import requests
import simpleaudio as sa

def text_to_speech(text, speaker_id=1):
    query_payload = {"text": text, "speaker": speaker_id}
    response = requests.post("http://localhost:50021/audio_query", params=query_payload)
    query_data = response.json()

    response = requests.post("http://localhost:50021/synthesis", params={"speaker": speaker_id}, json=query_data)
    with open("output.wav", "wb") as f:
        f.write(response.content)

    wave_obj = sa.WaveObject.from_wave_file("output.wav")
    play_obj = wave_obj.play()
    play_obj.wait_done()

