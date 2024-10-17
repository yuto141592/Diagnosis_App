import copy
import multiprocessing as mp
import numpy as np
import soundcard as sc

def capture_audio_output(audio_queue: mp.Queue, # 音声認識するプロセスにデータを受け渡すためのキュー
                         capture_sec: float, # 1回のループで録音する時間
                         sample_rate: int) -> None: # サンプリング周波数
    
    num_frame: int = int(sample_rate * capture_sec)
    
    # 利用可能なマイクデバイスを確認
    microphones = sc.all_microphones(include_loopback=False)
    print("Available microphones:", microphones)

    # マイクが正しく取得されているか確認
    mic = sc.default_microphone()
    print(f"Using microphone: {mic.name}")

    # 取得したマイクを使用して録音
    with mic.recorder(samplerate=sample_rate) as mic_recorder:
        while True:
            audio = mic_recorder.record(numframes=num_frame)
            audio_queue.put(copy.copy(audio[:, 0]))
