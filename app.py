import streamlit as st
import re
import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

# --- Initialization ---
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

# --- Templates & Config ---
template_map = {
    "Music Producer (H.N.I Beatz)": {
        "YouTube SEO": "Create a high-traffic YouTube description for {track_name} beat, optimized for {keywords}.",
        "Performance Recap": "Summarize my weekly music performance data for '{track_name}': {metrics_data}. Suggest 3 ways to improve engagement."
    },
    "Business Owner (Collective Essence)": {
        "Product Listing": "Write a compelling Etsy product description for {product_name}, focusing on handmade quality and the unique features of {materials}.",
        "Customer Service": "Draft a polite reply to customer regarding {order_number} status: {order_status}."
    }
}

# --- Utility Functions ---
def parse_with_regex(raw_text):
    patterns = {
        "track_name": r"(?:track|song|beat|title)[:=\s]+([^\"\n]+)",
        "metrics_data": r"(?:metrics|stats|data)[:=\s]+([^\"\n]+)",
        "product_name": r"(?:product|item)[:=\s]+([^\"\n]+)",
        "order_number": r"(?:order|#)[:=\s]+([^\"\n]+)"
    }
    return {k: re.search(p, raw_text, re.IGNORECASE).group(1).strip() for k, p in patterns.items() if re.search(p, raw_text, re.IGNORECASE)}

def smart_extract_with_ai(raw_text):
    if not api_key: return {}
    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = f"Extract these fields as JSON: track_name, metrics_data, product_name, order_number, order_status, keywords, materials, genre. Text: {raw_text}"
    try:
        response = model.generate_content(prompt)
        return json.loads(response.text.replace('```json', '').replace('```', ''))
    except:
        return {}

# --- UI Setup ---
st.set_page_config(page_title="Prompt Creator", layout="wide")
st.title("🚀 Multi-Purpose Prompt Creator")

# --- Dependencies Fix ---
# Add 'google-generativeai' to your requirements.txt file on GitHub as well!
# --- User Interface ---
st.write("Welcome back! Select your role and task to generate an optimized prompt.")

col1, col2 = st.columns(2)

with col1:
    identity = st.selectbox("Select Role", list(template_map.keys()))

with col2:
    task = st.selectbox("Select Task", list(template_map[identity].keys()))

raw_input = st.text_area("Paste your raw notes, stats, or information here:", height=150)

if st.button("Generate Prompt", type="primary"):
    if raw_input.strip() == "":
        st.warning("Please paste some text to generate a prompt.")
    else:
        with st.spinner("Extracting details and generating prompt..."):
            # Try to extract data using AI, fallback to Regex if needed
            extracted_data = smart_extract_with_ai(raw_input)
            if not extracted_data:
                extracted_data = parse_with_regex(raw_input)
            
            # Fetch the correct template
            template = template_map[identity][task]
            
            # Safely replace variables in the template
            final_prompt = template
            for key, value in extracted_data.items():
                final_prompt = final_prompt.replace(f"{{{key}}}", str(value))
            
            # Show the final result
            st.success("✅ Prompt Ready!")
            st.code(final_prompt, language="markdown")
            
            # Let you see what the AI found
            with st.expander("View Extracted Data"):
                st.json(extracted_data)
