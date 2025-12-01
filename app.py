import streamlit as st
import numpy as np
from skimage import io, color
import io as file_io # Required for reading the uploaded file bytes

# --- CRITICAL DEPLOYMENT STEP ---
# The logic below uses the scikit-image library, which handles image data 
# as NumPy arrays and performs color conversion without the complex 
# system dependencies required by OpenCV (cv2).

# Function to analyze the color and determine ripeness
def analyze_ripeness(image_array):
    """
    Analyzes the average Hue of the image to determine ripeness.
    Note: scikit-image normalizes the Hue channel to a range of [0.0, 1.0].
    """
    
    # 1. Convert the image array from RGB to HSV
    # (skimage.color.rgb2hsv normalizes all channels (H, S, V) to 0.0 to 1.0)
    img_hsv = color.rgb2hsv(image_array)

    # 2. Extract the HUE channel (index 0)
    hue_channel = img_hsv[:, :, 0]
    
    # Simple check: exclude black/white/gray areas (low Saturation and Value) 
    # and only consider pixels above a certain brightness/saturation.
    # We will simply calculate the mean of the whole image for this simplified app.
    mean_hue = np.mean(hue_channel)

    # 3. Ripeness Logic based on normalized Hue (0.0 to 1.0)
    # These thresholds are a simplified approximation:
    if mean_hue > 0.18:
        # High normalized Hue (e.g., 0.20 to 0.35) is Green
        ripeness = "Unripe 🟢"
        color_code = "green"
    elif mean_hue >= 0.10 and mean_hue <= 0.18:
        # Medium normalized Hue (e.g., 0.10 to 0.18) is Yellow/Ripe
        ripeness = "Perfectly Ripe! 🍌"
        color_code = "yellow"
    else:
        # Low normalized Hue (e.g., 0.0 to 0.09) is Orange/Red/Brown (Overripe)
        ripeness = "Overripe 🟤"
        color_code = "red"

    return ripeness, mean_hue, color_code

# --- Streamlit App Layout ---
st.title("🍌 Banana Ripeness Detector")

st.write(
    """
    This application uses the **scikit-image** library to analyze the color of an 
    uploaded image and estimate its ripeness based on the average Hue value.
    """
)

uploaded_file = st.file_uploader("Upload an image of a banana:", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    try:
        # Read the uploaded file into an in-memory byte stream
        bytes_data = uploaded_file.read()
        
        # Use scikit-image's io.imread to read the bytes directly into a NumPy array
        # We specify plugin='imageio' to ensure broad format compatibility
        image_array = io.imread(file_io.BytesIO(bytes_data), plugin='imageio')
        
        # Display the uploaded image
        st.image(image_array, caption='Uploaded Banana Image', use_column_width=True)
        st.write("")
        
        with st.spinner('Analyzing ripeness...'):
            ripeness_result, mean_hue_value, color_code = analyze_ripeness(image_array)
            
            st.markdown(f"### Result: **<span style='color:{color_code};'>{ripeness_result}</span>**", unsafe_allow_html=True)
            st.write(f"*(Mean Normalized Hue Value: {mean_hue_value:.4f})*")

            st.info(
                "**Note:** The color logic is based on **scikit-image's normalized Hue scale (0.0 to 1.0)**, "
                "which is why the threshold values are different from what you would use with OpenCV's 0-179 scale."
            )
            
    except Exception as e:
        st.error(f"An error occurred during image processing. Please check the image format. Error: {e}")

st.markdown("---")
st.markdown("⚠️ **Action Required:** For this code to work, you **must** update your `requirements.txt` file.")
