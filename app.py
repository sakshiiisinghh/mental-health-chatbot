import streamlit as st
import google.generativeai as genai
from textblob import TextBlob
import pandas as pd

# -----------------------------
# Configure Gemini API via Streamlit secrets
# -----------------------------
api_key = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=api_key)

# -----------------------------
# Functions
# -----------------------------
def generate_response(prompt):
    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
        result = model.generate_content(prompt)
        return result.text.strip()
    except Exception as e:
        return f"Error: {e}"

def analyze_sentiment(text):
    analysis = TextBlob(text)
    polarity = analysis.sentiment.polarity
    if polarity > 0.5:
        return "Very Positive", polarity
    elif 0.1 < polarity <= 0.5:
        return "Positive", polarity
    elif -0.1 <= polarity <= 0.1:
        return "Neutral", polarity
    elif -0.5 < polarity < -0.1:
        return "Negative", polarity
    else:
        return "Very Negative", polarity

def provide_coping_strategy(sentiment):
    strategies = {
        "Very Positive": "Keep up the positive vibes! Consider sharing your good mood with others.",
        "Positive": "It's great to see you're feeling positive. Keep doing what you're doing!",
        "Neutral": "Feeling neutral is okay. Consider engaging in activities you enjoy.",
        "Negative": "It seems you're feeling down. Try to take a break and do something relaxing.",
        "Very Negative": "I'm sorry to hear that you're feeling very negative. Consider talking to a friend or seeking professional help."
    }
    return strategies.get(sentiment, "Keep going, you're doing great!")

def display_disclaimer():
    st.sidebar.markdown(
        "<h2 style='color: #FF5733;'>Data Privacy Disclaimer</h2>",
        unsafe_allow_html=True
    )
    st.sidebar.markdown(
        "<span style='color: #FF5733;'>This application stores your session data temporarily during your session. "
        "Data is not saved permanently and is used solely for the chatbot experience. "
        "Avoid sharing personal or sensitive info.</span>",
        unsafe_allow_html=True
    )

def display_message(sender, message):
    if sender == "You":
        st.markdown(
            f"""
            <div style="background-color:#DCF8C6; padding:10px; border-radius:10px; margin:5px 0px; text-align:right;">
                <b>{sender}:</b> {message}
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f"""
            <div style="background-color:#F1F0F0; padding:10px; border-radius:10px; margin:5px 0px; text-align:left;">
                <b>{sender}:</b> {message}
            </div>
            """,
            unsafe_allow_html=True
        )

# -----------------------------
# Initialize session state
# -----------------------------
if 'messages' not in st.session_state:
    st.session_state['messages'] = []
if 'mood_tracker' not in st.session_state:
    st.session_state['mood_tracker'] = []

# -----------------------------
# UI: Title
# -----------------------------
st.title("Mental Health Support Chatbot")

# -----------------------------
# Chat input
# -----------------------------
with st.form(key='chat_form', clear_on_submit=True):
    user_message = st.text_input("Type your message here...")
    submit_button = st.form_submit_button(label='Send')

if submit_button and user_message:
    # Save user message
    st.session_state['messages'].append(("You", user_message))

    # Sentiment analysis
    sentiment, polarity = analyze_sentiment(user_message)
    coping_strategy = provide_coping_strategy(sentiment)

    # Generate bot response
    response = generate_response(user_message)
    st.session_state['messages'].append(("Bot", response))

    # Track mood
    st.session_state['mood_tracker'].append((user_message, sentiment, polarity))

# -----------------------------
# Display chat messages with styled bubbles
# -----------------------------
for sender, message in st.session_state['messages']:
    display_message(sender, message)

# -----------------------------
# Mood chart
# -----------------------------
if st.session_state['mood_tracker']:
    mood_data = pd.DataFrame(st.session_state['mood_tracker'], columns=["Message", "Sentiment", "Polarity"])
    st.line_chart(mood_data['Polarity'])

# -----------------------------
# Show coping strategy
# -----------------------------
if submit_button and user_message:
    st.markdown(
        f"""
        <div style="background-color:#FFF3CD; padding:10px; border-radius:10px; margin:10px 0px;">
            <b>Suggested Coping Strategy:</b> {coping_strategy}
        </div>
        """,
        unsafe_allow_html=True
    )

# -----------------------------
# Sidebar: Resources
# -----------------------------
st.sidebar.title("Resources")
st.sidebar.write("If you need immediate help, contact:")
st.sidebar.write("1. National Suicide Prevention Lifeline: 1-800-273-8255")
st.sidebar.write("2. Crisis Text Line: Text 'HELLO' to 741741")
st.sidebar.write("[More Resources](https://www.mentalhealth.gov/get-help/immediate-help)")

if st.sidebar.button("Show Session Summary"):
    st.sidebar.write("### Session Summary")
    for i, (message, sentiment, polarity) in enumerate(st.session_state['mood_tracker']):
        st.sidebar.write(f"{i + 1}. {message} - Sentiment: {sentiment} (Polarity: {polarity})")

# -----------------------------
# Disclaimer
# -----------------------------
display_disclaimer()
