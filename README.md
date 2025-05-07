# WatermarkRem — Video Watermark Detection and Blurring

This project consists of a **React Native frontend** and a **Python Flask backend** that work together to detect and blur watermarks in uploaded MP4 videos.

---

## 📁 Project Structure

```
WaterMarkRem/
├── app.py                  # Flask backend server
├── watermark.py      # Watermark detection & blurring logic
├── app.tsx/                # main tsx file for frontend

```

---

## ⚙️ Backend Setup (Python)

### 1. Create and activate a virtual environment (optional but recommended)

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install flask opencv-python numpy werkzeug
```

> You may also need `scikit-image` depending on how watermark detection is implemented.

### 3. Run the server

```bash
python app.py
```

The backend will be available at `http://localhost:5001`.

---

## 📱 Frontend Setup (React Native)

### 1. Install dependencies

```bash
npm install axios react-native-document-picker
# or
yarn add axios react-native-document-picker
```

If you're using Expo:

```bash
npx expo install expo-av
```

If not using Expo:

```bash
npm install react-native-video
```

### 2. Update the upload URL

In `App.tsx` or your main component, update the Axios URL:

```ts
const response = await axios.post('http://<your-ip>:5001/upload', ...)
```

Replace `<your-ip>` with your computer’s local IP (e.g. `192.168.0.10`).

> Ensure your phone and computer are on the same Wi-Fi network if testing on a physical device.

### 3. Run the frontend

```bash
npx react-native run-android  # or run-ios
# or if using Expo
npx expo start
```

---

## ✅ Usage

1. Open the app on your phone or emulator.
2. Tap **Upload Video**.
3. Select an `.mp4` video.
4. Wait for it to be processed.
5. View the blurred output video right in the app!

---

## 🧠 Credits

Built with Flask, OpenCV, and React Native.

---

## 🐛 Troubleshooting

- Ensure the backend is running on port `5001`.
- If using iOS, make sure `App Transport Security` allows insecure HTTP (or use HTTPS).
- Check CORS issues if running frontend in browser.
