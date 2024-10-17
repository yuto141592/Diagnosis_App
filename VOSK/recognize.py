import json
import multiprocessing as mp
import numpy as np
import vosk
from VOSK.VOICEVOX.voicevox import text_to_speech

def speech_to_text(audio_queue: mp.Queue, # 録音するプロセスから音声データを貰うためのキュー
                   result_dict: dict, 
                   sample_rate: int) -> None: # サンプリング周波数
    NO_LOG: int = -1 # VOSK関連のログを出さないためのフラグ
    MODEL_PATH = "model" # モデルのあるディレクトリまでのパス
    
    vosk.SetLogLevel(NO_LOG)
    
    # 以下のようにするとモデル名を指定すると、モデルが/Users/User/.cache/vosk/（パスはWindowsの場合）になければ自動でダウンロードしてくれ、
    # さらに次回以降別のディレクトリでプログラムを実行してもモデルを移動せずにプログラムを実行することができます。
    model: vosk.Model = vosk.Model(model_name="vosk-model-ja-0.22")
    #model: vosk.Model = vosk.Model(model_path=MODEL_PATH)
    recognizer = vosk.KaldiRecognizer(model, sample_rate)
    
    print("Recognizer is ready")
    print("Output sound from a speaker or a headphone")
    print("#" * 40)

    i = 0
    questions = [
        "今日はどうなさいましたか？",
        "体温は何度ですか？",
        "熱が出たのはいつですか？",
        "頭痛はありますか？",
        "喉の痛みはありますか？",
        "咳や痰は出ますか？",
        "他に気になる症状はありますか？",
        "吐き気はありますか？",
        "周りにコロナやインフルエンザに感染している・していた人はいますか？"
    ]
    categories = [
        'main_symptom',
        'temperature',
        'fever_start',
        'headache',
        'sore_throat',
        'cough_or_sputum',
        'other_symptoms',
        'nausea',
        'contact_with_infection'
    ]

    print(questions[i])
    text_to_speech(questions[i])
    i += 1
    
    symptoms = {}
    while True:
        audio = audio_queue.get()
        # 音声データを認識に使える形に変換
        audio = map(lambda x: (x+1)/2, audio)
        audio = np.fromiter(audio, np.float16)
        audio = audio.tobytes()
        
        if recognizer.AcceptWaveform(audio): # 音声データの読み込み、話しがちょうどいい区切りの場合、1を返す
            result: json = json.loads(recognizer.Result())
            text = result["text"].replace(" ", "")
            
            if text != "":
                print(text)
                print(i)
                symptoms[categories[i - 1]] = text

                if i <= 8:
                    print(questions[i])
                    text_to_speech(questions[i])
                    
                    i += 1 
                    print(f"Symptoms: {symptoms}")  # 辞書に追加される内容の確認
                    result_dict.update(symptoms)
                    print(f"Updated result_dict: {result_dict}")  # 更新後の確認
                else:
                    result_dict.update(symptoms)  # 症状の辞書を送信
                    break
