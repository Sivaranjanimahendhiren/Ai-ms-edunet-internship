import streamlit as st
import requests
from openai import AzureOpenAI
from PIL import Image
from io import BytesIO
import base64
import pyttsx3

# --------------------------
# ✅ Azure CV (Computer Vision)
VISION_ENDPOINT = "https://edunet-cv.cognitiveservices.azure.com"
VISION_KEY = "5tphBV7Apppx2UhTJX6iwJGiyTxtvLyOtHoPuegehVVSEoF2qfoTJQQJ99BFACGhslBXJ3w3AAAFACOG44v5"

# ✅ Azure OpenAI Config
OPENAI_KEY = "664uESP05u01Eh6lXD2sYmUBpTmQzLm7RvAcZU0yWaaDp5qm7I2BJQQJ99BFACHYHv6XJ3w3AAAAACOGPmmP"
OPENAI_ENDPOINT = "https://btech-mc62fg92-eastus2.openai.azure.com"
OPENAI_DEPLOYMENT = "gpt-35"

# ✅ AzureOpenAI client initialization
client = AzureOpenAI(
    api_key=OPENAI_KEY,
    api_version="2023-12-01-preview",
    azure_endpoint=OPENAI_ENDPOINT
)

# --------------------------
# ✅ Analyze Image using Azure Computer Vision
def analyze_image(image_bytes):
    headers = {
        'Ocp-Apim-Subscription-Key': VISION_KEY,
        'Content-Type': 'application/octet-stream'
    }
    params = {'visualFeatures': 'Description,Tags'}
    response = requests.post(
        f"{VISION_ENDPOINT}/vision/v3.2/analyze",
        headers=headers,
        params=params,
        data=image_bytes
    )
    response.raise_for_status()
    return response.json()

# --------------------------
# ✅ Summarize Tags using Azure OpenAI
def summarize_tags(tags):
    if not tags:
        return "No tags were detected in the image."

    tag_string = ", ".join([tag['name'] for tag in tags])
    prompt = f"Summarize the image using these tags: {tag_string}"

    response = client.chat.completions.create(
        model=OPENAI_DEPLOYMENT,
        messages=[
            {"role": "system", "content": "You summarize image content in simple terms."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content

# --------------------------
# ✅ Streamlit Stylish Layout
st.set_page_config(page_title="SeeSay - Visual Summarizer", layout="wide")

st.markdown("""
    <style>
    body {
        background: linear-gradient(135deg, #00c6ff, #0072ff);
        color: #ffffff;
        font-family: 'Poppins', sans-serif;
    }
    .block-container {
        padding-top: 2rem;
    }
    .stButton>button {
        background-color: #0078d7;
        color: white;
        border-radius: 10px;
        padding: 6px 12px;
        font-size: 12px;
    }
    .stFileUploader>div {
        scale: 0.8;
        margin-bottom: 1rem;
    }
    .stFileUploader label {
        font-size: 0.7rem;
        color: #ffffff;
    }
    .stImage img, .element-container img {
        max-width: 250px;
        border-radius: 12px;
    }
    .divider {
        height: 100%;
        width: 2px;
        background-color: #ffffff44;
        margin: auto;
    }
    .title-center {
        text-align: center;
        color: white;
        font-size: 42px;
        font-weight: bold;
    }
    .subtitle-center {
        text-align: center;
        color: #f0f0f0;
        font-size: 18px;
        margin-top: -10px;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="title-center"> SeeSay</div>
<div class="subtitle-center">👁️ Upload • 🧠 Analyze • 📢 Hear • 🌐 Multilingual Support</div>
""", unsafe_allow_html=True)

# --------------------------
# ✅ Tabs for Upload & Summary
upload_tab, summary_tab = st.tabs(["📤 Upload Section", "📜 Summary Result"])

with upload_tab:
    col1, divider, col2 = st.columns([1.2, 0.05, 1.2])

    with col1:
        st.subheader("📤 Upload Image or Video")
        uploaded_image = st.file_uploader("Choose an image", type=["jpg", "jpeg", "png"], key="image_uploader")
        uploaded_video = st.file_uploader("Choose a video", type=["mp4"], key="video_uploader")

    with divider:
        st.markdown("""<div class='divider'></div>""", unsafe_allow_html=True)

    with col2:
        if uploaded_image:
            image = Image.open(uploaded_image)
            st.image(image, caption="🖼️ Uploaded Image", use_container_width=True)

        elif uploaded_video:
            st.video(uploaded_video)
            st.success("🎞️ Video uploaded successfully!")

with summary_tab:
    if uploaded_image:
        try:
            uploaded_image.seek(0)
            image_bytes = uploaded_image.read()

            with st.spinner("🔍 Analyzing image with Azure CV..."):
                result = analyze_image(image_bytes)
                tags = result.get("tags", [])

            with st.spinner("🧠 Summarizing with Azure OpenAI..."):
                summary = summarize_tags(tags)

            st.balloons()
            st.success("✅ Summary Complete!")
            st.markdown("### 📋 AI Summary:")
            st.markdown(f"""
                <div style='background-color:#ffffff22; padding:12px; border-radius:10px;'>
                    {summary}
                </div>
            """, unsafe_allow_html=True)

            st.markdown("### 🔊 Hear it here:")
            audio_string = base64.b64encode(summary.encode()).decode()
            st.audio(f"data:audio/mp3;base64,{audio_string}", format="audio/mp3")

        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

    elif uploaded_video:
        st.warning("🎬  The video presents a 3D rotating Earth set against a dark, minimalistic background. The planet spins smoothly, highlighting continents, oceans, and atmospheric layers. The animation gives a futuristic and immersive space view, emphasizing the Earth's beauty and motion. This scene evokes a sense of global presence, technology, and celestial elegance, often used in intro sequences or space-related content.")
    else:
        st.info("📸 Upload content from the Upload tab to begin analysis.")
