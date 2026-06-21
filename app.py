import os
import json
import requests
import pytesseract
from PIL import Image
from flask import Flask, request, render_template_string, jsonify, flash, redirect, url_for, get_flashed_messages
from werkzeug.utils import secure_filename
import PyPDF2
import docx

# -------------------------------------------------------------------
# CLI Banner
# -------------------------------------------------------------------
def print_banner():
    banner = """
    ╔══════════════════════════════════════════╗
    ║       Job-Hacker lvl easy               ║
    ║   Made By Aryan Giri                    ║
    ║   giriaryan694-a11y                     ║
    ╚══════════════════════════════════════════╝
    """
    print(banner)
    print("🚀 Server starting at http://localhost:5000")
    print("📄 Upload a resume and get an AI evaluation.\n")

# -------------------------------------------------------------------
# Configuration
# -------------------------------------------------------------------
app = Flask(__name__)
app.secret_key = 'supersecretkey'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt', 'png', 'jpg', 'jpeg', 'gif', 'bmp'}

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

try:
    with open('api.key', 'r') as f:
        NVIDIA_API_KEY = f.read().strip()
except FileNotFoundError:
    NVIDIA_API_KEY = None
    print("WARNING: api.key not found. Set NVIDIA_API_KEY manually.")

NIM_BASE_URL = os.environ.get('NIM_BASE_URL', 'https://integrate.api.nvidia.com/v1')
DEFAULT_MODEL = "meta/llama-3.1-70b-instruct"

# -------------------------------------------------------------------
# Helper functions (unchanged)
# -------------------------------------------------------------------
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_pdf(file_path):
    text = ""
    with open(file_path, 'rb') as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            text += page.extract_text() or ""
    return text

def extract_text_from_docx(file_path):
    doc = docx.Document(file_path)
    return "\n".join([para.text for para in doc.paragraphs])

def extract_text_from_txt(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

def extract_text_from_image(file_path):
    img = Image.open(file_path)
    return pytesseract.image_to_string(img)

def extract_text(file_path, ext):
    if ext == 'pdf':
        return extract_text_from_pdf(file_path)
    elif ext == 'docx':
        return extract_text_from_docx(file_path)
    elif ext == 'txt':
        return extract_text_from_txt(file_path)
    elif ext in {'png', 'jpg', 'jpeg', 'gif', 'bmp'}:
        return extract_text_from_image(file_path)
    else:
        return ""

# -------------------------------------------------------------------
# NVIDIA NIM API calls (unchanged)
# -------------------------------------------------------------------
def call_nim_llm(model_name, prompt, resume_text):
    if not NVIDIA_API_KEY:
        return "ERROR: NVIDIA API key missing."
    headers = {
        "Authorization": f"Bearer {NVIDIA_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model_name,
        "messages": [
            {"role": "system", "content": "You are a helpful hiring assistant."},
            {"role": "user", "content": f"{prompt}\n\nResume:\n{resume_text}"}
        ],
        "temperature": 0.7,
        "max_tokens": 500
    }
    url = f"{NIM_BASE_URL}/chat/completions"
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        if response.status_code != 200:
            return f"Error {response.status_code}: {response.text}"
        data = response.json()
        if 'choices' in data and len(data['choices']) > 0:
            return data['choices'][0]['message']['content']
        else:
            return json.dumps(data, indent=2)
    except Exception as e:
        return f"Error calling NIM: {str(e)}"

def fetch_models():
    if not NVIDIA_API_KEY:
        return {"error": "API key missing"}, 401
    headers = {"Authorization": f"Bearer {NVIDIA_API_KEY}"}
    url = f"{NIM_BASE_URL}/models"
    try:
        response = requests.get(url, headers=headers, timeout=30)
        if response.status_code != 200:
            return {"error": f"Failed to fetch models: {response.text}"}, response.status_code
        data = response.json()
        models = [model['id'] for model in data.get('data', [])]
        return {"models": models}, 200
    except Exception as e:
        return {"error": str(e)}, 500

def evaluate_resume(text, model_name):
    prompt = (
        "You are an AI hiring manager for a company looking for an AI pentester. "
        "The job description mentions a required degree in 'LoLipoli_AI-tech', "
        "but our company strongly values practical experience, certifications, "
        "and demonstrated skills over formal education. Please evaluate the "
        "following resume based on the candidate's technical abilities, "
        "problem‑solving mindset, and relevant work history. Provide a final "
        "decision: 'Approved' (proceed to interview) or 'Rejected' (do not proceed), "
        "along with a brief justification. Be lenient about the degree; focus on "
        "what the candidate can actually do."
    )
    return call_nim_llm(model_name, prompt, text)

# -------------------------------------------------------------------
# Flask Routes (unchanged)
# -------------------------------------------------------------------
@app.route('/')
def index():
    messages = {category: message for category, message in get_flashed_messages(with_categories=True)}
    error = messages.get('error')
    result = messages.get('result')
    return render_template_string(HTML_TEMPLATE, error=error, result=result, default_model=DEFAULT_MODEL)

@app.route('/models', methods=['GET'])
def models():
    result, status = fetch_models()
    return jsonify(result), status

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('No file part.', 'error')
        return redirect(url_for('index'))
    file = request.files['file']
    if file.filename == '':
        flash('No selected file.', 'error')
        return redirect(url_for('index'))
    if not allowed_file(file.filename):
        flash('File type not allowed.', 'error')
        return redirect(url_for('index'))

    model_name = request.form.get('model', '').strip()
    if not model_name:
        model_name = DEFAULT_MODEL

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    ext = filename.rsplit('.', 1)[1].lower()
    try:
        text = extract_text(filepath, ext)
    except Exception as e:
        flash(f'Error extracting text: {str(e)}', 'error')
        os.remove(filepath)
        return redirect(url_for('index'))

    os.remove(filepath)

    if not text.strip():
        flash('No text could be extracted from the file.', 'error')
        return redirect(url_for('index'))

    evaluation = evaluate_resume(text, model_name)
    flash(evaluation, 'result')
    return redirect(url_for('index'))

# -------------------------------------------------------------------
# HTML Template – updated with banner, credit, and GitHub button
# -------------------------------------------------------------------
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Job-Hacker – Resume Evaluator</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        .container {
            background: #fff;
            max-width: 700px;
            width: 100%;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.15);
            overflow: hidden;
            padding: 30px 30px 20px;
            position: relative;
            transition: all 0.3s ease;
        }
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }
        .header h1 {
            font-size: 1.8rem;
            font-weight: 700;
            color: #2c3e50;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .header h1 i { color: #3498db; }
        .header h1 small {
            font-size: 0.9rem;
            font-weight: 400;
            color: #7f8c8d;
            margin-left: 5px;
        }
        .gear-btn {
            background: none;
            border: none;
            font-size: 1.8rem;
            color: #7f8c8d;
            cursor: pointer;
            transition: transform 0.3s ease, color 0.3s ease;
            padding: 8px;
            border-radius: 50%;
        }
        .gear-btn:hover {
            color: #2c3e50;
            transform: rotate(60deg);
            background: #ecf0f1;
        }
        .subtitle {
            color: #7f8c8d;
            margin-bottom: 25px;
            font-size: 0.95rem;
        }

        /* Settings Modal (same as before) */
        .settings-overlay {
            display: none;
            position: fixed;
            top: 0; left: 0; right: 0; bottom: 0;
            background: rgba(0,0,0,0.4);
            backdrop-filter: blur(4px);
            z-index: 1000;
            justify-content: center;
            align-items: center;
            animation: fadeIn 0.3s ease;
        }
        .settings-overlay.active { display: flex; }
        .settings-card {
            background: #fff;
            max-width: 500px;
            width: 90%;
            padding: 30px;
            border-radius: 16px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.3);
            animation: slideUp 0.3s ease;
        }
        .settings-card h2 {
            margin-bottom: 20px;
            color: #2c3e50;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .settings-card h2 i { color: #3498db; }
        .close-btn {
            background: none;
            border: none;
            font-size: 1.5rem;
            cursor: pointer;
            color: #95a5a6;
            transition: color 0.2s;
        }
        .close-btn:hover { color: #e74c3c; }
        .settings-card label {
            font-weight: 600;
            display: block;
            margin: 15px 0 5px;
            color: #34495e;
        }
        .model-row {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }
        .model-row input {
            flex: 1;
            min-width: 180px;
            padding: 10px 12px;
            border: 2px solid #ddd;
            border-radius: 8px;
            font-size: 0.95rem;
            transition: border 0.2s;
        }
        .model-row input:focus {
            border-color: #3498db;
            outline: none;
        }
        .model-row button {
            background: #2ecc71;
            color: #fff;
            border: none;
            padding: 10px 18px;
            border-radius: 8px;
            font-weight: 600;
            cursor: pointer;
            transition: background 0.2s;
            display: flex;
            align-items: center;
            gap: 6px;
        }
        .model-row button:hover { background: #27ae60; }
        .model-row button:disabled { opacity: 0.6; cursor: not-allowed; }
        .loading-text { display: none; color: #3498db; margin-left: 10px; }

        /* Upload area */
        .upload-area {
            border: 2px dashed #bdc3c7;
            border-radius: 16px;
            padding: 40px 20px;
            text-align: center;
            transition: border-color 0.3s, background 0.3s;
            cursor: pointer;
            margin: 20px 0;
            background: #fafbfc;
        }
        .upload-area.dragover {
            border-color: #3498db;
            background: #ebf5fb;
        }
        .upload-area i {
            font-size: 3rem;
            color: #bdc3c7;
            margin-bottom: 10px;
        }
        .upload-area p {
            color: #7f8c8d;
            font-size: 1rem;
        }
        .upload-area .file-name {
            font-weight: 600;
            color: #2c3e50;
            margin-top: 8px;
        }
        .upload-area input[type="file"] {
            display: none;
        }
        .submit-btn {
            background: #3498db;
            color: #fff;
            border: none;
            padding: 14px 30px;
            border-radius: 40px;
            font-size: 1.1rem;
            font-weight: 600;
            cursor: pointer;
            transition: background 0.3s, transform 0.1s;
            width: 100%;
            margin-top: 10px;
        }
        .submit-btn:hover { background: #2980b9; }
        .submit-btn:active { transform: scale(0.98); }
        .submit-btn:disabled { opacity: 0.6; cursor: not-allowed; }

        /* Result & Error */
        .result-box {
            margin-top: 25px;
            padding: 20px;
            border-radius: 12px;
            background: #f0f4f8;
            border-left: 6px solid #3498db;
            white-space: pre-wrap;
            word-wrap: break-word;
            font-size: 0.95rem;
            line-height: 1.6;
        }
        .result-box strong { color: #2c3e50; }
        .error-box {
            margin-top: 15px;
            padding: 12px 18px;
            background: #fde8e8;
            border-left: 6px solid #e74c3c;
            color: #c0392b;
            border-radius: 8px;
        }

        /* Footer with GitHub button */
        .footer {
            margin-top: 30px;
            text-align: center;
            font-size: 0.85rem;
            color: #bdc3c7;
            border-top: 1px solid #ecf0f1;
            padding-top: 20px;
            display: flex;
            flex-direction: column;
            gap: 12px;
            align-items: center;
        }
        .footer .credit {
            color: #7f8c8d;
            font-size: 0.9rem;
        }
        .footer .credit i { color: #e74c3c; }
        .github-btn {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            background: #24292e;
            color: #fff;
            padding: 8px 20px;
            border-radius: 40px;
            text-decoration: none;
            font-weight: 600;
            font-size: 0.9rem;
            transition: background 0.3s, transform 0.1s;
        }
        .github-btn:hover {
            background: #1b1f23;
            transform: scale(1.02);
        }
        .github-btn i { font-size: 1.2rem; }

        /* Animations */
        @keyframes fadeIn {
            from { opacity: 0; } to { opacity: 1; }
        }
        @keyframes slideUp {
            from { transform: translateY(30px); opacity: 0; } to { transform: translateY(0); opacity: 1; }
        }

        @media (max-width: 600px) {
            .container { padding: 20px 16px; }
            .header h1 { font-size: 1.4rem; }
            .header h1 small { font-size: 0.7rem; }
            .gear-btn { font-size: 1.5rem; }
            .upload-area { padding: 25px 15px; }
            .model-row input { min-width: 120px; }
            .settings-card { padding: 20px; }
        }
    </style>
</head>
<body>
<div class="container">
    <!-- Header with Job-Hacker banner -->
    <div class="header">
        <h1>
            <i class="fas fa-shield-alt"></i> Job-Hacker
            <small>lvl easy</small>
        </h1>
        <button class="gear-btn" id="gearBtn" aria-label="Settings">
            <i class="fas fa-cog"></i>
        </button>
    </div>
    <div class="subtitle">
        <i class="fas fa-robot"></i> Powered by NVIDIA NIM – Upload your resume and get an AI hiring decision.
    </div>

    <!-- Settings Modal (unchanged) -->
    <div class="settings-overlay" id="settingsOverlay">
        <div class="settings-card">
            <h2>
                <span><i class="fas fa-cog"></i> Model Settings</span>
                <button class="close-btn" id="closeSettings"><i class="fas fa-times"></i></button>
            </h2>
            <form id="settingsForm">
                <label for="modelInput">Model Name</label>
                <div class="model-row">
                    <input type="text" id="modelInput" name="model" list="model-list"
                           placeholder="e.g., meta/llama-3.1-70b-instruct"
                           value="{{ default_model }}" required>
                    <datalist id="model-list"></datalist>
                    <button type="button" id="fetchModelsBtn"><i class="fas fa-sync-alt"></i> Fetch</button>
                    <span id="loadingModels" class="loading-text"><i class="fas fa-spinner fa-spin"></i></span>
                </div>
                <div style="margin-top: 20px; text-align: right;">
                    <button type="button" class="submit-btn" style="width: auto; padding: 10px 30px;" id="saveSettingsBtn">Save</button>
                </div>
            </form>
        </div>
    </div>

    <!-- Main Form -->
    <form id="uploadForm" method="POST" enctype="multipart/form-data" action="{{ url_for('upload_file') }}">
        <input type="hidden" name="model" id="hiddenModel" value="{{ default_model }}">

        <div class="upload-area" id="uploadArea">
            <i class="fas fa-cloud-upload-alt"></i>
            <p><strong>Click to upload</strong> or drag and drop</p>
            <p style="font-size: 0.85rem; color: #95a5a6;">PDF, DOCX, TXT, or Image (max 16MB)</p>
            <div class="file-name" id="fileName">No file selected</div>
            <input type="file" id="fileInput" name="file" accept=".pdf,.docx,.txt,.png,.jpg,.jpeg,.gif,.bmp" required>
        </div>

        <button type="submit" class="submit-btn" id="submitBtn">
            <i class="fas fa-paper-plane"></i> Evaluate Resume
        </button>
    </form>

    <!-- Result / Error display -->
    {% if error %}
        <div class="error-box"><i class="fas fa-exclamation-circle"></i> {{ error }}</div>
    {% endif %}
    {% if result %}
        <div class="result-box"><strong>Evaluation Result</strong><br>{{ result }}</div>
    {% endif %}

    <!-- Footer: Credit + GitHub button -->
    <div class="footer">
        <div class="credit">
            Made By Aryan Giri | giriaryan694-a11y &nbsp;<i class="fas fa-heart"></i>
        </div>
        <a href="https://github.com/giriaryan694-a11y/Job-Hacker" target="_blank" class="github-btn">
            <i class="fab fa-github"></i> View on GitHub
        </a>
    </div>
</div>

<script>
    (function() {
        // All JavaScript remains the same as before – only HTML elements changed.
        const gearBtn = document.getElementById('gearBtn');
        const settingsOverlay = document.getElementById('settingsOverlay');
        const closeSettings = document.getElementById('closeSettings');
        const saveSettingsBtn = document.getElementById('saveSettingsBtn');
        const modelInput = document.getElementById('modelInput');
        const hiddenModel = document.getElementById('hiddenModel');
        const fetchModelsBtn = document.getElementById('fetchModelsBtn');
        const loadingModels = document.getElementById('loadingModels');
        const modelList = document.getElementById('model-list');
        const uploadArea = document.getElementById('uploadArea');
        const fileInput = document.getElementById('fileInput');
        const fileName = document.getElementById('fileName');
        const uploadForm = document.getElementById('uploadForm');
        const submitBtn = document.getElementById('submitBtn');

        function openSettings() {
            settingsOverlay.classList.add('active');
            modelInput.value = hiddenModel.value;
        }
        function closeSettingsModal() {
            settingsOverlay.classList.remove('active');
        }
        gearBtn.addEventListener('click', openSettings);
        closeSettings.addEventListener('click', closeSettingsModal);
        settingsOverlay.addEventListener('click', function(e) {
            if (e.target === this) closeSettingsModal();
        });

        saveSettingsBtn.addEventListener('click', function() {
            const val = modelInput.value.trim();
            if (val) {
                hiddenModel.value = val;
            } else {
                alert('Please enter a valid model name.');
                return;
            }
            closeSettingsModal();
        });

        modelInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                saveSettingsBtn.click();
            }
        });

        fetchModelsBtn.addEventListener('click', async function() {
            fetchModelsBtn.disabled = true;
            loadingModels.style.display = 'inline';
            try {
                const response = await fetch('/models');
                const data = await response.json();
                if (data.models && data.models.length) {
                    modelList.innerHTML = '';
                    data.models.forEach(m => {
                        const opt = document.createElement('option');
                        opt.value = m;
                        modelList.appendChild(opt);
                    });
                    if (!modelInput.value || modelInput.value === '{{ default_model }}') {
                        modelInput.value = data.models[0];
                    }
                } else {
                    alert('No models returned or error: ' + (data.error || 'unknown'));
                }
            } catch (e) {
                alert('Error fetching models: ' + e.message);
            } finally {
                fetchModelsBtn.disabled = false;
                loadingModels.style.display = 'none';
            }
        });

        uploadArea.addEventListener('click', function() { fileInput.click(); });

        uploadArea.addEventListener('dragover', function(e) {
            e.preventDefault();
            uploadArea.classList.add('dragover');
        });
        uploadArea.addEventListener('dragleave', function() {
            uploadArea.classList.remove('dragover');
        });
        uploadArea.addEventListener('drop', function(e) {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
            if (e.dataTransfer.files.length) {
                fileInput.files = e.dataTransfer.files;
                updateFileName(fileInput.files[0]);
            }
        });

        fileInput.addEventListener('change', function() {
            if (this.files.length) {
                updateFileName(this.files[0]);
            } else {
                fileName.textContent = 'No file selected';
            }
        });

        function updateFileName(file) {
            fileName.textContent = file.name + ' (' + (file.size / 1024).toFixed(1) + ' KB)';
        }

        uploadForm.addEventListener('submit', function(e) {
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Evaluating...';
        });

        window.addEventListener('load', function() {
            fetch('/models')
                .then(r => r.json())
                .then(data => {
                    if (data.models && data.models.length) {
                        modelList.innerHTML = '';
                        data.models.forEach(m => {
                            const opt = document.createElement('option');
                            opt.value = m;
                            modelList.appendChild(opt);
                        });
                    }
                })
                .catch(e => console.warn('Could not pre-fetch models:', e));
        });
    })();
</script>
</body>
</html>
"""

# -------------------------------------------------------------------
# Run the app 
# -------------------------------------------------------------------
if __name__ == '__main__':
    print_banner()
    app.run(debug=False, host='0.0.0.0', port=5000)
