from flask import Flask, request, jsonify, send_file
import requests
import os
import time
from threading import Timer
from jinja2 import Environment, FileSystemLoader
from xhtml2pdf import pisa

app = Flask(__name__)
UPLOADS_DIR = './uploads/'
TEMPLATES_DIR = './TEMPLATE_DIR/'
app.secret_key = "Resume_app"

os.makedirs(UPLOADS_DIR, exist_ok=True)
os.makedirs(TEMPLATES_DIR, exist_ok=True)

@app.route("/")
def home():
    return "App running successfully!", 200

@app.route("/download-cv", methods=["GET"])
def download_cv():
    token = request.headers.get("Authorization")
    
    if not token:
        return jsonify({"error": "Token not provided"}), 401  

    if token.startswith("Bearer "):
        token = token.split(" ")[1]

    node_api_url = "http://localhost:3000/api/fetch-cv"
    headers = {"Authorization": token}
    response = requests.get(node_api_url, headers=headers)

    if response.status_code != 200:
        return jsonify({"error": "Error fetching CV"}), response.status_code

    response_data = response.json()
    cv_data = response_data.get("data", {})  

    if not cv_data.get("basic_details"):
        return jsonify({"error": "CV data not found"}), 404

    candidate_name = cv_data["basic_details"].get("candidate_name", "unknown")
    pdf_filename = f"cv_{candidate_name}.pdf"
    pdf_filepath = os.path.join(UPLOADS_DIR, pdf_filename)

    # Generate PDF
    generate_pdf(cv_data, pdf_filepath)

    Timer(3600, delete_file, [pdf_filepath]).start()

    return jsonify({"file_path": pdf_filepath}), 200 

def generate_pdf(cv_data, pdf_filepath):
    env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))
    template = env.get_template("cv_template.html")  

    html_content = template.render(cv_data=cv_data)
    
    with open(pdf_filepath, "wb") as pdf_file:
        pisa.CreatePDF(html_content, dest=pdf_file)

def delete_file(filepath):
    """Deletes the generated PDF after 1 hour"""
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
            print(f"Deleted file: {filepath}")
    except Exception as e:
        print(f"Error deleting file {filepath}: {e}")

if __name__ == "__main__":
    app.run(port=5001, debug=True)