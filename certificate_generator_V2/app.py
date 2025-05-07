import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import os
import json

st.set_page_config(page_title="🎓 Certificate Generator", layout="centered")
st.title("🎓 LMDC Certificate Generator App")
st.title("|----👨‍💻 Developed by Saif Azeem---|")

TEMPLATE_DIR = "templates"
OUTPUT_DIR = "generated_certificates"
CONFIG_PATH = "certificate_config.json"
DEFAULT_FONT_PATH = "fonts/DejaVuSans.ttf"

os.makedirs(TEMPLATE_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# --- Template Upload and Selection ---
st.sidebar.subheader("📤 Upload Certificate Templates")
uploaded_templates = st.sidebar.file_uploader("Upload Templates (JPG/PNG)", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

if uploaded_templates:
    for uploaded_file in uploaded_templates:
        with open(os.path.join(TEMPLATE_DIR, uploaded_file.name), "wb") as f:
            f.write(uploaded_file.read())
    st.sidebar.success("Templates uploaded successfully! Please refresh if not visible in dropdown.")

# Load available templates
template_files = [f for f in os.listdir(TEMPLATE_DIR) if f.endswith((".jpg", ".jpeg", ".png"))]
selected_template_name = st.sidebar.selectbox("📄 Select Certificate Template", template_files)

TEMPLATE_PATH = os.path.join(TEMPLATE_DIR, selected_template_name)

try:
    cert_template = Image.open(TEMPLATE_PATH)
except Exception as e:
    st.error(f"Error loading template: {e}")
    st.stop()

# --- Certificate Text Inputs ---
st.sidebar.subheader("📝 Certificate Text Inputs")
name_input = st.sidebar.text_input("Enter Name", "Saif Azeem")
topic_input = st.sidebar.text_input("Enter Topic", 'for participating on the topic of "Python"')
date_input = st.sidebar.text_input("Enter Date", "04 May, 2025")

# Font Size & Position
st.sidebar.subheader("🎯 Text Position & Size")
col1, col2 = st.sidebar.columns(2)
with col1:
    name_x = st.sidebar.slider("Name X", 0, cert_template.width, 475)
    topic_x = st.sidebar.slider("Topic X", 0, cert_template.width, 290)
    date_x = st.sidebar.slider("Date X", 0, cert_template.width, 460)
with col2:
    name_y = st.sidebar.slider("Name Y", 0, cert_template.height, 435)
    topic_y = st.sidebar.slider("Topic Y", 0, cert_template.height, 510)
    date_y = st.sidebar.slider("Date Y", 0, cert_template.height, 585)

st.sidebar.subheader("🔠 Font Sizes & Styles")
font_size_name = st.sidebar.slider("Font Size for Name", 10, 100, 32)
font_size_topic = st.sidebar.slider("Font Size for Topic", 10, 100, 32)
font_size_date = st.sidebar.slider("Font Size for Date", 10, 100, 32)

font_color = st.sidebar.color_picker("🎨 Font Color", "#000000")

# Text styles
st.sidebar.subheader("💅 Font Text Styles")
bold_name = st.sidebar.checkbox("Bold Name")
italic_name = st.sidebar.checkbox("Italic Name")
underline_name = st.sidebar.checkbox("Underline Name")

bold_topic = st.sidebar.checkbox("Bold Topic")
italic_topic = st.sidebar.checkbox("Italic Topic")
underline_topic = st.sidebar.checkbox("Underline Topic")

bold_date = st.sidebar.checkbox("Bold Date")
italic_date = st.sidebar.checkbox("Italic Date")
underline_date = st.sidebar.checkbox("Underline Date")

# --- Logo & Signature Uploads ---
st.sidebar.subheader("🖼️ Logo Uploads")
logo1_file = st.sidebar.file_uploader("Upload Logo 1", type=["png", "jpg", "jpeg"])
logo1_x = st.sidebar.slider("Logo 1 X", 0, cert_template.width, 50)
logo1_y = st.sidebar.slider("Logo 1 Y", 0, cert_template.height, 50)
logo1_size = st.sidebar.slider("Logo 1 Size", 50, 400, 100)

logo2_file = st.sidebar.file_uploader("Upload Logo 2", type=["png", "jpg", "jpeg"])
logo2_x = st.sidebar.slider("Logo 2 X", 0, cert_template.width, 900)
logo2_y = st.sidebar.slider("Logo 2 Y", 0, cert_template.height, 50)
logo2_size = st.sidebar.slider("Logo 2 Size", 50, 400, 100)

st.sidebar.subheader("✍️ Signature Uploads")
sign1_file = st.sidebar.file_uploader("Upload Signature 1", type=["png", "jpg", "jpeg"])
sign1_x = st.sidebar.slider("Signature 1 X", 0, cert_template.width, 500)
sign1_y = st.sidebar.slider("Signature 1 Y", 0, cert_template.height, 500)
sign1_size = st.sidebar.slider("Signature 1 Size", 50, 400, 150)

sign2_file = st.sidebar.file_uploader("Upload Signature 2", type=["png", "jpg", "jpeg"])
sign2_x = st.sidebar.slider("Signature 2 X", 0, cert_template.width, 700)
sign2_y = st.sidebar.slider("Signature 2 Y", 0, cert_template.height, 500)
sign2_size = st.sidebar.slider("Signature 2 Size", 50, 400, 150)

# --- Load/Save Settings ---
if st.sidebar.button("💾 Save Settings"):
    config = {
        "positions": {
            "name": [name_x, name_y],
            "topic": [topic_x, topic_y],
            "date": [date_x, date_y]
        },
        "font_sizes": {
            "name": font_size_name,
            "topic": font_size_topic,
            "date": font_size_date
        },
        "font_color": font_color,
        "styles": {
            "name": [bold_name, italic_name, underline_name],
            "topic": [bold_topic, italic_topic, underline_topic],
            "date": [bold_date, italic_date, underline_date]
        }
    }
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f)
    st.sidebar.success("Settings saved!")

if st.sidebar.button("📂 Load Settings"):
    try:
        with open(CONFIG_PATH, "r") as f:
            config = json.load(f)
        st.experimental_rerun()
    except:
        st.sidebar.error("Could not load config.")

# --- CSV Upload ---
csv_file = st.sidebar.file_uploader("📥 Upload CSV (name, topic, date)", type=["csv"])

# --- Text Rendering with Styles ---
def draw_text(draw, pos, text, font_path, size, color, bold=False, italic=False, underline=False):
    try:
        # Try loading the custom font if available
        font = ImageFont.truetype(font_path, size)
    except IOError:
        # Fallback to default font if custom font is not found
        font = ImageFont.load_default()

    if bold:
        for offset in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            draw.text((pos[0] + offset[0], pos[1] + offset[1]), text, font=font, fill=color)
    draw.text(pos, text, font=font, fill=color)
    if underline:
        text_width = font.getlength(text)
        draw.line((pos[0], pos[1] + size + 5, pos[0] + text_width, pos[1] + size + 5), fill=color, width=2)

# --- Generate Certificate ---
def generate_certificate(name, topic, date, preview=False):
    img = cert_template.copy()
    draw = ImageDraw.Draw(img)

    draw_text(draw, (name_x, name_y), name, DEFAULT_FONT_PATH, font_size_name, font_color, bold_name, italic_name, underline_name)
    draw_text(draw, (topic_x, topic_y), topic, DEFAULT_FONT_PATH, font_size_topic, font_color, bold_topic, italic_topic, underline_topic)
    draw_text(draw, (date_x, date_y), date, DEFAULT_FONT_PATH, font_size_date, font_color, bold_date, italic_date, underline_date)

    for file, x, y, size in [(logo1_file, logo1_x, logo1_y, logo1_size), (logo2_file, logo2_x, logo2_y, logo2_size)]:
        if file:
            logo = Image.open(file).convert("RGBA").resize((size, size))
            img.paste(logo, (x, y), logo)

    for file, x, y, size in [(sign1_file, sign1_x, sign1_y, sign1_size), (sign2_file, sign2_x, sign2_y, sign2_size)]:
        if file:
            sign = Image.open(file).convert("RGBA").resize((size, size))
            img.paste(sign, (x, y), sign)

    if preview:
        return img

    output_path = os.path.join(OUTPUT_DIR, f"{name}.jpg")
    img.save(output_path)
    return output_path

# Preview the certificate
st.subheader("👁️ Live Preview of Certificate")
preview_img = generate_certificate(name_input, topic_input, date_input, preview=True)
st.image(preview_img)

# --- Certificate Download ---
if st.button("🎓 Generate Certificate"):
    certificate_path = generate_certificate(name_input, topic_input, date_input)
    with open(certificate_path, "rb") as f:
        st.download_button("📥 Download Certificate", f, file_name=os.path.basename(certificate_path), mime="image/jpeg")
