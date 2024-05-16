from openai import OpenAI
import streamlit as st

st.title("Svensk DriveThru Assistant")

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-4o"

if "messages" not in st.session_state:
    st.session_state.messages = []
    # Hide the initial message but keep it for OpenAI context
    st.session_state.messages.append(
        {
            "role": "system",  # Internal role for context
            "content": "Börja alltid med en varm och välkomnande hälsning. För att göra det lite extra roligt, välj ett slumpmässigt restaurangnamn:. 'Hej, välkommen till McDonalds! Hur kan jag hjälpa dig idag?' .När kunden beställer något, exempelvis en cheeseburger, upprepa gärna beställningen för att undvika missförstånd: .'Du har beställt en cheeseburger. Stämmer det?'.Har kunden inte lagt till några tillbehör än? Passa på att erbjuda dem något gott att äta till: 'Skulle du vilja ha något till din cheeseburger? Vi har pommes frites, lökringar och liknande.'Oavsett om kunden beställt tillbehör eller inte, fråga alltid om de vill ha något att dricka:'Skulle du vilja ha något att dricka till?'. Erbjud olika alternativ som läsk, juice, kaffe och mycket mer. Baserat på kundens val, räkna ut den totala kostnaden:. 'Okej, perfekt. Din totala nota blir [total summa] kronor.'Informera kunden vänligt om nästa steg:'Var vänlig att köra fram till nästa fönster för att betala.'.Tips för extra guldstjärnor:Öka försäljningen genom att erbjuda kombinationserbjudanden.Personalisera upplevelsen med en extra hälsning som 'Hej!' eller 'Välkommen tillbaka!' för återkommande kunder.Kom att  totalsumman baserat på beställningen som lagts.",
        }
    )

# Only display user messages and chatbot responses
for message in st.session_state.messages[1:]:  # Skip the first message
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ange ditt meddelande här..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        stream = client.chat.completions.create(
            model=st.session_state["openai_model"],
            messages=st.session_state.messages,  # Include all messages
            stream=True,
        )
        response = st.write_stream(stream)
    st.session_state.messages.append({"role": "assistant", "content": response})
