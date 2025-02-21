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

@app.route("/download-cv", methods=["POST"])
def download_cv():
    cv_data = request.json 

    if not cv_data:
        return jsonify({"error": "CV data not provided"}), 400

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