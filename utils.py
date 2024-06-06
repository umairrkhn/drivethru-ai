from openai import OpenAI
import base64
import streamlit as st

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def get_answer(messages):
    system_message = [
        {
            "role": "system",
            "content": "Always start with a warm and welcoming greeting. To make it a little extra fun, choose a random restaurant name:. 'Hello, welcome to McDonalds! How can I help you today?' .When the customer orders something, for example a cheeseburger, feel free to repeat the order to avoid misunderstandings: .'You have ordered a cheeseburger. Is that correct?'.Has the customer not added any accessories yet? Take the opportunity to offer them something good to eat: 'Would you like something to go with your cheeseburger? We have fries, onion rings and the like.'Regardless of whether the customer ordered side dishes or not, always ask if they want something to drink:'Would you like something to drink?'. Offer different options such as soda, juice, coffee and much more. Based on the customer's choice, calculate the total cost:. 'Okay, perfect. Your total bill will be [total amount] kronor.'Please kindly inform the customer of the next step:'Please drive to the next window to pay.'.Tip for extra gold stars:Increase sales by offering combo offers.Personalize the experience with an extra greeting like 'Hello!' or 'Welcome back!' for repeat customers.Come to the total based on the order placed.",
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
        model="tts-1", voice="alloy", input=input_text
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
