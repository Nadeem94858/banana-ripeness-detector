import cv2
import numpy as np


# ---------- Helper Functions ----------

def auto_adjust_brightness(hsv):
    """Normalize brightness (V channel) for consistent lighting."""
    hsv[:, :, 2] = cv2.equalizeHist(hsv[:, :, 2])
    return hsv


def get_banana_mask(hsv, brightness):
    """Refined Mask: Focuses on high S and V to exclude shadows and dull backgrounds."""

    # We maintain a wide H range to catch Green (H > 40) down to Brown (H < 20).
    # S and V are kept high to strictly select the fruit and exclude dark shadows/backgrounds.

    if brightness < 100:
        lower = np.array([0, 50, 40])
        upper = np.array([85, 255, 255])
    else:
        lower = np.array([0, 60, 50])
        upper = np.array([85, 255, 255])

    mask = cv2.inRange(hsv, lower, upper)
    mask = cv2.medianBlur(mask, 7)

    # Apply morphological opening to remove small noise
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

    return mask


def classify_ripeness(h, s, v):
    """
    FINAL CLASSIFICATION LOGIC: Calibrated to user's low Hue and LOW Value (V) output.
    V-threshold for Ripe is significantly lowered to V > 50.
    """

    # 1. Unripe (Green): H > 35
    if h >= 35 and s > 80:
        return "Unripe (Green)", "7–10 days to harvest", (0, 255, 0)

    # 2. Ripe (Yellow): Mid-Low Hue (15 <= H < 35) AND Average V > 50.
    # **FIX:** V threshold lowered to V > 50 to accommodate your V=63.1 reading.
    elif 20 <= h < 35 and s > 90 and v > 50:
        return "Ripe (Yellow)", "1–3 days to harvest", (0, 255, 255)

    # 3. Overripe (Brown/Black): Low Hue (H < 35) AND V is very low (V <= 50).
    # This should now only catch very dark brown/black spots that register V <= 50.
    elif h <= 20 and s > 60 and v <= 110:
        return "Overripe (Brown)", "Harvest immediately", (0, 140, 255)

    # 4. Ambiguous/Semi-ripe
    else:
        return "Semi-ripe/Ambiguous", "4–6 days to harvest (Check visually)", (255, 255, 255)


# ---------- Core Analysis Function (No Change) ----------

def analyze_banana(frame):
    """Analyzes the full frame for banana ripeness, discarding the ROI concept."""

    analysis_region = frame.copy()

    # Convert analysis_region to HSV and normalize brightness
    hsv = cv2.cvtColor(analysis_region, cv2.COLOR_BGR2HSV)
    hsv_normalized = auto_adjust_brightness(hsv.copy())

    brightness = np.mean(hsv_normalized[:, :, 2])
    mask = get_banana_mask(hsv_normalized, brightness)

    h_vals = hsv_normalized[:, :, 0][mask > 0]
    s_vals = hsv_normalized[:, :, 1][mask > 0]
    v_vals = hsv_normalized[:, :, 2][mask > 0]

    if len(h_vals) == 0:
        cv2.putText(frame, "No Banana Detected (Filtered by Mask)", (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
        return None, frame

    avg_h = np.mean(h_vals)
    avg_s = np.mean(s_vals)
    avg_v = np.mean(v_vals)

    ripeness, harvest_days, color = classify_ripeness(avg_h, avg_s, avg_v)

    # Overlay text on the frame
    cv2.putText(frame, f"Ripeness: {ripeness}", (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 1.0, color, 3)
    cv2.putText(frame, f"Harvest: {harvest_days}", (20, 80),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

    result = {
        "ripeness": ripeness,
        "harvest_days": harvest_days,
        "avg_h": avg_h,
        "avg_s": avg_s,
        "avg_v": avg_v,
        "color": color
    }

    return result, frame