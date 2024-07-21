import re
from openai import OpenAI
import streamlit as st
import utils
import os

st.title("Drive Thru Assistant")

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
assistant = client.beta.assistants.retrieve(assistant_id=st.secrets["ASSISTANT_ID"])

if "messages" not in st.session_state:
    st.session_state.messages = []

if "thread_id" not in st.session_state:
    st.session_state.thread_id = client.beta.threads.create().id

if "order_status" not in st.session_state:
    st.session_state.order_status = ""

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("What would you like to order?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Send input to the assistant
    client.beta.threads.messages.create(
        thread_id=st.session_state.thread_id, role="user", content=prompt
    )
    run = client.beta.threads.runs.create(
        thread_id=st.session_state.thread_id, assistant_id=assistant.id
    )

    # Wait for the assistant's response
    while run.status != "completed":
        run = client.beta.threads.runs.retrieve(
            thread_id=st.session_state.thread_id, run_id=run.id
        )

    # Get the assistant's response
    messages = client.beta.threads.messages.list(thread_id=st.session_state.thread_id)
    assistant_response = messages.data[0].content[0].text.value

    # Update order status in the sidebar
    st.session_state.order_status = assistant_response

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = utils.get_answer(st.session_state.messages)
        message_placeholder.markdown(full_response)

        # Convert response to speech
        audio_file = utils.text_to_speech(full_response)
        utils.autoplay_audio(audio_file)
        os.remove(audio_file)

    st.session_state.messages.append({"role": "assistant", "content": full_response})

# Update sidebar with order status
pattern = r'【\d+†source】'
if st.session_state.order_status:
    order_status = st.session_state.order_status
    order_status = re.sub(pattern, "", order_status)
    st.sidebar.subheader("Order Status")
    st.sidebar.text(order_status)
    