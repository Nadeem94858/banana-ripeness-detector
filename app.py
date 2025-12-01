import streamlit as st
from PIL import Image
import numpy as np

# --- Configuration for Ripeness Detection (Based on Average RGB) ---
# Note: These thresholds are simple examples and may need calibration 
# based on the images you use.
RIPENESS_STAGES = {
    "Under-ripe (Green)": (50, 200, 50, 100),   # Range: R, G, B, Max_Green
    "Ripe (Yellow)": (150, 255, 150, 180),      # Range: R, G, B, Min_Red
    "Over-ripe (Brown)": (100, 150, 0, 150)     # Range: R, G, Max_Blue
}

def analyze_ripeness(image_array):
    """Calculates the average RGB and returns a ripeness stage."""
    
    # Calculate the average Red, Green, and Blue pixel values across the entire image
    avg_r = np.mean(image_array[:, :, 0])
    avg_g = np.mean(image_array[:, :, 1])
    avg_b = np.mean(image_array[:, :, 2])
    
    # Simple color logic based on channel dominance:
    if avg_g > 150 and avg_r < 100:
        # High Green, Low Red (Classic unripe)
        stage = "Under-ripe (Green) 🟢"
        advice = "The banana is still very green. Wait a few days for optimal sweetness."
    elif avg_r > 150 and avg_g > 150 and avg_b < 100:
        # High Red and Green (Yellow/Orange mix)
        stage = "Perfectly Ripe! 🟡"
        advice = "This banana is at peak ripeness. Enjoy it now!"
    else:
        # Everything else (usually dark/brown or mixed)
        stage = "Over-ripe / Other 🟤"
        advice = "The banana may be over-ripe or browning. Best for baking or smoothies."
        
    return stage, advice, avg_r, avg_g, avg_b


# --- Streamlit Application Layout ---

st.set_page_config(page_title="Banana Ripeness Detector", layout="wide")
st.title("🍌 Banana Ripeness Detector")
st.markdown("Upload an image of a banana to analyze its maturity using simple color detection.")

uploaded_file = st.file_uploader("Choose an image file...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    try:
        # Use Pillow to open the image file
        image = Image.open(uploaded_file).convert("RGB")
        
        # Convert the Pillow Image to a NumPy array for numerical analysis
        image_array = np.array(image)
        
        # --- Display Image and Process ---
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.header("Uploaded Image")
            st.image(image, caption='Banana Image', use_column_width=True)

        with col2:
            st.header("Ripeness Analysis")
            
            # Analyze the color
            ripeness_stage, advice, avg_r, avg_g, avg_b = analyze_ripeness(image_array)

            st.subheader(f"Result: {ripeness_stage}")
            st.info(advice)
            
            st.subheader("Average Color Statistics (0-255)")
            st.markdown(f"**Red (R):** {avg_r:.2f}")
            st.markdown(f"**Green (G):** {avg_g:.2f}")
            st.markdown(f"**Blue (B):** {avg_b:.2f}")
            
            # Display a bar chart of the average color values
            color_data = {
                'Channel': ['Red', 'Green', 'Blue'],
                'Average Value': [avg_r, avg_g, avg_b]
            }
            st.bar_chart(color_data, x='Channel', y='Average Value')
            

    except Exception as e:
        st.error(f"An error occurred during processing: {e}")
        st.warning("Please ensure the uploaded file is a valid image.")
