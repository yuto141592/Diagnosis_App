import os
import sys
import time
from colorama import init, Fore
from OpenAI import openAI
from VOSK.VOICEVOX.voicevox import text_to_speech
from VOSK.vosk import exeVosk
from fpdf import FPDF, XPos, YPos

# coloramaの初期化（自動リセットを有効にする）
init(autoreset=True)

# ストリーミングのように文字を表示する関数
def print_streaming(text, delay=0.05, color=Fore.WHITE):
    for char in text:
        sys.stdout.write(color + char)
        sys.stdout.flush()
        time.sleep(delay)
    print()  # 最後に改行

# 患者の症状を対話形式で入力する関数
def ask_patient():
    symptoms = {}

    print_streaming("今日はどうなさいましたか？", delay=0.05, color=Fore.CYAN)
    symptoms['main_symptom'] = input(">> ")

    print_streaming("体温は何度ですか？", delay=0.05, color=Fore.CYAN)
    symptoms['temperature'] = input(">> ")

    print_streaming("熱が出たのはいつですか？", delay=0.05, color=Fore.CYAN)
    symptoms['fever_start'] = input(">> ")

    print_streaming("頭痛はありますか？", delay=0.05, color=Fore.CYAN)
    symptoms['headache'] = input(">> ")

    print_streaming("喉の痛みはありますか？", delay=0.05, color=Fore.CYAN)
    symptoms['sore_throat'] = input(">> ")

    print_streaming("咳や痰は出ますか？", delay=0.05, color=Fore.CYAN)
    symptoms['cough_or_sputum'] = input(">> ")

    print_streaming("他に気になる症状はありますか？", delay=0.05, color=Fore.CYAN)
    symptoms['other_symptoms'] = input(">> ")

    print_streaming("吐き気はありますか？", delay=0.05, color=Fore.CYAN)
    symptoms['nausea'] = input(">> ")

    print_streaming("周りにコロナやインフルエンザに感染している・していた人はいますか？", delay=0.05, color=Fore.CYAN)
    symptoms['contact_with_infection'] = input(">> ")

    return symptoms

# 症状に基づいて診断候補を推奨する関数
def suggest_diagnosis(symptoms):
    diagnosis_candidates = []

    temperature = float(symptoms['temperature'][:-1])  # 例: "38.5℃" -> 38.5
    if temperature > 38:
        diagnosis_candidates.append("新型コロナウイルス感染症")
        diagnosis_candidates.append("インフルエンザ")
    if symptoms['headache'] == "ある" and symptoms['sore_throat'] == "ある":
        diagnosis_candidates.append("風邪")
    if symptoms['cough_or_sputum'] == "でる":
        diagnosis_candidates.append("気管支炎の可能性")
    if symptoms['other_symptoms'] == "めまいがする":
        diagnosis_candidates.append("脱水症状")

    # 第1～第3候補をまとめる
    result = ""
    for i, candidate in enumerate(diagnosis_candidates[:3], start=1):
        result += f"第{i}候補：{candidate}\n"
    if len(diagnosis_candidates) < 3:
        result += "第3候補：なし\n"
    return result

# テキストファイル (.txt) 形式での出力
def create_txt(symptoms_summary, diagnosis_suggestions):
    txt_output_path = "diagnosis_result.txt"
    with open(txt_output_path, "w", encoding="utf-8") as file:
        file.write("診断結果\n")
        file.write("症状のまとめ:\n")
        file.write(symptoms_summary + "\n")
        file.write("予測される病気:\n")
        file.write(diagnosis_suggestions)
    
    return txt_output_path

# PDFの作成に画像を追加する関数
def create_pdf(symptoms_summary, diagnosis_suggestions, image_path):
    pdf = FPDF()
    pdf.add_page()

    # 日本語フォントを追加
    font_path = os.path.join(os.path.dirname(__file__), 'NotoSansJP-Regular.ttf')  # フォントファイルのパス
    if not os.path.exists(font_path):
        print(f"フォントファイルが見つかりません: {font_path}")
        return "フォントファイルが見つかりません。"

    pdf.add_font('NotoSansJP', '', font_path, uni=True)  # 日本語フォントの追加
    pdf.set_font('NotoSansJP', size=12)

    # タイトル
    pdf.cell(200, 10, text="診断結果", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')

    # 症状のまとめ
    pdf.cell(200, 10, text="症状のまとめ:", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='L')
    pdf.multi_cell(0, 10, symptoms_summary)

    # 予測される病気
    pdf.cell(200, 10, text="予測される病気:", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='L')
    pdf.multi_cell(0, 10, diagnosis_suggestions)

    # これまでの受診歴
    pdf.cell(200, 10, text="これまでの受診歴:", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='L')
    pdf.cell(0, 10, text=f"2021年 〇〇医院 胃カメラ検査", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='L')
    pdf.cell(0, 10, text=f"2021年 △△クリニック 胃カメラ検査", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='L')
    pdf.cell(0, 10, text=f"2021年 □□大学病院 心エコー検査", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='L')

    # 1行分の空白を追加
    pdf.cell(0, 10, text="", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='L')
    
    # 生体情報
    pdf.cell(200, 10, text="生体情報:", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='L')
    pdf.cell(0, 10, text=f"心拍数: 75 回/分", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='L')
    pdf.cell(0, 10, text=f"今日の歩数: 500 歩", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='L')
    
    # 1行分の空白を追加
    pdf.cell(0, 10, text="", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='L')
    

    # 画像を追加
    if image_path:
        try:
            if os.path.exists(image_path):
                pdf.cell(200, 10, text="診断に関する画像:", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='L')
                pdf.image(image_path, x=10, y=None, w=100)  # 画像を挿入
            else:
                print(f"指定された画像ファイルが存在しません: {image_path}")
        except Exception as e:
            print(f"画像の追加中にエラーが発生しました: {e}")

    # PDFをファイルとして保存
    pdf_output_path = "diagnosis_result_with_image.pdf"
    pdf.output(pdf_output_path)

    return pdf_output_path

# メイン処理
def main():
    # 患者の症状を入力
    symptoms = exeVosk()
    print(symptoms)

    text_to_speech("結果がでるまでしばらくおまちください")

    # 症状のまとめ
    symptoms_summary = (
        f"主な症状: {symptoms['main_symptom']}\n"
        f"体温: {symptoms['temperature']}\n"
        f"頭痛: {symptoms['headache']}\n"
        f"喉の痛み: {symptoms['sore_throat']}\n"
        f"咳や痰: {symptoms['cough_or_sputum']}\n"
        f"その他: {symptoms['other_symptoms']}\n"
        f"感染者との接触: {symptoms['contact_with_infection']}\n"
    )

    # 診断候補を提案
    diagnosis_suggestions = openAI(symptoms)

    # テキストファイルの作成
    txt_path = create_txt(symptoms_summary, diagnosis_suggestions)
    print(f"テキストファイルが生成されました: {txt_path}")
    print(diagnosis_suggestions)
    text_to_speech(diagnosis_suggestions)

    # PDFファイルの作成
    pdf_path = create_pdf(symptoms_summary, diagnosis_suggestions, symptoms['image_path'])
    print(f"PDFファイルが生成されました: {pdf_path}")
    


# 実行
if __name__ == "__main__":
    main()
