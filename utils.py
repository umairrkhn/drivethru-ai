from openai import OpenAI
import base64
import streamlit as st

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
assistant = client.beta.assistants.retrieve(st.secrets["ASSISTANT_ID"])


def get_answer(messages):
    system_message = [
        {
            "role": "system",
            "content": "As an AI assistant working in a drive-thru at Max Burgers, your primary responsibility is to accurately handle customer orders. This includes retrieving the information for menu items and respective prices from the restaurant’s database, creating a precise list of customer's orders, and providing real-time updates every time a change is made. Customer Interaction Instructions: Greet the customer politely and ask for their order. If the customer orders a single item, ask if they would like it to be a meal. If the customer orders multiple items, ask if any of them should be a meal. Whenever the customer asks for a meal, ask what they would like from the add-ons menu (assume they can see the menu). Encourage the customer to look at the add-ons options on the menu.If the customer is not having a meal, ask if they would like any sides or drinks. Confirm the order by repeating it back to the customer after each addition or change. Politely ask the customer to move to the next window.",
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
        model="tts-1-hd", voice="alloy", input=input_text
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
