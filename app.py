import streamlit as st
from PIL import Image
from streamlit_cropper import st_cropper
import io
import zipfile
from pathlib import Path

# ==========================================
# PAGE CONFIG
# ==========================================

st.set_page_config(
    page_title="Bulk WebP Converter",
    layout="wide"
)

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

# ==========================================
# SIDEBAR SETTINGS
# ==========================================

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

# ==========================================
# FILE UPLOADER
# ==========================================

uploaded_files = st.file_uploader(
    "Upload JPG or PNG Images",
    type=["jpg", "jpeg", "png"],
    accept_multiple_files=True
)

# ==========================================
# MAIN APP
# ==========================================

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

            # ==========================================
            # OPEN IMAGE
            # ==========================================

            image = Image.open(uploaded_file)

            st.write(
                f"Original Resolution: "
                f"{image.width} × {image.height}"
            )

            # ==========================================
            # FILE NAME INPUT
            # ==========================================

            custom_name = st.text_input(
                "Enter File Name",
                value=Path(uploaded_file.name).stem,
                key=f"name_{index}"
            )

            # ==========================================
            # IMAGE CROPPER
            # ==========================================

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

            # ==========================================
            # FINAL RESIZE
            # ==========================================

            final_img = cropped_img.resize(
                (crop_width, crop_height)
            )

            # ==========================================
            # CONVERT TO WEBP
            # ==========================================

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

            # ==========================================
            # SIZE CALCULATIONS
            # ==========================================

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

            # ==========================================
            # IMAGE PREVIEW
            # ==========================================

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

            # ==========================================
            # FILE NAME
            # ==========================================

            webp_filename = (
                custom_name.strip() + ".webp"
            )

            # ==========================================
            # DOWNLOAD BUTTON
            # ==========================================

            st.download_button(
                label=f"⬇ Download {webp_filename}",
                data=output,
                file_name=webp_filename,
                mime="image/webp",
                key=f"download_{index}"
            )

            # ==========================================
            # ADD TO ZIP
            # ==========================================

            zip_file.writestr(
                webp_filename,
                output.getvalue()
            )

    # ==========================================
    # ZIP DOWNLOAD
    # ==========================================

    zip_buffer.seek(0)

    st.divider()

    st.download_button(
        label="📦 Download All as ZIP",
        data=zip_buffer,
        file_name="converted_images.zip",
        mime="application/zip"
    )

else:

    st.info(
        "Upload one or more JPG or PNG images to begin."
    )