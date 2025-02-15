from fastapi import FastAPI, Form, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
import uvicorn

from network_security.utils.estimator import NetworkModel
from network_security.utils.utils import load_object

from helper import extract_features

app = FastAPI()
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load the trained ML model
preprocesor=load_object("final_model/preprocessor.pkl")
final_model=load_object("final_model/model.pkl")
network_model = NetworkModel(preprocessor=preprocesor,model=final_model)

# Set up templates
templates = Jinja2Templates(directory="app/templates")


@app.get("/", response_class=HTMLResponse)
async def render_home(request: Request):
    """
    Render the home page with a form for URL submission.
    """
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/analyze", response_class=HTMLResponse)
async def analyze_url(request: Request, url: str = Form(...)):
    """
    Analyze the submitted URL, extract features, and predict phishing or safe.
    """
    try:
        # Extract features
        features = extract_features(url)

        # Prepare feature values for prediction
        feature_values = [
            features.get("having_IP_Address", 0),
            features.get("URL_Length", 0),
            features.get("Shortining_Service", 0),
            features.get("having_At_Symbol", 0),
            features.get("double_slash_redirecting", 0),
            features.get("Prefix_Suffix", 0),
            features.get("having_Sub_Domain", 0),
            features.get("SSLfinal_State", 0),
            features.get("Domain_registeration_length", 0),
        ]
        
        # Fill the remaining 23 features with default values (e.g., 0)
        full_features = feature_values + [-1] * (30 - len(feature_values))

        # Convert to NumPy array for model input
        full_features_array = np.array(full_features).reshape(1, -1)

        # Predict using the ML model
        prediction = network_model.predict(full_features_array)

        result = "Phishing" if prediction[0] == 1 else "Safe"
        return templates.TemplateResponse(
            "result.html",
            {
                "request": request,
                "url": url,
                "result": result,
                "features": features,
            },
        )
    except Exception as e:
        return templates.TemplateResponse(
            "error.html", {"request": request, "message": str(e)}
        )


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
