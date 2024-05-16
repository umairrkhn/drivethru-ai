import streamlit as st
from openai import OpenAI

# Title for the Streamlit app
st.title("DriveThru Assistant")

# Load OpenAI API key from Streamlit secrets
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Set default model and message history if not already set
if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-4o"
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# Display past conversation history
for message in st.session_state["messages"]:
    st.chat_message(message["role"], message["content"])

# Get user input and add it to message history
user_prompt = st.chat_input("Enter your message here...")
if user_prompt:
    st.session_state["messages"].append({"role": "user", "content": user_prompt})
    st.chat_message("user", user_prompt)

    # Generate assistant response using OpenAI API
    assistant_message = client.chat.completions.create(
        model=st.session_state["openai_model"],
        messages=[
            {
                "role": "system",
                "content": "You are a drivethru assistant. Repy to any greetings with 'Hi, welcome to ' + any restaurant name+ 'how can I help you today?'",
            },
            *[
                {**message} for message in st.session_state["messages"]
            ],  # Unpack messages list
        ],
        stream=True,
    )

    # Display streamlit response and update message history
    response = st.write_stream(assistant_message)
    st.session_state["messages"].append(
        {"role": "assistant", "content": response.choices[0].text}
    )
