import streamlit as st
import pdfplumber
import requests

# Replace with your Groq API URL and API Key
groq_api_url = "https://api.groq.com/openai/v1/chat/completions"
groq_api_key = "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"

# Function to send prompt to Groq API
def query_groq(prompt):
    headers = {
        "Authorization": f"Bearer {groq_api_key}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }
    
    response = requests.post(groq_api_url, json=data, headers=headers)
    if response.status_code == 200:
        return response.json()['choices'][0]['message']['content'].strip()
    else:
        return f"Error: {response.status_code}, {response.text}"

# Extract text from uploaded PDF
def extract_text_from_pdf(uploaded_file):
    try:
        with pdfplumber.open(uploaded_file) as pdf:
            text = ""
            for page in pdf.pages:
                text += page.extract_text()
            return text.strip()
    except Exception as e:
        return f"Error reading PDF: {e}"

# Extract basic paragraph text from HTML
def extract_text_from_url(url):
    try:
        html = requests.get(url).text
        start = html.find("<p>")
        paragraphs = []
        while start != -1:
            end = html.find("</p>", start)
            if end == -1:
                break
            paragraph = html[start+3:end]
            paragraphs.append(paragraph.strip())
            start = html.find("<p>", end)
        return "\n".join(paragraphs)
    except Exception as e:
        return f"Failed to fetch article content. Error: {e}"

# ---------------- UI ----------------
st.set_page_config(page_title="AI Text Utility - Groq", layout="wide")

# Layout with space columns
left_space, main_col, right_space = st.columns([1, 4, 1])

with main_col:
    st.title("🚀 AI Text Utility using Groq")

    # Input section
    input_mode = st.radio("Choose Input Source", ["Text", "PDF", "Article URL"], horizontal=True)
    text_input = ""

    if input_mode == "Text":
        text_input = st.text_area("Enter your text here:", height=200)
    elif input_mode == "PDF":
        uploaded_pdf = st.file_uploader("Upload PDF", type="pdf")
        if uploaded_pdf:
            text_input = extract_text_from_pdf(uploaded_pdf)
    elif input_mode == "Article URL":
        url = st.text_input("Paste article URL:")
        if url:
            text_input = extract_text_from_url(url)

    if not text_input:
        st.warning("Please provide some input to continue.")
        st.stop()

    st.markdown("---")

    # Task selection
    task_option = st.radio(
        "Choose Task",
        ["Summarization", "Keyword Extraction", "Text Intent Detection", "Dual Output"],
        horizontal=True
    )

    if st.button("Run"):
        with st.spinner("Processing with Groq..."):
            if task_option == "Summarization":
                prompt = f"Summarize the following text in exactly 3 lines:\n\n{text_input}"
                output = query_groq(prompt)
                st.subheader("📝 Summary")
                st.success(output)

            elif task_option == "Keyword Extraction":
                prompt = f"Extract 5 relevant keywords from the text. Just return a comma-separated list:\n\n{text_input}"
                output = query_groq(prompt)
                st.subheader("🗝️ Keywords")
                st.info(output)

            elif task_option == "Text Intent Detection":
                prompt = f"What is the main intent of this text? Keep the answer short:\n\n{text_input}"
                output = query_groq(prompt)
                st.subheader("🧠 Text Intent")
                st.write(output)

            elif task_option == "Dual Output":
                sum_prompt = f"Summarize the following text in exactly 3 lines:\n\n{text_input}"
                kw_prompt = f"Extract 5 relevant keywords from the text. Just return a comma-separated list:\n\n{text_input}"
                summary = query_groq(sum_prompt)
                keywords = query_groq(kw_prompt)

                st.subheader("📝 Summary")
                st.success(summary)
                st.subheader("🗝️ Keywords")
                st.info(keywords)
