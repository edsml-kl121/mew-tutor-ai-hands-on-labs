import logging
from flask import Flask, request, jsonify
import os
import function

# Set path for the model
cwd = os.path.abspath(os.path.dirname(__file__))
given_path = "model"
model_path = os.path.abspath(os.path.join(cwd, given_path))

logging.basicConfig(level=logging.DEBUG)
app = Flask(__name__)

@app.route("/", methods=['GET'])
def home():
    html = "<h3>Model Serving</h3>"
    return html.format(format)

@app.route("/predict", methods=['POST'])
def predict():
    try:
        json_payload = request.json
        instances = json_payload.get('instances', [])
        app.logger.info(f"json_payload: {instances}")
        
        # Call the predict function and capture predictions
        predictions = function.predict(instances)
        
        # Convert predictions to a JSON-serializable format
        predictions = [float(pred) for pred in predictions]
        
        app.logger.info(f"predictions: {predictions}")
        
        return jsonify({"predictions": predictions})
    
    except Exception as e:
        # Log the error and return a 500 response
        app.logger.error(f"An error occurred during prediction: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=9000, debug=True)