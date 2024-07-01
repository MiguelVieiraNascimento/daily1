import openai
import streamlit as st
import pandas as pd
import os
import shelve
import matplotlib.pyplot as plt
import io

from flask.cli import load_dotenv

load_dotenv()
with open("sytle.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.title("DAILYBOT")
USER_AVATAR = "👤"
BOT_AVATAR = "🤖"
client = openai.OpenAI()

if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"

def load_chat_history():
    with shelve.open("chat_history") as db:
        return db.get("messages", [])

def save_chat_history(messages):
    with shelve.open("chat_history") as db:
        db["messages"] = messages

# Function to create and save a plot
def create_and_save_plot(data):
    # Assuming 'data' is a DataFrame from Pandas
    fig, ax = plt.subplots()
    # Example plot (replace with your actual data and plot logic)
    data.plot(kind='bar', ax=ax)
    ax.set_title('Exemplo de Gráfico')
    ax.set_xlabel('Dias da Semana')
    ax.set_ylabel('Horas da Semana')
    # Save the plot to a BytesIO object
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    return buffer

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = load_chat_history()

# Sidebar button to clear chat history
with st.sidebar:
    if st.button("Apagar histórico"):
        st.session_state.messages = []
        save_chat_history([])

# Display chat history
for message in st.session_state.messages:
    avatar = USER_AVATAR if message["role"] == "user" else BOT_AVATAR
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# Main chat interface
if prompt := st.chat_input("Como posso ajudar?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar=USER_AVATAR):
        st.markdown(prompt)

    with st.chat_message("assistente", avatar=BOT_AVATAR):
        # Example of generating a plot based on user input (replace with your logic)
        if "gráfico" in prompt.lower():  # Example condition to generate a plot
            # Example DataFrame (replace with your actual data)
            df = pd.DataFrame({
                'Categoria': ['Segunda-Feira', 'Terça-Feira', 'Quarta-Feira'],
                'Valor': [4, 8, 10]
            })
            # Generate and save plot
            plot_buffer = create_and_save_plot(df)
            # Display the plot in Streamlit
            st.image(plot_buffer, use_column_width=True)
            response = "Aqui está um exemplo de gráfico de horas."
        else:
            # Default OpenAI chat completion logic
            response = ""
            for resp in client.chat.completions.create(
                model=st.session_state["openai_model"],
                messages=st.session_state["messages"],
                stream=True,
            ):
                response += resp.choices[0].delta.content or ""
            st.markdown(response)

        st.session_state.messages.append({"role": "assistant", "content": response})

# Save chat history after each interaction
save_chat_history(st.session_state.messages)