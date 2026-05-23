import streamlit as st
from PIL import Image
from streamlit_cropper import st_cropper
import io

st.set_page_config(layout="wide")

st.title("🖼 JPG/PNG Crop + WebP Converter - Shailesh")

# SETTINGS
st.sidebar.header("⚙ Settings")

quality = st.sidebar.slider(
    "WebP Quality",
    10,
    100,
    80
)

crop_width = st.sidebar.number_input(
    "Crop Width",
    value=768
)

crop_height = st.sidebar.number_input(
    "Crop Height",
    value=1152
)

uploaded_file = st.file_uploader(
    "Upload Image",
    type=["jpg", "jpeg", "png"]
)

if uploaded_file:

    image = Image.open(uploaded_file)

    st.write(f"Original Image Size: {image.width} × {image.height}")

    st.subheader("✂ Crop Image")

    # IMPORTANT FIX
    cropped_img = st_cropper(
        image,
        realtime_update=True,
        aspect_ratio=(crop_width, crop_height),
        return_type="image",
        box_color="#FF4B4B",
        should_resize_image=False
    )

    # Resize final
    final_img = cropped_img.resize(
        (crop_width, crop_height)
    )

    # Convert WEBP
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

    # Sizes
    original_size = len(uploaded_file.getvalue()) / 1024
    converted_size = len(output.getvalue()) / 1024

    # PREVIEW
    col1, col2 = st.columns(2)

    with col1:

        st.subheader("Original")

        st.image(
            image,
            width=min(image.width, 700)
        )

        st.info(
            f"""
Resolution: {image.width} × {image.height}

Size: {original_size:.2f} KB
"""
        )

    with col2:

        st.subheader("Converted")

        st.image(
            final_img,
            width=min(crop_width, 500)
        )

        st.success(
            f"""
Resolution: {crop_width} × {crop_height}

Size: {converted_size:.2f} KB
"""
        )

    # DOWNLOAD
    st.download_button(
        "⬇ Download WebP",
        data=output,
        file_name="converted.webp",
        mime="image/webp"
    )

else:
    st.info("Upload image to begin.")