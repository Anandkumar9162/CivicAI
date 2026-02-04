import streamlit as st
import google.generativeai as genai

api_key = st.text_input("Enter Gemini API Key", type="password")

try:
    genai.configure(api_key=api_key)
    print("Searching for models...")
    # Ye code Google se puchega ki kaunse model chalenge
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"Found: {m.name}")
except Exception as e:
    print(f"Error: {e}")