import streamlit as st
import cv2
import numpy as np
from banana_ripeness_detector import analyze_banana  # Import the analysis function

# --- Streamlit Setup ---
st.set_page_config(layout="wide")
st.title("🍌 Smart Banana Ripeness Detector")
st.markdown("### Real-time Classification using Adaptive Color Analysis (HSV)")

# --- Video Capture ---
# Note: Streamlit doesn't natively handle live webcam feed for analysis easily.
# For a quick demo, we'll let the user UPLOAD an image instead.
# For a true live feed, you'd use a library like 'webrtc-streamlit'.

st.sidebar.header("Upload Image")
uploaded_file = st.sidebar.file_uploader(
    "Upload a picture of your banana to analyze:",
    type=['jpg', 'jpeg', 'png']
)

if uploaded_file is not None:
    # Read the image file and convert it to an OpenCV format (BGR)
    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    frame = cv2.imdecode(file_bytes, 1)

    # Resize for consistent processing
    frame = cv2.resize(frame, (640, 480))

    # --- Analysis ---
    result, annotated_frame = analyze_banana(frame)

    # Convert BGR to RGB for Streamlit display
    annotated_frame_rgb = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)

    # --- Display Results ---
    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("Analyzed Image (Region of Interest: Center Box)")
        st.image(annotated_frame_rgb, use_column_width=True)

    with col2:
        st.subheader("Ripeness Report")

        if result is None:
            st.error(
                "⚠️ **No Banana Detected.** Please ensure the banana is clearly visible in the center of the image.")
        else:
            ripeness = result['ripeness']
            harvest_days = result['harvest_days']

            # Use Markdown for dramatic result
            st.markdown(f"## **Ripeness: {ripeness}**")
            st.markdown(f"### Estimated Harvest: **{harvest_days}**")

            st.info(f"""
            **Details:**
            - Average Hue (H): `{result['avg_h']:.1f}`
            - Average Saturation (S): `{result['avg_s']:.1f}`
            - Average Value (V): `{result['avg_v']:.1f}`

            *The color ranges are used to classify the stage, primarily focusing on the Hue (H) channel.*
            """)

else:
    st.info("Upload an image to start the banana ripeness analysis!")