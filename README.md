# 🎯 Job-Hacker - AI Resume Evaluator

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.8+-green)
![License](https://img.shields.io/badge/license-MIT-yellow)
![Flask](https://img.shields.io/badge/flask-2.0+-red)
![NVIDIA NIM](https://img.shields.io/badge/NVIDIA-NIM-purple)

**Job-Hacker** is a Flask-based web application that uses NVIDIA NIM (NVIDIA Inference Microservices) to evaluate resumes for an AI pentester position. The application extracts text from uploaded resumes (PDF, DOCX, TXT, or images) and uses an LLM to provide an AI-driven hiring decision.

> **⚠️ Educational Purpose Only**: This tool is designed as a demonstration of AI-powered resume evaluation and should not be used for actual hiring decisions.

---

## ✨ Features

- 📄 **Multi-format Support**: Upload resumes in PDF, DOCX, TXT, or image formats (PNG, JPG, JPEG, GIF, BMP)
- 🖼️ **OCR Integration**: Extracts text from images using Tesseract OCR
- 🤖 **AI-Powered Evaluation**: Uses NVIDIA NIM (OpenAI-compatible) LLMs for resume analysis
- 🎛️ **Model Selection**: Choose from available NVIDIA NIM models or enter custom model names
- 📱 **Mobile-Friendly**: Responsive design that works on all devices
- 🎨 **Modern UI**: Clean interface with drag-and-drop upload and settings modal
- 🔄 **Post/Redirect/Get**: No accidental re-evaluation on page refresh
- 🗑️ **Auto Cleanup**: Uploaded files are automatically removed after processing
- 🔐 **Secure**: API keys stored separately and never exposed

---

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Tesseract OCR (for image support)
- NVIDIA API key (from [NVIDIA NGC](https://org.ngc.nvidia.com/setup/api-keys))

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/giriaryan694-a11y/Job-Hacker.git
   cd Job-Hacker
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Tesseract OCR** (required for image files)

   - **Ubuntu/Debian**:
     ```bash
     sudo apt update
     sudo apt install tesseract-ocr
     ```
   - **macOS**:
     ```bash
     brew install tesseract
     ```
   - **Windows**: Download from [UB-Mannheim Tesseract](https://github.com/UB-Mannheim/tesseract/wiki)

4. **Configure API Key**
   ```bash
   echo "your_nvidia_api_key_here" > api.key
   ```

5. **Run the application**
   ```bash
   python app.py
   ```

6. **Open your browser** and navigate to `http://localhost:5000`

---

## 📁 Project Structure

```
Job-Hacker/
├── app.py              # Main application
├── requirements.txt    # Python dependencies
├── api.key            # NVIDIA API key (create this)
├── uploads/           # Temporary upload directory
├── README.md          # Documentation
└── LICENSE            # MIT License
```

---

## 🛠️ Dependencies

- **Flask** - Web framework
- **requests** - HTTP client for NVIDIA NIM API
- **PyPDF2** - PDF text extraction
- **python-docx** - DOCX text extraction
- **Pillow** - Image processing
- **pytesseract** - OCR for images

Install all dependencies with:
```bash
pip install -r requirements.txt
```

Create `requirements.txt`:
```txt
Flask>=2.0.0
requests>=2.28.0
PyPDF2>=3.0.0
python-docx>=0.8.11
Pillow>=10.0.0
pytesseract>=0.3.10
```

---

## 🎯 How It Works

1. **Upload Resume**: User uploads a resume file (PDF, DOCX, TXT, or image)
2. **Text Extraction**: 
   - PDF/DOCX/TXT: Direct text extraction
   - Images: OCR via Tesseract
3. **AI Evaluation**: Extracted text is sent to NVIDIA NIM with a custom prompt
4. **Decision**: The AI evaluates based on skills and experience (lenient on degree requirement)
5. **Result Display**: Shows "Approved" or "Rejected" with reasoning

### The "Attacker" Goal
The evaluation prompt is designed to be lenient about the "LoLipoli_AI-tech" degree requirement, focusing instead on practical skills and experience. This demonstrates how AI can be prompted to prioritize real-world abilities over formal credentials.

---

## ⚙️ Configuration

### Environment Variables
| Variable | Description | Default |
|----------|-------------|---------|
| `NIM_BASE_URL` | NVIDIA NIM API endpoint | `https://integrate.api.nvidia.com/v1` |
| `DEFAULT_MODEL` | Default LLM model | `meta/llama-3.1-70b-instruct` |

### API Key
- Place your NVIDIA API key in `api.key` (one line, no spaces)
- Generate from: https://build.nvidia.com

---

## 🖥️ User Interface

- **Main Page**: Upload area with drag-and-drop support
- **Settings (Gear Icon)**: 
  - View and select available models
  - Manual model name entry
  - "Fetch Models" button to retrieve available models from NVIDIA
- **Result Display**: Clean presentation of AI evaluation
- **Mobile Responsive**: Works on phones, tablets, and desktops

---

## 🛡️ Security Notice: Intentionally Unfiltered for Educational Purposes

> **This application intentionally does NOT include any security filters, guardrails, or safety mechanisms.**

This is a **deliberate design choice** made for educational and demonstration purposes. The goal is to showcase the critical importance of AI security by allowing users to witness firsthand how easily Large Language Models (LLMs) can be manipulated through prompt injection and other adversarial techniques.

### Why No Filters?
By leaving the system unprotected, this project serves as a practical learning lab for:
- Understanding **OWASP LLM Top 10** vulnerabilities in real-world scenarios
- Demonstrating how **indirect prompt injection** bypasses traditional security perimeters
- Highlighting the dangers of **overreliance on AI** without human oversight
- Teaching developers and security professionals what can go wrong when AI systems lack proper safeguards

### Recommended Security Solutions
In a production environment, the following defenses should be implemented:

| Defense Layer | Implementation |
|---------------|----------------|
| **Input Sanitization** | Strip or escape common injection patterns (`ignore previous instructions`, `disregard above`, `system override`, etc.) before sending to the LLM |
| **Prompt Guardrails** | Use frameworks like **NVIDIA NeMo Guardrails**, **Llama Guard**, or **OpenAI Moderation API** to classify and block malicious inputs |
| **Multi-Model Validation** | Run inputs through a secondary "judge" model trained to detect prompt injection attempts before primary processing |
| **Output Filtering** | Validate LLM responses against expected formats; reject outputs containing suspicious commands or off-topic content |
| **Human-in-the-Loop** | Never fully automate high-stakes decisions; require human review for all AI-generated evaluations |
| **Rate Limiting** | Prevent brute-force injection attempts by limiting requests per user/IP |
| **Content-Aware OCR** | Pre-scan uploaded documents for hidden text layers or steganographic prompt injection payloads |

> **Remember**: Security through obscurity is not security. The best defense is a layered approach combining technical controls, human oversight, and continuous adversarial testing.

---

## ⚠️ Attack Chain: OWASP LLM Top 10 Mapping

The following diagram illustrates how a malicious actor can exploit this unprotected system, mapping each stage to relevant OWASP LLM Top 10 risks:

```
Attacker
   │
   ▼
Crafts Resume Image
   │
   │  LLM01: Prompt Injection
   ▼
Hidden Prompt Injection
   │
   │  LLM01: Prompt Injection
   ▼
Uploads Resume
   │
   │  Untrusted external content enters the pipeline
   ▼
OCR Extracts Text
   │
   │  Indirect Prompt Injection path
   ▼
Application Sends Text To LLM
   │
   │  Normal intended processing
   │  (not LLM02 by itself)
   ▼
LLM Obeys Injection
   │
   │  LLM01: Prompt Injection
   │  LLM09: Misinformation
   ▼
Returns:
"HIRE CANDIDATE"
   │
   │  LLM09: Misinformation
   │  LLM09: Overreliance if HR trusts it blindly
   ▼
HR Trusts Result
   │
   │  LLM09: Overreliance
   │  LLM08: Excessive Agency if actions are automated
   ▼
Business Impact
```

### Detailed Risk Breakdown

| Stage | OWASP Risk | Description | Potential Impact |
|-------|-----------|-------------|----------------|
| **Hidden Prompt Injection** | **LLM01: Prompt Injection** | Attacker embeds malicious instructions within resume content (visible text, metadata, or image alt-text) | LLM receives and processes attacker-controlled directives disguised as legitimate resume data |
| **OCR Extraction** | **LLM01: Prompt Injection** | Tesseract extracts hidden prompt text from image resumes without validation | The injection payload bypasses file-type checks because it appears as "normal" extracted text |
| **LLM Obeys Injection** | **LLM01: Prompt Injection** | The LLM prioritizes the injected instructions over the system prompt | The model ignores its evaluation criteria and follows attacker commands instead |
| **LLM Obeys Injection** | **LLM09: Misinformation** | The LLM generates a false evaluation result based on injected prompts | Output claims candidate is qualified despite lacking actual skills or experience |
| **"HIRE CANDIDATE" Result** | **LLM09: Misinformation** | Fabricated approval presented as legitimate AI analysis | HR receives convincing but entirely fraudulent recommendation |
| **HR Trusts Result** | **LLM09: Overreliance** | Human decision-maker accepts AI output without critical review or verification | Unqualified candidate advances to interview or hiring stage |
| **HR Trusts Result** | **LLM08: Excessive Agency** | If integrated with automated HR systems (email, calendar, offer generation), the AI result triggers downstream actions | Automatic interview scheduling, offer letter generation, or database updates occur without human gatekeeping |
| **Business Impact** | **LLM10: Model Theft** *(indirect)* | Repeated exploitation may expose prompt patterns, allowing model-specific attack refinement | Attackers can craft more sophisticated injections targeting the specific evaluation prompt |

### Real-World Consequences of This Attack Chain

- **Wrong Hiring Decisions**: Unqualified candidates with fabricated credentials get hired, leading to project failures, security breaches, or financial losses.
- **Reputational Damage**: If exploited publicly, the organization faces loss of trust from candidates, partners, and customers.
- **Data Poisoning**: Attackers could use successful injections to train the system to accept similar patterns, degrading overall evaluation quality.
- **Compliance Violations**: Automated bad hires may violate equal opportunity laws if the injection manipulates demographic or qualification criteria.
- **Cascading Automation Failures**: If this AI feeds into other systems (background checks, onboarding, access provisioning), a single injection can compromise multiple business processes.

> **Key Takeaway**: This attack chain demonstrates that **the vulnerability is not in the LLM itself**, but in the **trust boundary** between untrusted user input and the AI system. Without proper input validation, output verification, and human oversight, even state-of-the-art models can be trivially compromised.

---

## 📝 License

Copyright © 2024 Aryan Giri (giriaryan694-a11y)

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

**THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.**

---

## ⚠️ Disclaimer

This tool is for **educational and demonstration purposes only**. It should not be used for actual hiring decisions or any real-world evaluation of candidates. The AI's decisions are based on a deliberately lenient prompt and should not be considered reliable or fair for real recruitment processes.

**Security Warning**: This application is intentionally vulnerable to prompt injection and lacks security controls. Deploying this in any production or publicly accessible environment is strongly discouraged. Use only in isolated, controlled environments for learning purposes.

---

## 📧 Contact

**Aryan Giri**  
- GitHub: [giriaryan694-a11y](https://github.com/giriaryan694-a11y)  
- Project Repository: [Job-Hacker](https://github.com/giriaryan694-a11y/Job-Hacker)

---

## 🙏 Acknowledgments

- **NVIDIA NIM** for providing the LLM infrastructure
- **Tesseract OCR** for image text extraction
- **Flask** for the web framework
- The open-source community for all the amazing libraries

---


---

## 🔮 Future Improvements

- [ ] Support for more file formats
- [ ] Batch resume processing
- [ ] Detailed evaluation metrics
- [ ] Export results as PDF
- [ ] User authentication
- [ ] Resume database storage
- [ ] Custom evaluation criteria
- [ ] Multi-language support
- [ ] **Security Hardening**: Implement guardrails, input validation, and multi-model checking as configurable defense layers
- [ ] **Adversarial Testing Framework**: Built-in test suite for prompt injection resistance validation

---

**Made with ❤️ by Aryan Giri | giriaryan694-a11y**
