import cv2
import numpy as np
from skimage import filters

def detect_watermark_robust(frame, sensitivity=0.85):
    """
    Detect watermark in unknown positions using multiple detection methods.
    
    Args:
        frame: Input video frame (BGR format)
        sensitivity: Detection sensitivity (0-1)
        
    Returns:
        List of potential watermark regions (x, y, w, h) or None
    """
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    height, width = gray.shape
    
    # Method 1: Edge density analysis
    edges = cv2.Canny(gray, 50, 150)
    edge_density = cv2.blur(edges, (30, 30)) / 255
    
    # Method 2: Local contrast analysis
    local_contrast = filters.sobel(gray)
    local_contrast = cv2.normalize(local_contrast, None, 0, 1, cv2.NORM_MINMAX)
    
    # Method 3: Frequency domain analysis (for periodic patterns)
    dft = np.fft.fft2(gray)
    dft_shift = np.fft.fftshift(dft)
    magnitude_spectrum = 20 * np.log(np.abs(dft_shift))
    magnitude_spectrum = cv2.normalize(magnitude_spectrum, None, 0, 1, cv2.NORM_MINMAX)
    
    # Combine detection methods
    combined = (edge_density + local_contrast + magnitude_spectrum) / 3
    _, thresholded = cv2.threshold((combined*255).astype(np.uint8), 
                                 int(sensitivity*255), 255, cv2.THRESH_BINARY)
    
    # Find contours of potential watermarks
    contours, _ = cv2.findContours(thresholded, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    potential_regions = []
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        
        # Filter regions by size and aspect ratio (typical watermark characteristics)
        if 20 < w < width//3 and 20 < h < height//3 and 0.2 < w/h < 5:
            # Check if region has consistent features across methods
            region_consistency = np.mean(combined[y:y+h, x:x+w])
            if region_consistency > sensitivity * 0.8:
                potential_regions.append((x, y, w, h))
    
    # Merge overlapping regions
    if len(potential_regions) > 0:
        potential_regions = merge_overlapping_regions(potential_regions)
    
    return potential_regions if potential_regions else None

def merge_overlapping_regions(regions, overlap_threshold=0.5):
    """
    Merge overlapping or nearby regions.
    """
    if not regions:
        return []
    
    # Convert to numpy array for easier manipulation
    regions = np.array(regions)
    x, y, w, h = regions[:, 0], regions[:, 1], regions[:, 2], regions[:, 3]
    right = x + w
    bottom = y + h
    
    keep = np.ones(len(regions), dtype=bool)
    
    for i in range(len(regions)):
        if not keep[i]:
            continue
            
        for j in range(i+1, len(regions)):
            if not keep[j]:
                continue
                
            # Calculate intersection area
            dx = min(right[i], right[j]) - max(x[i], x[j])
            dy = min(bottom[i], bottom[j]) - max(y[i], y[j])
            if dx > 0 and dy > 0:
                intersection = dx * dy
                area_i = w[i] * h[i]
                area_j = w[j] * h[j]
                
                # Merge if significant overlap
                if intersection > overlap_threshold * min(area_i, area_j):
                    # Merge regions
                    x[i] = min(x[i], x[j])
                    y[i] = min(y[i], y[j])
                    right_i = max(right[i], right[j])
                    bottom_i = max(bottom[i], bottom[j])
                    w[i] = right_i - x[i]
                    h[i] = bottom_i - y[i]
                    keep[j] = False
    
    return regions[keep].tolist()

def process_video_robust(input_path, output_path, blur_strength=15, sensitivity=0.85):
    """
    Process video with robust watermark detection that scans entire frames.
    """
    cap = cv2.VideoCapture(input_path)
    if not cap.isOpened():
        print("Error opening video file")
        return
    
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    # For tracking consistent watermark position across frames
    watermark_history = []
    history_length = 10
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        # Detect watermark using robust method
        potential_regions = detect_watermark_robust(frame, sensitivity)
        
        if potential_regions:
            # Use the largest region by default (or implement more sophisticated selection)
            selected_region = max(potential_regions, key=lambda r: r[2]*r[3])
            
            # Update watermark position history
            watermark_history.append(selected_region)
            if len(watermark_history) > history_length:
                watermark_history.pop(0)
            
            # Get most consistent position from history
            if len(watermark_history) >= history_length//2:
                avg_region = np.mean(watermark_history, axis=0).astype(int)
                frame = blur_watermark(frame, avg_region, blur_strength)
        
        out.write(frame)
    
    cap.release()
    out.release()
    cv2.destroyAllWindows()

# Example usage
if __name__ == "__main__":
    input_video = "with watermark Big.mp4"
    output_video = "output_video_blurred.mp4"
    
    # Adjust sensitivity higher (closer to 1) for stricter detection
    process_video_robust(input_video, output_video, sensitivity=0.9)