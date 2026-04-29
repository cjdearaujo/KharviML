# KharviML Frontend Dashboard

This is the premium, modern frontend dashboard for the KharviML prediction API. It uses high-quality Vanilla HTML, CSS, and JS to avoid the need for Node.js or `npm` installations.

## Features
- **Premium Design**: Dark-mode ocean analytics aesthetic with glassmorphism cards and smooth interactions.
- **Dynamic Endpoints**: Predicts either Price (TL) or Catch Volume (Tonnes) based on button clicked.
- **API Status Indicator**: Automatically checks if the FastAPI backend is running.
- **Responsive**: Fully responsive grid layout for mobile and desktop screens.

## How to Run

Because of CORS (Cross-Origin Resource Sharing), you cannot simply double-click the `index.html` file to run it with the backend. You need to serve it using a local web server on port `5173`.

### 1. Start the Backend API
In one terminal, from the root of the project:
```bash
uvicorn src.api.main:app --reload --port 8000
```
*(Make sure the models are located in the `models` directory).*

### 2. Serve the Frontend
Open a **new** terminal, navigate to the `frontend` folder, and start a Python HTTP server on port `5173`:
```bash
cd frontend
python -m http.server 5173
```

### 3. Open the Dashboard
Open your web browser and go to:
[http://127.0.0.1:5173](http://127.0.0.1:5173)

You can now fill out the fish parameters and hit "Predict Price" or "Predict Catch".

## Design Choices
- **Vanilla CSS**: Used CSS Grid, Flexbox, custom properties (variables), and radial gradients.
- **Material Symbols**: Integrated Google Material Icons for clear visual indicators.
- **Inter Font**: Modern, highly readable typography.
