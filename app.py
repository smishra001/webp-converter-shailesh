
import streamlit as st
from PIL import Image
from streamlit_cropper import st_cropper
import io
import zipfile
from pathlib import Path
import json
import os
import base64

# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="Bulk WebP Converter + Prompt Manager",
    layout="wide"
)

# =====================================================
# JSON FILE
# =====================================================

PROMPT_FILE = "prompts.json"

if not os.path.exists(PROMPT_FILE):
    with open(PROMPT_FILE, "w") as f:
        json.dump([], f)

# =====================================================
# LOAD / SAVE
# =====================================================

def load_prompts():
    with open(PROMPT_FILE, "r") as f:
        return json.load(f)

def save_prompts(data):
    with open(PROMPT_FILE, "w") as f:
        json.dump(data, f, indent=4)

# =====================================================
# COPY BUTTON FUNCTION
# =====================================================

def copy_button(text, key):

    b64 = base64.b64encode(text.encode()).decode()

    copy_script = f"""
        <button onclick="
        navigator.clipboard.writeText(atob('{b64}'));
        "
        style="
            background:#111827;
            color:white;
            border:none;
            padding:8px 14px;
            border-radius:8px;
            cursor:pointer;
            width:100%;
            font-size:14px;
            margin-bottom:8px;
        ">
        📋 Copy
        </button>
    """

    st.components.v1.html(copy_script, height=45)

# =====================================================
# TABS
# =====================================================

tab1, tab2 = st.tabs([
    "🖼 Image Converter",
    "📝 Prompt Manager"
])

# =====================================================
# TAB 1 — IMAGE CONVERTER
# =====================================================

with tab1:

    st.title("🖼 Bulk JPG/PNG Crop + WebP Converter")

    st.write(
        """
Upload multiple JPG or PNG images,
crop them to exact size,
rename files,
convert to WebP,
and download individually or as ZIP.
"""
    )

    # =================================================
    # SIDEBAR SETTINGS
    # =================================================

    st.sidebar.header("⚙ Settings")

    quality = st.sidebar.slider(
        "WebP Quality",
        10,
        100,
        80
    )

    crop_width = st.sidebar.number_input(
        "Crop Width",
        min_value=100,
        max_value=5000,
        value=768
    )

    crop_height = st.sidebar.number_input(
        "Crop Height",
        min_value=100,
        max_value=5000,
        value=1152
    )

    # =================================================
    # FILE UPLOADER
    # =================================================

    uploaded_files = st.file_uploader(
        "Upload JPG or PNG Images",
        type=["jpg", "jpeg", "png"],
        accept_multiple_files=True
    )

    # =================================================
    # MAIN APP
    # =================================================

    if uploaded_files:

        zip_buffer = io.BytesIO()

        with zipfile.ZipFile(
            zip_buffer,
            "a",
            zipfile.ZIP_DEFLATED,
            False
        ) as zip_file:

            for index, uploaded_file in enumerate(uploaded_files):

                st.divider()

                st.header(f"Image {index + 1}")

                image = Image.open(uploaded_file)

                st.write(
                    f"Original Resolution: "
                    f"{image.width} × {image.height}"
                )

                custom_name = st.text_input(
                    "Enter File Name",
                    value=Path(uploaded_file.name).stem,
                    key=f"name_{index}"
                )

                st.subheader("✂ Crop Image")

                cropped_img = st_cropper(
                    image,
                    realtime_update=True,
                    aspect_ratio=(crop_width, crop_height),
                    return_type="image",
                    box_color="#FF4B4B",
                    should_resize_image=False,
                    key=f"cropper_{index}"
                )

                final_img = cropped_img.resize(
                    (crop_width, crop_height)
                )

                output = io.BytesIO()

                if final_img.mode == "RGBA":

                    final_img.save(
                        output,
                        format="WEBP",
                        quality=quality,
                        optimize=True
                    )

                else:

                    final_img.convert("RGB").save(
                        output,
                        format="WEBP",
                        quality=quality,
                        optimize=True
                    )

                output.seek(0)

                original_size = (
                    len(uploaded_file.getvalue()) / 1024
                )

                converted_size = (
                    len(output.getvalue()) / 1024
                )

                saved = original_size - converted_size

                saved_percent = (
                    saved / original_size
                ) * 100

                col1, col2 = st.columns(2)

                with col1:

                    st.subheader("Original Image")

                    st.image(
                        image,
                        width=min(image.width, 500)
                    )

                    st.info(
                        f"""
Resolution: {image.width} × {image.height}

Original Size: {original_size:.2f} KB
"""
                    )

                with col2:

                    st.subheader("Converted WebP")

                    st.image(
                        final_img,
                        width=min(crop_width, 400)
                    )

                    st.success(
                        f"""
Resolution: {crop_width} × {crop_height}

Converted Size: {converted_size:.2f} KB

Saved: {saved_percent:.1f}%
"""
                    )

                webp_filename = (
                    custom_name.strip() + ".webp"
                )

                st.download_button(
                    label=f"⬇ Download {webp_filename}",
                    data=output,
                    file_name=webp_filename,
                    mime="image/webp",
                    key=f"download_{index}"
                )

                zip_file.writestr(
                    webp_filename,
                    output.getvalue()
                )

        zip_buffer.seek(0)

        st.divider()

        st.download_button(
            label="📦 Download All as ZIP",
            data=zip_buffer,
            file_name="converted_images.zip",
            mime="application/zip"
        )

# =====================================================
# TAB 2 — PROMPT MANAGER
# =====================================================

with tab2:

    st.title("📝 Prompt Manager")

    prompts = load_prompts()

    # =================================================
    # SESSION STATE
    # =================================================

    if "edit_index" not in st.session_state:
        st.session_state.edit_index = None

    edit_data = None

    if st.session_state.edit_index is not None:
        edit_data = prompts[
            st.session_state.edit_index
        ]

    # =================================================
    # FORM
    # =================================================

    with st.form("prompt_form"):

        st.subheader("Add / Edit Prompt")

        title = st.text_input(
            "Title",
            value=edit_data["title"]
            if edit_data else ""
        )

        prompt_text = st.text_area(
            "Prompt",
            height=180,
            value=edit_data["prompt"]
            if edit_data else ""
        )

        ref_url = st.text_input(
            "Reference Image URL",
            value=edit_data["ref"]
            if edit_data else ""
        )

        submitted = st.form_submit_button(
            "💾 Save Prompt"
        )

        if submitted:

            new_data = {
                "title": title,
                "prompt": prompt_text,
                "ref": ref_url
            }

            # EDIT
            if st.session_state.edit_index is not None:

                prompts[
                    st.session_state.edit_index
                ] = new_data

                st.session_state.edit_index = None

                save_prompts(prompts)

                st.success("Prompt Updated!")

            # NEW
            else:

                prompts.append(new_data)

                save_prompts(prompts)

                st.success("Prompt Saved!")

            st.rerun()

    st.divider()

    # =================================================
    # TABLE HEADER
    # =================================================

    st.markdown("""
    <style>

    .table-header{
        background:#111827;
        color:white;
        padding:14px;
        border-radius:10px;
        font-weight:600;
        margin-bottom:12px;
    }

    .table-row{
        border:1px solid #e5e7eb;
        border-radius:12px;
        padding:15px;
        margin-bottom:14px;
        background:white;
    }

    .prompt-box{
        background:#f3f4f6;
        padding:10px;
        border-radius:8px;
        font-size:14px;
        height:120px;
        overflow:auto;
    }

    </style>
    """, unsafe_allow_html=True)

    st.subheader("📚 Saved Prompts")

    # =================================================
    # HEADER ROW
    # =================================================

    h1, h2, h3, h4 = st.columns([2, 4, 2, 2])

    with h1:
        st.markdown("### Title")

    with h2:
        st.markdown("### Prompt")

    with h3:
        st.markdown("### Image")

    with h4:
        st.markdown("### Actions")

    st.divider()

    # =================================================
    # ROWS
    # =================================================

    if len(prompts) == 0:

        st.info("No prompts saved yet.")

    else:

        for index, item in enumerate(prompts):

            c1, c2, c3, c4 = st.columns(
                [2, 4, 2, 2]
            )

            # =========================================
            # TITLE
            # =========================================

            with c1:

                st.markdown(
                    f"### {item['title']}"
                )

            # =========================================
            # PROMPT
            # =========================================

            with c2:

                st.code(
                    item["prompt"],
                    language=None
                )

            # =========================================
            # IMAGE
            # =========================================

            with c3:

                if item["ref"]:

                    image_html = f"""
                    <a href="{item['ref']}" target="_blank">
                        <img src="{item['ref']}"
                        style="
                            width:140px;
                            border-radius:10px;
                            cursor:pointer;
                            border:1px solid #ddd;
                        ">
                    </a>
                    """

                    st.markdown(
                        image_html,
                        unsafe_allow_html=True
                    )

                else:

                    st.info("No Image")

            # =========================================
            # ACTIONS
            # =========================================

            with c4:

                copy_button(
                    item["prompt"],
                    f"copy_{index}"
                )

                if st.button(
                    "✏ Edit",
                    key=f"edit_{index}",
                    use_container_width=True
                ):

                    st.session_state.edit_index = index
                    st.rerun()

                if st.button(
                    "🗑 Delete",
                    key=f"delete_{index}",
                    use_container_width=True
                ):

                    prompts.pop(index)

                    save_prompts(prompts)

                    st.success(
                        "Prompt Deleted"
                    )

                    st.rerun()

            st.divider()
