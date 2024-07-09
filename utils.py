from openai import OpenAI
import base64
import streamlit as st

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
assistant = client.beta.assistants.retrieve(st.secrets["ASSISTANT_ID"])


def get_answer(messages):
    system_message = [
        {
            "role": "system",
            "content": "As an AI assistant working in a drive-thru at Max Burgers, your primary responsibility is to talk the customers through the process of ordering. Customer Interaction Instructions: Greet the customer politely and ask for their order. If the customer orders a single item, ask if they would like it to be a meal. If the customer orders multiple items, ask if any of them should be a meal. Whenever the customer asks for a meal, ask what kind of drink they want with the meal (assume they want medium fries which is included in the meal). Encourage the customer to look at the add-ons options on the menu.If the customer is not having a meal, ask if they would like any sides or drinks. Do not repeat the order to the customer. Keep the conversation as short as possible asking only relevant questions when necessary. Politely ask the customer to move to the next window once they end the conversation. Don't ask them to move to next window unless they themselves say thats it or that would be all or they say they are done with there order. ",
        }
    ]
    messages = system_message + messages
    response = client.chat.completions.create(model="gpt-4o", messages=messages)
    return response.choices[0].message.content


def speech_to_text(audio_data):
    with open(audio_data, "rb") as audio_file:
        transcript = client.audio.transcriptions.create(
            model="whisper-1", response_format="text", file=audio_file
        )
    return transcript


def text_to_speech(input_text):
    response = client.audio.speech.create(
        model="tts-1-hd", voice="alloy", input=input_text, speed=1.25
    )
    webm_file_path = "temp_audio_play.mp3"
    with open(webm_file_path, "wb") as f:
        response.stream_to_file(webm_file_path)
    return webm_file_path


def autoplay_audio(file_path: str):
    with open(file_path, "rb") as f:
        data = f.read()
    b64 = base64.b64encode(data).decode("utf-8")
    md = f"""
    <audio autoplay>
    <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
    </audio>
    """
    st.markdown(md, unsafe_allow_html=True)
