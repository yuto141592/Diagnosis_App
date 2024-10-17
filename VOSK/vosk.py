import multiprocessing as mp
from VOSK.recognize import speech_to_text
from VOSK.record import capture_audio_output
import sounddevice as sd

def exeVosk():
    CAPTURE_SEC: int = 0.4 # 録音するプロセスが1回のループで録音する時間
    
    audio_queue: mp.Queue = mp.Queue() # 録音するプロセスと音声認識するプロセスがやり取りするためのキュー
    manager = mp.Manager()
    result_dict = manager.dict()
    sample_rate: int = int(sd.query_devices(kind="output")["default_samplerate"]) # サンプリング周波数は、システムの音声出力の周波数を利用
    stt_proc: mp.Process = mp.Process(target=speech_to_text,
                                      args=(audio_queue, result_dict, sample_rate)) # 録音するプロセスの作成
    
    print("Type Ctrl+C to stop")
    
    stt_proc.start()
    
    try:
        capture_audio_output(audio_queue=audio_queue, capture_sec=CAPTURE_SEC, sample_rate=sample_rate)

        stt_proc.join()  # プロセス終了を待つ
        print("症状:", dict(result_dict))  # Managerのdictを普通のdictに変換して出力
        return dict(result_dict)
    
    except KeyboardInterrupt:
        stt_proc.terminate()
        print("\nDone")
        print("症状:", dict(result_dict))  # Managerのdictを普通のdictに変換して出力
        return dict(result_dict)
