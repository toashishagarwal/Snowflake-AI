# 🌟 AxLens 
AI-Powered Chat App for Aesthetic Industry News Insight

[![Streamlit](https://img.shields.io/badge/Built%20with-Streamlit-orange?logo=streamlit&style=flat-square)](https://streamlit.io/)
[![Snowflake](https://img.shields.io/badge/Powered%20by-Snowflake-blue?logo=snowflake&style=flat-square)](https://www.snowflake.com/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Made with ❤️](https://img.shields.io/badge/Made%20with-❤️-ff69b4)](#)

> Discover insights from the Aesthetics Industry - Powered by AI and vector search

AxLens is an AI-powered Streamlit chat application that queries curated news from the aesthetics industry to provide meaningful insights. By crawling top beauty and aesthetics news sources, converting the information to PDFs, and leveraging Snowflake’s scalable data infrastructure with state-of-the-art vector embeddings, AxLens enables users to ask natural language questions and receive relevant, intelligent responses — instantly.

---

## ✨ Key Features

✅ AI Chatbot tailored for the aesthetics industry  
✅ Insights from authoritative news sources  
✅ Intelligent semantic search using vector similarity  
✅ Scalable data pipelines via Snowflake internal stages  
✅ Clean and interactive UI using Streamlit
✅ Provision to use different LLM models 

---

## 📚 How It Works

AxLens combines the power of modern data architecture and LLMs to deliver a seamless experience:

1. 📄 **PDF Upload**  
   Crawled articles in PDF format uploads to a Snowflake internal stage

2. 🧠 **Text Chunking & Embedding**  
   Uses text splitting and vectorization (e.g., OpenAI embeddings, HuggingFace) to process text for similarity search

3. 🔍 **AI-Powered Query Engine**  
   When users ask questions, AxLens performs a similarity search against the vector store, returning relevant document chunks and summarizing them via an LLM.

4. 💬 **Streamlit Chat UI**  
   Users interact using an intuitive chat interface powered by Streamlit.

---

## 🚀 Tech Stack

| Layer             | Technology                                                                 |
|------------------ |----------------------------------------------------------------------------|
| UI/Frontend       | [Streamlit](https://streamlit.io/)                                         |
| Backend/LLM       | [OpenAI](https://openai.com/) / HuggingFace Transformers                   |
| Data Platform     | [Snowflake](https://www.snowflake.com/) Internal Stage & SQL               |
| Embeddings        | OpenAI / Snowflake Arctic LLM Embeddings                                   |
| Vector Search     | Snowflake-based similarity search via Cortex Search Service                |

---

## 🖥️ Screenshot

<p align="center">
  <img src="https://github.com/toashishagarwal/Snowflake-AI/blob/main/5%20AxLens/images/demo.gif" width="800" alt="AxLens Screenshot">
</p>

---

## 🛠️ Installation & Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/axlens.git
   cd axlens
   
2. Create a virtual environment & install dependencies
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   
3. Set environment variables:
   Create a .env file and configure your keys

	```bash
   OPENAI_API_KEY=your_openai_api_key
   SNOWFLAKE_ACCOUNT=your_account
   SNOWFLAKE_USER=your_user
   SNOWFLAKE_PASSWORD=your_password
   SNOWFLAKE_WAREHOUSE=your_warehouse
   SNOWFLAKE_DATABASE=your_database
   SNOWFLAKE_SCHEMA=your_schema
   
4. Execute the ipynb once on your snowflake

5. Run the streamlit app
	```bash
	streamlit run app.py
