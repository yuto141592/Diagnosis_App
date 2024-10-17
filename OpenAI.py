import openai

# APIキーの設定
openai.api_key = ""
def openAI(symptoms):

    # GPTによる応答生成
    prompt = """
    以下の症状を有する人で考えられる疾患を、可能性の高い順に３つ教えてください。
    主な症状: {}
    体温: {}
    頭痛: {}
    喉の痛み: {}
    咳や痰: {}
    その他: {}
    感染者との接触: {}
    """.format(symptoms['main_symptom'], symptoms['temperature'], symptoms['headache'], symptoms['sore_throat'], symptoms['cough_or_sputum'], symptoms['other_symptoms'], symptoms['contact_with_infection'])

    response = openai.ChatCompletion.create(
        model = "gpt-3.5-turbo",
        messages = [
            {"role": "system", "content": "You are a doctor."},
            {"role": "user", "content": prompt}
        ],
        temperature=0
    )

    # 応答の表示
    text = response['choices'][0]['message']['content']
    return text
