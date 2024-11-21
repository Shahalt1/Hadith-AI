import streamlit as st
from google import generativeai as genai
import time
import chromadb
from dotenv import load_dotenv
from os import getenv

__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

load_dotenv()
api_key = getenv("GEMINI_API_KEY")
collection = chromadb.PersistentClient('vectordb').get_collection("hadith-collection")

def stream_data(response):
    for word in response.split(" "):
        yield word + " "
        time.sleep(0.05)


def generate_prompt(query):
        result = results(query)
        prompt = f"""
            The Question is {query}
            summarize the answer using the context : {result['documents'][0][0]} in plain text and formal way
        """
        return prompt

def results(query):
    result = collection.query(
        query_texts= query, 
        include=['documents', 'metadatas'],
        n_results=1
    )
    return result
    
st.title("Hadith AI")



model = genai.GenerativeModel('gemini-1.5-flash-8b', generation_config=genai.types.GenerationConfig(
    temperature=0.1,
    candidate_count=1,
    stop_sequences=None,
    max_output_tokens=1000,
    response_mime_type='text/plain')
)
chat = model.start_chat(history=[])

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if api_key :
    if prompt := st.chat_input("What is up?"):
        st.chat_message("user").markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})
        modified_prompt = generate_prompt(prompt)
        response = chat.send_message(modified_prompt)
        with st.chat_message("assistant") :
            st.write_stream(stream_data(response.text))
        st.session_state.messages.append({"role": "assistant", "content": response.text})
else:
    api_key = st.chat_input("Input API Key", )
    st.warning("Please Input Your API Key")
    
st.sidebar.markdown(
    "<h2 style='font-size:30px;'>Query Info</h2><hr>", 
    unsafe_allow_html=True
)

with st.sidebar:
    if prompt:
        result = results(prompt)
        st.markdown(f"### **User Query**")
        st.markdown(f"{prompt}")

        st.markdown(f"### **Category of Hadith**")
        st.markdown(f"{result['metadatas'][0][0]['Category']}")

        st.markdown(f"### **Title of Book**")
        st.markdown(f"{result['metadatas'][0][0]['Title']}")

        st.markdown(f"### **Link to Website**")
        st.markdown(f"[{result['metadatas'][0][0]['URL']}]({result['metadatas'][0][0]['URL']})")


genai.configure(api_key=api_key)