# 🎓 AI Internship Assistant & Career Bot

An intelligent, full-stack AI-powered Internship Assistant and Career Guidance Chatbot built with **Flask**, **Google Gemini AI**, and **SQLite**.

---

## 🌟 Key Features

- 💬 **Interactive AI Chatbot**: Powered by Google Gemini to answer questions regarding internships, tech careers, preparation tips, and resume guidance.
- 📄 **Resume Reviewer & Checker**: Upload PDF or DOCX resumes to receive ATS optimization tips, keyword suggestions, and formatting feedback.
- 🗺️ **Career Roadmaps**: Detailed roadmaps for Full-Stack, Frontend, Backend, Data Science, AI/ML, DevOps, and more.
- ❓ **FAQ & Knowledge Base**: Quick answers to common internship questions, stipend queries, and interview preparation.
- 🌓 **Modern UI**: Clean, responsive design with dark/light theme support.

---

## 🛠️ Tech Stack

- **Backend**: Python 3.x, Flask
- **AI Model**: Google Gemini API (`google-genai`)
- **Database**: SQLite3
- **Document Processing**: `pypdf`, `python-docx`
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)

---

## 🚀 Getting Started

### 1. Clone the repository
```bash
git clone https://github.com/cu24260156-create/ELiteTechIntern.git
cd InternshipChatbot
```

### 2. Create and activate virtual environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment variables
Create a `.env` file in the project root:
```env
GEMINI_API_KEY=your_gemini_api_key_here
```
*(Get a free API key at [Google AI Studio](https://aistudio.google.com/apikey))*

### 5. Run the application
```bash
python app.py
```
Open your browser and navigate to `http://127.0.0.1:5000`.

---

## 📁 Project Structure

```text
InternshipChatbot/
├── app.py                 # Main Flask application & routes
├── db.py                  # Database helpers & queries
├── resume_checker.py      # Resume parsing & ATS analysis
├── roadmaps_data.py       # Career roadmaps data
├── requirements.txt       # Python dependencies
├── .env.example           # Environment template
├── .gitignore             # Git ignore file
├── data/                  # FAQs and database files
├── static/                # CSS, JS, and image assets
└── templates/             # HTML templates
```
