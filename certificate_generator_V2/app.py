import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import os
import json
import pandas as pd
from fpdf import FPDF
import io
import zipfile

# --- Setup ---
st.set_page_config(page_title="🎓 Certificate Generator", layout="centered")
st.title("🎓 LMDC Certificate Generator App")
st.title("|----👨‍💻 Developed by Saif Azeem---|")

TEMPLATE_DIR = "templates"
OUTPUT_DIR = "generated_certificates"
CONFIG_PATH = "certificate_config.json"
DEFAULT_FONT_PATH = "fonts/DejaVuSans.ttf"

os.makedirs(TEMPLATE_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# --- Template Upload ---
st.sidebar.subheader("📤 Upload Certificate Templates")
uploaded_templates = st.sidebar.file_uploader("Upload Templates (JPG/PNG)", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

if uploaded_templates:
    for uploaded_file in uploaded_templates:
        with open(os.path.join(TEMPLATE_DIR, uploaded_file.name), "wb") as f:
            f.write(uploaded_file.read())
    st.sidebar.success("Templates uploaded! Refresh if not showing.")

template_files = [f for f in os.listdir(TEMPLATE_DIR) if f.endswith((".jpg", ".jpeg", ".png"))]
selected_template_name = st.sidebar.selectbox("📄 Select Certificate Template", template_files)
TEMPLATE_PATH = os.path.join(TEMPLATE_DIR, selected_template_name)

try:
    cert_template = Image.open(TEMPLATE_PATH)
except Exception as e:
    st.error(f"Error loading template: {e}")
    st.stop()

# --- Inputs ---
st.sidebar.subheader("📝 Certificate Text Inputs")
name_input = st.sidebar.text_input("Enter Name", "Saif Azeem")
topic_input = st.sidebar.text_input("Enter Topic", 'for participating on the topic of "Python"')
date_input = st.sidebar.text_input("Enter Date", "04 May, 2025")

# --- Text Position ---
st.sidebar.subheader("🎯 Text Position & Size")
name_x = st.sidebar.slider("Name X", 0, cert_template.width, 475)
name_y = st.sidebar.slider("Name Y", 0, cert_template.height, 435)
topic_x = st.sidebar.slider("Topic X", 0, cert_template.width, 290)
topic_y = st.sidebar.slider("Topic Y", 0, cert_template.height, 510)
date_x = st.sidebar.slider("Date X", 0, cert_template.width, 460)
date_y = st.sidebar.slider("Date Y", 0, cert_template.height, 585)

font_size_name = st.sidebar.slider("Font Size (Name)", 10, 100, 32)
font_size_topic = st.sidebar.slider("Font Size (Topic)", 10, 100, 32)
font_size_date = st.sidebar.slider("Font Size (Date)", 10, 100, 32)

font_color = st.sidebar.color_picker("🎨 Font Color", "#000000")

# --- Styles ---
st.sidebar.subheader("💅 Text Styles")
bold_name = st.sidebar.checkbox("Bold Name")
italic_name = st.sidebar.checkbox("Italic Name")
underline_name = st.sidebar.checkbox("Underline Name")

bold_topic = st.sidebar.checkbox("Bold Topic")
italic_topic = st.sidebar.checkbox("Italic Topic")
underline_topic = st.sidebar.checkbox("Underline Topic")

bold_date = st.sidebar.checkbox("Bold Date")
italic_date = st.sidebar.checkbox("Italic Date")
underline_date = st.sidebar.checkbox("Underline Date")

# --- CSV Upload for Bulk ---
st.sidebar.subheader("📥 Upload CSV for Bulk")
csv_file = st.sidebar.file_uploader("CSV (name, topic, date)", type=["csv"])

# --- Helper Function to Draw Text ---
def draw_text(draw, pos, text, font_path, size, color, bold=False, italic=False, underline=False):
    try:
        font = ImageFont.truetype(font_path, size)
    except IOError:
        font = ImageFont.load_default()
    if bold:
        for offset in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            draw.text((pos[0] + offset[0], pos[1] + offset[1]), text, font=font, fill=color)
    draw.text(pos, text, font=font, fill=color)
    if underline:
        width = font.getlength(text)
        draw.line((pos[0], pos[1]+size+5, pos[0]+width, pos[1]+size+5), fill=color, width=2)

# --- Certificate Generator ---
def generate_certificate(name, topic, date, as_pdf=False):
    img = cert_template.copy()
    draw = ImageDraw.Draw(img)

    draw_text(draw, (name_x, name_y), name, DEFAULT_FONT_PATH, font_size_name, font_color, bold_name, italic_name, underline_name)
    draw_text(draw, (topic_x, topic_y), topic, DEFAULT_FONT_PATH, font_size_topic, font_color, bold_topic, italic_topic, underline_topic)
    draw_text(draw, (date_x, date_y), date, DEFAULT_FONT_PATH, font_size_date, font_color, bold_date, italic_date, underline_date)

    image_path = os.path.join(OUTPUT_DIR, f"{name}.jpg")
    img.save(image_path)

    if as_pdf:
        pdf = FPDF()
        pdf.add_page()
        pdf.image(image_path, x=10, y=10, w=190)
        pdf_path = os.path.join(OUTPUT_DIR, f"{name}.pdf")
        pdf.output(pdf_path)
        return image_path, pdf_path

    return image_path, None

# --- Live Preview ---
st.subheader("👁️ Live Preview")
preview_img = cert_template.copy()
draw = ImageDraw.Draw(preview_img)
draw_text(draw, (name_x, name_y), name_input, DEFAULT_FONT_PATH, font_size_name, font_color, bold_name, italic_name, underline_name)
draw_text(draw, (topic_x, topic_y), topic_input, DEFAULT_FONT_PATH, font_size_topic, font_color, bold_topic, italic_topic, underline_topic)
draw_text(draw, (date_x, date_y), date_input, DEFAULT_FONT_PATH, font_size_date, font_color, bold_date, italic_date, underline_date)
st.image(preview_img)

# --- Generate for Single ---
if st.button("🎓 Generate Single Certificate"):
    img_path, pdf_path = generate_certificate(name_input, topic_input, date_input, as_pdf=True)

    with open(img_path, "rb") as img_file:
        st.download_button("📷 Download Image", img_file, file_name=os.path.basename(img_path), mime="image/jpeg")

    with open(pdf_path, "rb") as pdf_file:
        st.download_button("📄 Download PDF", pdf_file, file_name=os.path.basename(pdf_path), mime="application/pdf")

# --- Bulk Generate ---
if csv_file and st.button("📚 Generate Certificates in Bulk"):
    df = pd.read_csv(csv_file)
    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, "w") as zip_file:
        for _, row in df.iterrows():
            name, topic, date = row["name"], row["topic"], row["date"]
            img_path, pdf_path = generate_certificate(name, topic, date, as_pdf=True)

            zip_file.write(img_path, os.path.basename(img_path))
            zip_file.write(pdf_path, os.path.basename(pdf_path))

    st.success(f"Generated {len(df)} certificates!")
    st.download_button("📦 Download ZIP (PDF + JPG)", data=zip_buffer.getvalue(), file_name="certificates.zip", mime="application/zip")
