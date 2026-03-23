import streamlit as st
import requests
import os

BACKEND_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Equity Research Copilot", layout="wide")

st.title("📊 AI Equity Research Copilot")
st.markdown("Analyze financial documents using AI-powered insights")

# -------------------------------
# 📁 Upload PDF Section
# -------------------------------
st.header("📁 Upload Financial Documents")

uploaded_files = st.file_uploader(
    "Upload one or more PDFs",
    type=["pdf"],
    accept_multiple_files=True
)

if uploaded_files:
    try:
        os.makedirs("data/raw", exist_ok=True)

        for uploaded_file in uploaded_files:
            file_path = os.path.join("data/raw", uploaded_file.name)

            with open(file_path, "wb") as f:
                f.write(uploaded_file.read())

            res = requests.post(
                f"{BACKEND_URL}/ingest/",
                params={"file_path": file_path}
            )

            if res.status_code == 200:
                st.success(f"✅ {uploaded_file.name} processed")
            else:
                st.error(f"❌ Error processing {uploaded_file.name}: {res.text}")

    except Exception as e:
        st.error(f"❌ Upload error: {str(e)}")

# -------------------------------
# 💬 Query Section
# -------------------------------
st.header("💬 Ask Questions")

query = st.text_input("Enter your query (e.g., Compare companies, risks, summary)")

if st.button("Analyze"):
    if not query:
        st.warning("⚠️ Please enter a question")
    else:
        try:
            with st.spinner("Analyzing..."):
                response = requests.get(
                    f"{BACKEND_URL}/query/",
                    params={"q": query}
                )

            if response.status_code == 200:
                data = response.json()

                # -------------------------------
                # 📊 Output Section
                # -------------------------------
                st.markdown("## 📌 Analysis Result")
                st.markdown("---")
                st.markdown(data.get("answer", "No response"))

                # -------------------------------
                # 📚 Sources Section
                # -------------------------------
                st.markdown("## 📚 Source Details")

                sources = data.get("sources", [])

                if sources:
                    for i, src in enumerate(sources):
                        with st.expander(f"📄 Source {i+1}: {src.get('source', 'unknown')}"):
                            st.write(f"📄 {src['source']} (Page {src.get('page', 'N/A')})")
                            st.caption(src["snippet"])
                else:
                    st.info("No sources available")

            else:
                st.error(f"❌ Backend Error: {response.text}")

        except Exception as e:
            st.error(f"❌ Connection error: {str(e)}")