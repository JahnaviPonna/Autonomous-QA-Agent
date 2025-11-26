# streamlit_app/app.py
import streamlit as st
import requests
import json

BACKEND = "http://localhost:8000"

st.set_page_config(page_title="Autonomous QA Agent", layout="wide")
st.title("Autonomous QA Agent — Test Case & Script Generator")

if "latest_testcases" not in st.session_state:
    st.session_state["latest_testcases"] = None

# --------------------------------
# Upload Support Files
# --------------------------------
st.sidebar.header("1) Upload Assets")
uploaded_support = st.sidebar.file_uploader(
    "Upload support docs", accept_multiple_files=True
)
uploaded_html = st.sidebar.file_uploader("Upload checkout.html", type=["html", "htm"])

if st.sidebar.button("Upload files to backend"):
    results = []

    if uploaded_support:
        for f in uploaded_support:
            files = {"file": (f.name, f.getvalue(), f.type)}
            resp = requests.post(f"{BACKEND}/upload_support_doc", files=files)
            results.append(resp.json())

    if uploaded_html:
        files = {"file": (uploaded_html.name, uploaded_html.getvalue(), uploaded_html.type)}
        resp = requests.post(f"{BACKEND}/upload_checkout", files=files)
        results.append(resp.json())

    st.sidebar.write(results)

# --------------------------------
# Build KB
# --------------------------------
st.sidebar.header("2) Build Knowledge Base")
if st.sidebar.button("Build Knowledge Base"):
    resp = requests.post(f"{BACKEND}/build_kb")
    st.sidebar.write(resp.json())

# --------------------------------
# Generate Test Cases
# --------------------------------
st.header("Generate Test Cases")
query = st.text_area("Enter requirement", height=100)

if st.button("Generate Test Cases"):
    if not query.strip():
        st.error("Please enter a query!")
    else:
        resp = requests.post(
            f"{BACKEND}/generate_testcases",
            json={"query": query}    # JSON request now
        )

        try:
            out = resp.json()
            st.code(json.dumps(out, indent=2))
        except:
            st.error("Invalid backend response")

        if "testcases" in out:
            st.session_state["latest_testcases"] = out

# --------------------------------
# Select Test Case
# --------------------------------
st.header("Select Test Case")

cases = st.session_state["latest_testcases"]
selected = None

if cases and "testcases" in cases:
    ids = [tc["Test_ID"] for tc in cases["testcases"]]
    pick = st.selectbox("Test Case", ["--select--"] + ids)
    if pick != "--select--":
        selected = next(tc for tc in cases["testcases"] if tc["Test_ID"] == pick)
        st.json(selected)

else:
    st.info("Generate test cases first.")

# --------------------------------
# Generate Script
# --------------------------------
if selected and st.button("Generate Selenium Script"):
    resp = requests.post(
        f"{BACKEND}/generate_script",
        json={"testcase_json": selected}    # JSON request now
    )

    try:
        out = resp.json()
        script = out.get("script", "")
        st.code(script, language="python")
    except:
        st.error("Invalid backend response")
