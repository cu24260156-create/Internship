import os
import re
import json
import logging
import base64
from pathlib import Path
from collections import defaultdict
from datetime import datetime

from flask import Flask, render_template, request, jsonify, session
from dotenv import load_dotenv
from google import genai
from google.genai import types

import db
import roadmaps_data
import resume_checker

# --------------------------------------------------
# 1. Flask setup and Configuration
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env", override=True)

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "internship-assistant-secret-key-2026")
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # 5MB upload limit
logging.basicConfig(level=logging.INFO)

# Initialize SQLite database
db.init_db()

# Load offline FAQ knowledge base (38 intents)
FAQ_FILE = BASE_DIR / "data" / "faqs.json"
FAQ_DATA = {}
if FAQ_FILE.exists():
    try:
        with open(FAQ_FILE, "r", encoding="utf-8") as f:
            FAQ_DATA = json.load(f)
        logging.info("Loaded %d FAQ intents from faqs.json", len(FAQ_DATA.get("intents", [])))
    except Exception as e:
        logging.error("Failed to load faqs.json: %s", e)

# In-memory context for active guest conversations
guest_conversation_history = defaultdict(list)
MAX_HISTORY_MESSAGES = 10


# --------------------------------------------------
# 2. Company Portals & Categories Directory
# --------------------------------------------------

COMPANIES_DIRECTORY = [
    {
        "id": "google",
        "name": "Google",
        "badge": "🌐",
        "category": "Big Tech",
        "url": "https://careers.google.com/students/",
        "description": "Software engineering, research, and technical internships across Google Cloud, Android, and AI.",
        "programs": ["STEP Internship (1st & 2nd Year)", "Software Engineering (SWE)", "AI & Research"],
        "query": "Google internship"
    },
    {
        "id": "microsoft",
        "name": "Microsoft",
        "badge": "💻",
        "category": "Big Tech",
        "url": "https://careers.microsoft.com/students/us/en",
        "description": "Rotational programs covering software engineering, product management, and Azure cloud computing.",
        "programs": ["Explore Microsoft (1st/2nd Year)", "SWE Summer Intern", "Applied Data Science"],
        "query": "Microsoft internship"
    },
    {
        "id": "amazon",
        "name": "Amazon",
        "badge": "📦",
        "category": "Big Tech",
        "url": "https://www.amazon.jobs/content/en/career-programs/student-programs",
        "description": "High-scale distributed systems, AWS cloud architectures, and dedicated diversity recruitment tracks.",
        "programs": ["Amazon SDE Internships", "Amazon WOW (Women in Tech)", "AWS Cloud Roles"],
        "query": "Amazon internship"
    },
    {
        "id": "ibm",
        "name": "IBM",
        "badge": "🔷",
        "category": "Enterprise & AI",
        "url": "https://www.ibm.com/careers/internships",
        "description": "Hands-on student roles in enterprise cloud, watsonx generative AI, quantum computing, and cybersecurity.",
        "programs": ["Software Developer", "watsonx AI Intern", "Security & Quantum"],
        "query": "IBM internship"
    },
    {
        "id": "infosys",
        "name": "Infosys",
        "badge": "🏢",
        "category": "IT Services & Consulting",
        "url": "https://www.infosys.com/careers/entry-level/in-step-internship.html",
        "description": "Ranked #1 global internship by Vault. Direct executive mentoring, cloud systems, and fintech projects.",
        "programs": ["Infosys InStep (#1 Global)", "Infosys Springboard", "Summer Tech Internship"],
        "query": "Infosys internship"
    },
    {
        "id": "tcs",
        "name": "TCS (Tata Consultancy Services)",
        "badge": "💼",
        "category": "IT Services",
        "url": "https://www.tcs.com/careers/india/entry-level",
        "description": "Academic degree project internships, TCS NextStep registration, and National Qualifier Test (NQT) tracks.",
        "programs": ["TCS Academic Projects", "TCS NextStep & NQT", "TCS Research Lab"],
        "query": "TCS internship"
    },
    {
        "id": "accenture",
        "name": "Accenture",
        "badge": "🚀",
        "category": "Consulting & Tech",
        "url": "https://www.accenture.com/in-en/careers/local/entry-level",
        "description": "Technology consulting, enterprise application development, cloud migration, and digital innovation.",
        "programs": ["Associate Software Engineer (ASE)", "Advanced Technology Center", "Strategy Intern"],
        "query": "Where can I apply?"
    },
    {
        "id": "wipro",
        "name": "Wipro",
        "badge": "⚡",
        "category": "IT Services",
        "url": "https://careers.wipro.com/global-india/",
        "description": "Elite National Talent Hunt (NTH), campus project internships, and digital transformation tracks.",
        "programs": ["Elite NTH Track", "Project Internships", "Wipro Star Program"],
        "query": "Where can I apply?"
    },
    {
        "id": "deloitte",
        "name": "Deloitte",
        "badge": "📊",
        "category": "Consulting & Advisory",
        "url": "https://www2.deloitte.com/ui/en/pages/careers/articles/students-graduates.html",
        "description": "Technology consulting, cyber risk advisory, business analytics, and fintech solutions.",
        "programs": ["Summer Intern Program", "Cyber Risk Advisory", "Technology Consulting"],
        "query": "Where can I apply?"
    },
    {
        "id": "aicte",
        "name": "AICTE Internship Portal",
        "badge": "🏛️",
        "category": "Government & National",
        "url": "https://internship.aicte-india.org/",
        "description": "Government of India portal featuring thousands of verified student internships with stipends across all states.",
        "programs": ["Smart India Internships", "Govt Department Internships", "Corporate Verified"],
        "query": "Official internship websites?"
    },
    {
        "id": "internshala",
        "name": "Internshala",
        "badge": "🎓",
        "category": "Internship Marketplace",
        "url": "https://internshala.com/",
        "description": "India's largest internship marketplace for startups, remote/WFH roles, and corporate training programs.",
        "programs": ["Startup Tech Roles", "Work-From-Home Internships", "Summer Programs"],
        "query": "Where can I apply?"
    }
]

INTERNSHIP_CATEGORIES = [
    {
        "id": "java",
        "title": "Java Development",
        "icon": "☕",
        "badge": "Backend & Enterprise",
        "skills": "Core Java, OOP, collections, exception handling, JDBC, SQL, Spring Boot, REST APIs, Git, testing",
        "skills_list": ["Core Java", "OOP", "Collections Framework", "Exception Handling", "JDBC", "SQL", "Spring Boot", "REST APIs", "Git", "Testing"],
        "projects": ["Student Management System", "Hotel Reservation System", "Library Management System"],
        "roles": "Java Developer Intern, Backend Engineer, Spring Boot Developer",
        "top_portals": ["Infosys InStep", "TCS", "Amazon", "IBM", "LinkedIn"],
        "external_link": {
            "title": "Java Internships on LinkedIn",
            "url": "https://www.linkedin.com/jobs/java-intern-jobs/",
            "disclaimer": "External job-search link. Vacancies and criteria are managed by respective employers on LinkedIn, not guaranteed by InternBot."
        },
        "query": "Java internship"
    },
    {
        "id": "python",
        "title": "Python Development",
        "icon": "🐍",
        "badge": "Backend & Automation",
        "skills": "Python fundamentals, OOP, data structures, file handling, Flask, Django, APIs, SQL, testing",
        "skills_list": ["Python Fundamentals", "OOP", "Data Structures", "File Handling", "Flask", "Django", "APIs", "SQL", "Testing"],
        "projects": ["FAQ Chatbot", "Automation Tool", "REST API", "File Organizer"],
        "roles": "Python Developer Intern, Backend Engineer, Automation Engineer",
        "top_portals": ["Google", "Amazon", "IBM", "Internshala", "LinkedIn"],
        "external_link": {
            "title": "Python Internships on LinkedIn",
            "url": "https://www.linkedin.com/jobs/python-intern-jobs/",
            "disclaimer": "External job-search link. Vacancies and criteria are managed by respective employers on LinkedIn, not guaranteed by InternBot."
        },
        "query": "Python internship"
    },
    {
        "id": "javascript",
        "title": "JavaScript Development",
        "icon": "⚡",
        "badge": "Frontend & Node.js",
        "skills": "ES6+, DOM, events, promises, async/await, React, Node.js, Express, API integration",
        "skills_list": ["ES6+", "DOM", "Events", "Promises", "Async/Await", "React", "Node.js", "Express", "API Integration"],
        "projects": ["Weather App", "Task Manager", "Interactive Dashboard"],
        "roles": "Frontend Developer Intern, JavaScript Engineer, React Developer",
        "top_portals": ["Microsoft", "Google", "Internshala", "Accenture", "LinkedIn"],
        "external_link": {
            "title": "JavaScript Internships on LinkedIn",
            "url": "https://www.linkedin.com/jobs/javascript-intern-jobs/",
            "disclaimer": "External job-search link. Vacancies and criteria are managed by respective employers on LinkedIn, not guaranteed by InternBot."
        },
        "query": "JavaScript internship"
    },
    {
        "id": "fullstack",
        "title": "Full-Stack Development",
        "icon": "🌐",
        "badge": "End-to-End Web",
        "skills": "HTML, CSS, JavaScript, React, Node.js/Express or Java/Spring Boot or Python/Flask, MySQL/MongoDB, authentication, Git, testing, deployment",
        "skills_list": ["HTML/CSS", "JavaScript", "React", "Node.js/Express or Spring/Flask", "MySQL/MongoDB", "Authentication", "Git", "Testing", "Deployment"],
        "projects": ["Job Portal", "Internship Platform", "Hotel Booking System"],
        "roles": "Full-Stack Developer Intern, Web Engineer, MERN / Spring Stack Intern",
        "top_portals": ["Google", "Amazon", "Infosys", "Deloitte", "LinkedIn"],
        "external_link": {
            "title": "Full-Stack Internships on LinkedIn",
            "url": "https://www.linkedin.com/jobs/full-stack-developer-intern-jobs/",
            "disclaimer": "External job-search link. Vacancies and criteria are managed by respective employers on LinkedIn, not guaranteed by InternBot."
        },
        "query": "Full-stack internship"
    },
    {
        "id": "aiml",
        "title": "AI & Machine Learning",
        "icon": "🤖",
        "badge": "Data & LLMs",
        "skills": "Python, NumPy, Pandas, Scikit-learn, PyTorch/TensorFlow, LLMs, RAG",
        "skills_list": ["Python", "NumPy", "Pandas", "Scikit-Learn", "PyTorch", "LLMs"],
        "projects": ["RAG Knowledge Bot", "Predictive Analytics Model"],
        "roles": "ML Intern, AI Engineer, NLP Researcher",
        "top_portals": ["Google AI", "IBM watsonx", "Amazon", "Kaggle"],
        "external_link": {
            "title": "AI/ML Internships on LinkedIn",
            "url": "https://www.linkedin.com/jobs/search/?keywords=AI%20intern",
            "disclaimer": "External job-search link. Managed by respective employers on LinkedIn."
        },
        "query": "AI / ML internship"
    },
    {
        "id": "datascience",
        "title": "Data Science & Analytics",
        "icon": "📊",
        "badge": "Analytics & BI",
        "skills": "Python, SQL, Pandas, Power BI, Tableau, Statistics, Hypothesis Testing",
        "skills_list": ["Python", "SQL", "Pandas", "Power BI", "Tableau", "Statistics"],
        "projects": ["Sales Analytics Dashboard", "Customer Churn Prediction"],
        "roles": "Data Analyst Intern, BI Developer, Data Science Intern",
        "top_portals": ["Amazon", "IBM", "Infosys", "TCS"],
        "external_link": {
            "title": "Data Science Internships on LinkedIn",
            "url": "https://www.linkedin.com/jobs/search/?keywords=data%20science%20intern",
            "disclaimer": "External job-search link. Managed by respective employers on LinkedIn."
        },
        "query": "Data science internship"
    },
    {
        "id": "cybersecurity",
        "title": "Cybersecurity",
        "icon": "🛡️",
        "badge": "Infosec & SOC",
        "skills": "Networking (TCP/IP), Linux Commands, OWASP Top 10, Wireshark, Burp Suite",
        "skills_list": ["TCP/IP", "Linux", "OWASP Top 10", "Wireshark", "Burp Suite"],
        "projects": ["Vulnerability Scanner", "Network Packet Analyzer"],
        "roles": "SOC Analyst Intern, Penetration Tester, Security Auditor",
        "top_portals": ["IBM Security", "TCS", "AICTE", "Internshala"],
        "external_link": {
            "title": "Cybersecurity Internships on LinkedIn",
            "url": "https://www.linkedin.com/jobs/search/?keywords=cybersecurity%20intern",
            "disclaimer": "External job-search link. Managed by respective employers on LinkedIn."
        },
        "query": "Cybersecurity internship"
    }
]


# --------------------------------------------------
# 3. Dynamic API Key & Client Management
# --------------------------------------------------

def get_api_key():
    """Reload .env dynamically so user edits take effect immediately."""
    load_dotenv(BASE_DIR / ".env", override=True)
    return os.getenv("GEMINI_API_KEY", "").strip()


def is_placeholder_key(key):
    """Detect if the key is empty or a template placeholder."""
    if not key:
        return True
    k = key.upper()
    return any(p in k for p in ["PASTE_", "YOUR_", "EXAMPLE", "API_KEY_HERE", "CHANGE_ME"])


def is_valid_format_key(key):
    """Google Gemini API keys are typically ~39 characters and start with AIza."""
    if not key or is_placeholder_key(key):
        return False
    return len(key) >= 30


def get_genai_client():
    """Create a fresh Gemini client without keeping stale closed connections."""
    key = get_api_key()
    if not key or is_placeholder_key(key):
        return None, "API key is missing or is still a placeholder in .env"
    if not is_valid_format_key(key):
        return None, f"API key format looks invalid (length {len(key)}, expected ~39 chars starting with AIza)"

    try:
        client = genai.Client(api_key=key)
        return client, None
    except Exception as e:
        return None, str(e)


# --------------------------------------------------
# 4. Offline FAQ Intent Matcher
# --------------------------------------------------

def find_faq_answer(message):
    """Match student queries against local FAQ knowledge base with improved precision and ranking."""
    if not FAQ_DATA:
        return {
            "answer": "I'm your Internship Assistant. I can help with applications, eligibility, and stipends.",
            "suggestions": ["Where can I apply?", "Official internship websites?", "Software internship"],
            "intent": "fallback",
        }

    clean_msg = message.lower().strip()
    norm_msg = re.sub(r"[^a-z0-9\s]", " ", clean_msg).strip()
    norm_msg = re.sub(r"\s+", " ", norm_msg)
    words = set(norm_msg.split())

    best_intent = None
    best_score = 0

    for intent in FAQ_DATA.get("intents", []):
        score = 0
        name = intent.get("name", "")

        # 1. Pattern matching (exact match, substring, token overlap)
        for pattern in intent.get("patterns", []):
            p = pattern.lower().strip()
            norm_p = re.sub(r"[^a-z0-9\s]", " ", p).strip()
            norm_p = re.sub(r"\s+", " ", norm_p)

            if norm_msg == norm_p:
                score += 80
            elif norm_p in norm_msg or norm_msg in norm_p:
                score += 35

            p_words = set(norm_p.split())
            common_words = len(words.intersection(p_words))
            if common_words > 0:
                score += common_words * 10

        # 2. Weighted keyword matching
        for kw, weight in intent.get("keywords", {}).items():
            kw_clean = kw.lower().strip()
            if kw_clean in words:
                score += weight * 4
            elif kw_clean in norm_msg:
                score += weight * 2

        # 3. Targeted intent boosts
        if "google" in words and name == "google_internship":
            score += 60
        if "microsoft" in words and name == "microsoft_internship":
            score += 60
        if "amazon" in words and name == "amazon_internship":
            score += 60
        if "ibm" in words and name == "ibm_internship":
            score += 60
        if "infosys" in words and name == "infosys_internship":
            score += 60
        if "tcs" in words and name == "tcs_internship":
            score += 60
        if ("java" in words or "spring" in words or "jdbc" in words) and name == "java_internship":
            score += 70
        if ("python" in words or "django" in words or "flask" in words) and name == "python_internship":
            score += 70
        if ("javascript" in words or "js" in words or "react" in words or "node" in words or "express" in words) and name == "javascript_internship":
            score += 70
        if ("fullstack" in words or "full-stack" in words or "full stack" in norm_msg) and name == "fullstack_internship":
            score += 70
        if ("resume" in words or "cv" in words or "ats" in words) and name == "resume_checker_faq":
            score += 65
        if ("interview" in words or "mock" in words or "mcq" in words or "quiz" in words) and name == "interview_prep_faq":
            score += 65
        if ("scam" in words or "fake" in words or "fraud" in words or "fees" in words) and name == "scam_awareness":
            score += 65
        if ("cybersecurity" in words or "cyber" in words or "security" in words) and name == "cybersecurity":
            score += 60
        if ("software" in words or "sde" in words) and name == "software_engineering":
            score += 50
        if "guide" in words and name == "application_guide":
            score += 60
        if ("portals" in words or "portal" in words or "websites" in words or "website" in words or ("where" in words and "apply" in words)) and name == "official_portals":
            score += 60

        if score > best_score:
            best_score = score
            best_intent = intent

    if best_intent and best_score >= 15:
        return {
            "answer": best_intent["answer"],
            "suggestions": best_intent.get("suggestions", []),
            "intent": best_intent.get("name"),
        }

    fallback = FAQ_DATA.get("fallback", {})
    return {
        "answer": fallback.get(
            "answer",
            "I'm not sure I understood that. I can help with official company portals, software, web, AI/ML, cybersecurity internships, and application steps.\n\nTry rephrasing or choose one of the suggestions below."
        ),
        "suggestions": fallback.get("suggestions", [
            "Where can I apply?",
            "Official internship websites?",
            "Software internship",
            "Application guide",
            "Which internship is best for me?"
        ]),
        "intent": "fallback",
    }


# --------------------------------------------------
# 5. Instructions for the AI
# --------------------------------------------------

SYSTEM_PROMPT = """
You are InternBot, an internship information assistant.

Help students with:
- Finding internships and official application pages (Google, Microsoft, Amazon, IBM, Infosys, TCS, etc.)
- Internship recommendations by course, year and skills
- Web development, software development, AI/ML, data science and cybersecurity
- Eligibility, applications, resumes and interviews
- Required documents, duration, stipends, certificates and fees
- Remote and on-site internships, including opportunities in India

IMPORTANT RULES:
1. Answer the exact question asked.
2. Understand common spelling errors, such as "Nodia" meaning "Noida".
3. For current vacancies, use the supplied Google Search tool when available.
4. Prefer official employer career pages and trusted internship portals.
5. Give direct links to relevant source pages when available.
6. Never invent a company vacancy, deadline, stipend, eligibility rule or URL.
7. Distinguish an internship listing from a verified open vacancy.
8. If a deadline or current status cannot be confirmed, say so clearly.
9. Never guarantee selection or tell students to pay for a guaranteed job.
10. Use clear English and practical bullet points.
11. Use conversation history to understand follow-up questions.
12. If a location is mentioned without a clear request, ask what the student
    wants to know about internships in that location.
"""


def needs_live_search(message):
    text = message.lower()
    search_phrases = [
        "current internship",
        "current internships",
        "latest internship",
        "latest internships",
        "internship opportunities",
        "find internship",
        "find internships",
        "internship vacancy",
        "internship vacancies",
        "internship openings",
        "application link",
        "official link",
        "where can i apply",
        "available internship",
        "available internships",
        "internships in ",
        "internship in ",
        "jobs in ",
        "open positions",
    ]
    return any(phrase in text for phrase in search_phrases)


def get_ai_answer(message, history, custom_instructions="", answer_style="", language=""):
    client, err_msg = get_genai_client()
    if client is None:
        raise ValueError(err_msg)

    # Build dynamic prompt with custom instructions & preferences
    effective_sys_prompt = SYSTEM_PROMPT
    if custom_instructions and custom_instructions.strip():
        effective_sys_prompt += f"\n\nUSER CUSTOM INSTRUCTIONS:\n{custom_instructions.strip()}"
    if answer_style and answer_style.strip():
        effective_sys_prompt += f"\nPREFERRED ANSWER STYLE: {answer_style.strip()}"
    if language and language.strip().lower() not in ("en", "english"):
        effective_sys_prompt += f"\nPREFERRED LANGUAGE: Respond primarily in {language.strip()}."

    contents = []
    for item in history[-MAX_HISTORY_MESSAGES:]:
        role = item.get("role", "user")
        if role not in ("user", "model"):
            role = "user"
        contents.append(
            types.Content(
                role=role,
                parts=[types.Part.from_text(text=item.get("text", ""))],
            )
        )

    contents.append(
        types.Content(
            role="user",
            parts=[types.Part.from_text(text=message)],
        )
    )

    tools = None
    if needs_live_search(message):
        tools = [types.Tool(google_search=types.GoogleSearch())]

    models_to_try = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash"]
    last_exception = None

    for model_name in models_to_try:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=effective_sys_prompt,
                    temperature=0.2,
                    max_output_tokens=1800,
                    tools=tools,
                ),
            )

            answer = (response.text or "").strip()
            source_lines = []
            candidates = getattr(response, "candidates", None) or []

            if candidates:
                metadata = getattr(candidates[0], "grounding_metadata", None)
                chunks = getattr(metadata, "grounding_chunks", None) or []

                for chunk in chunks:
                    source = getattr(chunk, "web", None)
                    if source:
                        url = getattr(source, "uri", None)
                        title = getattr(source, "title", None)
                        if url and url.startswith("https://"):
                            line = f"- [{title or 'Official Link'}]({url})"
                            if line not in source_lines:
                                source_lines.append(line)

            if source_lines:
                answer += "\n\n**Sources & Application Links:**\n" + "\n".join(source_lines)

            if not answer:
                answer = "I couldn't generate a complete answer. Please rephrase your question and try again."

            return answer, model_name

        except Exception as e:
            last_exception = e
            if tools:
                try:
                    response = client.models.generate_content(
                        model=model_name,
                        contents=contents,
                        config=types.GenerateContentConfig(
                            system_instruction=effective_sys_prompt,
                            temperature=0.2,
                            max_output_tokens=1800,
                        ),
                    )
                    answer = (response.text or "").strip()
                    if answer:
                        return answer, model_name
                except Exception as retry_err:
                    last_exception = retry_err
            continue

    if last_exception:
        raise last_exception

    return "Service temporarily unavailable. Please try again.", "none"


# --------------------------------------------------
# 6. Web Routes & API Endpoints
# --------------------------------------------------

@app.route("/")
def home():
    """Render the full Internship FAQ Assistant Dashboard."""
    google_client_id = os.getenv("GOOGLE_CLIENT_ID", "")
    return render_template("index.html", google_client_id=google_client_id)


@app.route("/chat", methods=["POST"])
def chat():
    """Chat endpoint supporting both guest users and saved database sessions."""
    data = request.get_json(silent=True) or {}
    message = data.get("message", "")
    session_id = data.get("session_id")

    if not isinstance(message, str) or not message.strip():
        return jsonify({
            "answer": "Please enter your question.",
            "reply": "Please enter your question.",
            "suggestions": [],
            "success": False,
        }), 400

    message = message.strip()
    user_id = session.get("user_id")

    # Retrieve user settings & custom instructions
    custom_instructions = ""
    answer_style = ""
    language = ""
    if user_id:
        user_settings = db.get_user_settings(user_id)
        if user_settings:
            custom_instructions = user_settings.get("custom_instructions", "")
            answer_style = user_settings.get("answer_style", "")
            language = user_settings.get("language", "")
    if not custom_instructions and data.get("custom_instructions"):
        custom_instructions = data.get("custom_instructions")
    if not answer_style and data.get("answer_style"):
        answer_style = data.get("answer_style")
    if not language and data.get("language"):
        language = data.get("language")

    # Load history
    history = []
    if session_id:
        db_msgs = db.get_session_messages(session_id)
        history = [{"role": m["role"], "text": m["text"]} for m in db_msgs]
    else:
        conv_key = user_id or request.remote_addr or "guest"
        history = guest_conversation_history[conv_key]

    key = get_api_key()
    has_valid_key = is_valid_format_key(key)

    # 1. When Gemini is unavailable / key not configured -> clean FAQ answer
    if not has_valid_key:
        faq_res = find_faq_answer(message)
        answer = faq_res["answer"]
        suggestions = faq_res.get("suggestions", [])

        # Persist to database if in a saved session
        if session_id:
            db.save_message(session_id, "user", message)
            db.save_message(session_id, "bot", answer)
        else:
            conv_key = user_id or request.remote_addr or "guest"
            guest_conversation_history[conv_key].append({"role": "user", "text": message})
            guest_conversation_history[conv_key].append({"role": "model", "text": answer})
            guest_conversation_history[conv_key] = guest_conversation_history[conv_key][-MAX_HISTORY_MESSAGES:]

        return jsonify({
            "answer": answer,
            "reply": answer,
            "suggestions": suggestions,
            "success": True,
            "mode": "faq_offline",
        }), 200

    # 2. When valid Gemini key configured -> Attempt AI generation
    try:
        answer, model_used = get_ai_answer(
            message=message,
            history=history,
            custom_instructions=custom_instructions,
            answer_style=answer_style,
            language=language
        )

        if session_id:
            db.save_message(session_id, "user", message)
            db.save_message(session_id, "bot", answer)
        else:
            conv_key = user_id or request.remote_addr or "guest"
            guest_conversation_history[conv_key].append({"role": "user", "text": message})
            guest_conversation_history[conv_key].append({"role": "model", "text": answer})
            guest_conversation_history[conv_key] = guest_conversation_history[conv_key][-MAX_HISTORY_MESSAGES:]

        return jsonify({
            "answer": answer,
            "reply": answer,
            "suggestions": [
                "Where can I apply?",
                "Official internship websites?",
                "Software internship",
                "Application guide",
            ],
            "success": True,
            "mode": f"gemini ({model_used})",
        }), 200

    except Exception as error:
        app.logger.exception("Gemini API call failed, gracefully serving FAQ answer")
        faq_res = find_faq_answer(message)
        base_answer = faq_res["answer"]
        suggestions = faq_res.get("suggestions", [])

        if session_id:
            db.save_message(session_id, "user", message)
            db.save_message(session_id, "bot", base_answer)
        else:
            conv_key = user_id or request.remote_addr or "guest"
            guest_conversation_history[conv_key].append({"role": "user", "text": message})
            guest_conversation_history[conv_key].append({"role": "model", "text": base_answer})
            guest_conversation_history[conv_key] = guest_conversation_history[conv_key][-MAX_HISTORY_MESSAGES:]

        return jsonify({
            "answer": base_answer,
            "reply": base_answer,
            "suggestions": suggestions,
            "success": True,
            "mode": "faq_fallback",
        }), 200


# --------------------------------------------------
# 7. Image Upload & Notice Analyzer
# --------------------------------------------------

@app.route("/api/upload-notice", methods=["POST"])
def upload_notice():
    """Validate image notice upload and analyze with Gemini Vision or local verifier."""
    if "notice" not in request.files and "file" not in request.files:
        return jsonify({"success": False, "error": "No image file provided."}), 400

    file = request.files.get("notice") or request.files.get("file")
    if not file or file.filename == "":
        return jsonify({"success": False, "error": "No file selected."}), 400

    filename = file.filename.lower()
    allowed_extensions = {".png", ".jpg", ".jpeg", ".webp"}
    file_ext = Path(filename).suffix

    if file_ext not in allowed_extensions:
        return jsonify({
            "success": False,
            "error": "Invalid file format. Please upload a PNG, JPG, JPEG, or WEBP image."
        }), 400

    # Read bytes into memory (do not permanently save on disk)
    image_bytes = file.read()
    file_size_kb = len(image_bytes) / 1024

    if len(image_bytes) > 5 * 1024 * 1024:
        return jsonify({
            "success": False,
            "error": "File size exceeds 5MB limit. Please upload a smaller image."
        }), 400

    mime_type = "image/png" if file_ext == ".png" else "image/jpeg"
    if file_ext == ".webp":
        mime_type = "image/webp"

    # Try Gemini Vision if key configured
    key = get_api_key()
    if is_valid_format_key(key):
        try:
            client = genai.Client(api_key=key)
            vision_prompt = (
                "You are an expert internship adviser analyzing an internship poster / notice screenshot.\n"
                "Extract and structure the following details in clean markdown:\n"
                "1. 🏢 **Company / Organization Name**:\n"
                "2. 🎯 **Internship Role & Domain**:\n"
                "3. 🎓 **Eligibility Criteria** (degree, year, required skills):\n"
                "4. 💰 **Stipend / Compensation & Duration**:\n"
                "5. 📅 **Application Deadline & Official Link / Contact**:\n"
                "6. 🛡️ **Scam & Red Flag Verification**:\n"
                "   - Does it ask for registration fees, training money, or security deposits? (Genuine internships NEVER charge money!)\n"
                "   - Verdict: [VERIFIED / CAUTION / SUSPICIOUS SCAM]\n"
                "   - Clear practical advice for the student.\n"
            )

            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[
                    types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
                    vision_prompt
                ]
            )
            analysis = (response.text or "").strip()
            if analysis:
                return jsonify({
                    "success": True,
                    "filename": file.filename,
                    "size_kb": round(file_size_kb, 1),
                    "analysis": analysis,
                    "mode": "gemini_vision"
                })
        except Exception as e:
            app.logger.warning("Gemini vision analysis failed, using local verifier: %s", e)

    # Local Intelligent Notice Verifier Checklist
    local_analysis = (
        f"📋 **Internship Notice Verification Report**\n\n"
        f"• **Uploaded File**: `{file.filename}` ({round(file_size_kb, 1)} KB)\n"
        f"• **Format**: `{file_ext.upper()}` — Validated successfully\n\n"
        f"**6-Point Authenticity & Verification Checklist:**\n\n"
        f"1. 🚫 **No Upfront Fees**: Genuine corporate and government internships **never** ask students for application fees, registration charges, or training deposits.\n"
        f"2. 🌐 **Official Domain Verification**: Confirm the email address ends with the official company domain (e.g. `@google.com`, `@tcs.com`, `@infosys.com`) rather than generic `@gmail.com` or `@yahoo.com`.\n"
        f"3. 💼 **Offer Letter Transparency**: Genuine internships provide a formal letter detailing stipend, working hours, and mentor details on company letterhead.\n"
        f"4. 🏛️ **Cross-Check with Official Portals**: Compare this notice with listings on the company's verified career portal in our **Company Portals** directory.\n"
        f"5. 💰 **Stipend Transparency**: Ensure stipend amounts and performance criteria are documented in writing before accepting.\n"
        f"6. 🛡️ **Free Government Alternatives**: You can also apply for verified government-backed internships directly on the [AICTE Internship Portal](https://internship.aicte-india.org/).\n"
    )

    return jsonify({
        "success": True,
        "filename": file.filename,
        "size_kb": round(file_size_kb, 1),
        "analysis": local_analysis,
        "mode": "local_checklist"
    })


# --------------------------------------------------
# 8. Directory & Search Endpoints
# --------------------------------------------------

@app.route("/api/companies", methods=["GET"])
def get_companies():
    """Return verified company career portals."""
    return jsonify({
        "success": True,
        "count": len(COMPANIES_DIRECTORY),
        "companies": COMPANIES_DIRECTORY
    })


@app.route("/api/categories", methods=["GET"])
def get_categories():
    """Return internship categories and learning roadmaps."""
    return jsonify({
        "success": True,
        "categories": INTERNSHIP_CATEGORIES
    })


@app.route("/api/search", methods=["GET"])
def search():
    """Unified search across FAQs, companies, categories, and user history."""
    q = request.args.get("q", "").strip().lower()
    if not q:
        return jsonify({
            "success": True,
            "faqs": [],
            "companies": [],
            "categories": [],
            "history": []
        })

    # Search FAQs
    matched_faqs = []
    for intent in FAQ_DATA.get("intents", []):
        patterns = intent.get("patterns", [])
        keywords = intent.get("keywords", {})
        answer = intent.get("answer", "")

        matches = any(q in p.lower() for p in patterns) or any(q in k.lower() for k in keywords) or (q in answer.lower())
        if matches:
            matched_faqs.append({
                "name": intent.get("name"),
                "title": patterns[0].title() if patterns else intent.get("name").replace("_", " ").title(),
                "snippet": answer[:140].replace("\n", " ") + "...",
                "query": patterns[0] if patterns else intent.get("name")
            })

    # Search Companies
    matched_companies = [
        c for c in COMPANIES_DIRECTORY
        if q in c["name"].lower() or q in c["category"].lower() or any(q in p.lower() for p in c["programs"])
    ]

    # Search Categories
    matched_categories = [
        cat for cat in INTERNSHIP_CATEGORIES
        if q in cat["title"].lower() or q in cat["skills"].lower() or q in cat["roles"].lower()
    ]

    # Search User History
    matched_history = []
    user_id = session.get("user_id")
    if user_id:
        matched_history = db.search_user_history(user_id, q)

    return jsonify({
        "success": True,
        "query": q,
        "faqs": matched_faqs[:6],
        "companies": matched_companies[:6],
        "categories": matched_categories[:4],
        "history": matched_history[:5]
    })


# --------------------------------------------------
# 9. Authentication & User Profile
# --------------------------------------------------

@app.route("/api/auth/google", methods=["POST"])
def google_auth():
    """Handle Google OAuth credential or demo sign-in."""
    data = request.get_json(silent=True) or {}
    email = data.get("email")
    name = data.get("name")
    picture = data.get("picture")
    google_id = data.get("google_id")
    credential = data.get("credential")

    # If real Google ID token received, parse payload
    if credential and not email:
        try:
            parts = credential.split(".")
            if len(parts) >= 2:
                padded = parts[1] + "=" * (-len(parts[1]) % 4)
                payload_json = base64.urlsafe_b64decode(padded).decode("utf-8")
                payload = json.loads(payload_json)
                google_id = payload.get("sub")
                email = payload.get("email")
                name = payload.get("name") or email.split("@")[0]
                picture = payload.get("picture") or ""
        except Exception as e:
            app.logger.warning("Could not parse Google credential: %s", e)

    if not email:
        email = f"student_{datetime.utcnow().strftime('%M%S')}@gmail.com"
    if not name:
        name = "Student"

    user = db.get_or_create_user(google_id=google_id, email=email, name=name, picture=picture)
    session["user_id"] = user["id"]

    return jsonify({
        "success": True,
        "user": user,
        "message": f"Welcome back, {user['name']}!"
    })


@app.route("/api/auth/me", methods=["GET"])
def get_current_user():
    """Return the currently authenticated user or guest state."""
    user_id = session.get("user_id")
    if user_id:
        user = db.get_user_by_id(user_id)
        if user:
            return jsonify({"logged_in": True, "user": user})

    return jsonify({"logged_in": False, "user": None})


@app.route("/api/auth/logout", methods=["POST"])
def logout():
    """Clear session on sign out."""
    session.clear()
    return jsonify({"success": True, "message": "Signed out successfully."})


# --------------------------------------------------
# 10. Chat History Persistence Endpoints
# --------------------------------------------------

@app.route("/api/history", methods=["GET"])
def list_history():
    """List all saved chat sessions for the active user."""
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"success": True, "sessions": []})

    sessions = db.get_user_sessions(user_id)
    return jsonify({"success": True, "sessions": sessions})


@app.route("/api/history", methods=["POST"])
def create_session():
    """Create a new chat conversation session."""
    user_id = session.get("user_id")
    data = request.get_json(silent=True) or {}
    title = data.get("title", "New Conversation")

    new_sess = db.create_chat_session(user_id=user_id, title=title)
    return jsonify({"success": True, "session": new_sess})


@app.route("/api/history/<session_id>", methods=["GET"])
def get_session_history(session_id):
    """Retrieve messages for a specific chat session."""
    messages = db.get_session_messages(session_id)
    return jsonify({"success": True, "session_id": session_id, "messages": messages})


@app.route("/api/history/<session_id>", methods=["PATCH"])
def rename_session_route(session_id):
    """Rename a conversation session."""
    user_id = session.get("user_id")
    data = request.get_json(silent=True) or {}
    new_title = data.get("title", "").strip()

    if not new_title:
        return jsonify({"success": False, "error": "Title cannot be empty."}), 400

    ok = db.rename_session(session_id, user_id, new_title)
    return jsonify({"success": ok})


@app.route("/api/history/<session_id>", methods=["DELETE"])
def delete_session_route(session_id):
    """Delete a conversation session."""
    user_id = session.get("user_id")
    ok = db.delete_session(session_id, user_id)
    return jsonify({"success": ok})



# --------------------------------------------------
# 11. Roadmaps & Personalized Recommendations
# --------------------------------------------------

@app.route("/api/roadmaps", methods=["GET"])
def get_roadmaps():
    """Return all 4 structured domain roadmaps."""
    return jsonify({
        "success": True,
        "categories": roadmaps_data.get_all_categories()
    })


@app.route("/api/roadmaps/<cat_id>", methods=["GET"])
def get_roadmap_by_category(cat_id):
    """Return roadmap, skills, and projects for a single domain."""
    cat = roadmaps_data.get_category_by_id(cat_id)
    if not cat:
        return jsonify({"success": False, "error": f"Category '{cat_id}' not found."}), 404
    return jsonify({"success": True, "category": cat})


@app.route("/api/recommendations", methods=["POST"])
def get_recommendations():
    """Generate personalized project recommendations with transparent reasons."""
    data = request.get_json(silent=True) or {}
    skills = data.get("skills", [])
    career_goal = data.get("career_goal", "")

    user_id = session.get("user_id")
    if user_id and not skills:
        user_settings = db.get_user_settings(user_id)
        if user_settings:
            current_skills_str = user_settings.get("current_skills", "")
            if current_skills_str:
                skills = [s.strip() for s in current_skills_str.split(",") if s.strip()]
            if not career_goal:
                career_goal = user_settings.get("career_goals", "")

    recs = roadmaps_data.get_recommendations_for_user(skills, career_goal)
    return jsonify({"success": True, "recommendations": recs})


# --------------------------------------------------
# 12. Settings & Custom Instructions Endpoints
# --------------------------------------------------

@app.route("/api/settings", methods=["GET"])
def get_settings():
    """Get user settings from SQLite if logged in, else return defaults."""
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({
            "success": True,
            "logged_in": False,
            "settings": {
                "theme": "system",
                "language": "en",
                "answer_style": "balanced",
                "default_category": "java",
                "experience_level": "Beginner",
                "career_goals": "Software Engineering Internship",
                "current_skills": "Java, Python, Git",
                "desired_skills": "Spring Boot, React, Docker",
                "learning_style": "Hands-on projects",
                "daily_learning_time": "1-2 hours",
                "custom_instructions": "",
                "memory_enabled": 1,
                "enter_to_send": 1,
                "notifications_enabled": 1,
                "font_size": "medium",
                "reduced_motion": 0,
                "contrast": "normal"
            }
        })

    user_settings = db.get_user_settings(user_id)
    return jsonify({
        "success": True,
        "logged_in": True,
        "settings": user_settings
    })


@app.route("/api/settings", methods=["POST"])
def save_settings():
    """Save user settings to SQLite if authenticated."""
    user_id = session.get("user_id")
    data = request.get_json(silent=True) or {}

    if not user_id:
        # Return success for guest with echoed settings so client can store in localStorage
        return jsonify({
            "success": True,
            "logged_in": False,
            "message": "Settings saved locally for guest session.",
            "settings": data
        })

    saved = db.save_user_settings(user_id, data)
    return jsonify({
        "success": True,
        "logged_in": True,
        "message": "Settings saved successfully to cloud.",
        "settings": saved
    })


# --------------------------------------------------
# 13. Memory Management Endpoints
# --------------------------------------------------

@app.route("/api/memory", methods=["GET"])
def list_memory():
    """List opt-in saved memory items."""
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"success": True, "logged_in": False, "memories": []})

    memories = db.get_user_memory(user_id)
    return jsonify({"success": True, "logged_in": True, "memories": memories})


@app.route("/api/memory", methods=["POST"])
def add_memory():
    """Add a new memory item."""
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"success": False, "error": "Sign in required to persist memory items."}), 401

    data = request.get_json(silent=True) or {}
    key = data.get("key", "").strip()
    value = data.get("value", "").strip()
    category = data.get("category", "preference").strip()

    if not key or not value:
        return jsonify({"success": False, "error": "Key and value are required."}), 400

    mem_id = db.add_user_memory(user_id, key, value, category)
    return jsonify({"success": True, "id": mem_id, "message": "Memory item saved."})


@app.route("/api/memory/<int:memory_id>", methods=["DELETE"])
def delete_memory_route(memory_id):
    """Delete a specific memory item."""
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"success": False, "error": "Authentication required."}), 401

    ok = db.delete_user_memory(memory_id, user_id)
    return jsonify({"success": ok})


@app.route("/api/memory/clear", methods=["POST"])
def clear_memory_route():
    """Clear all memory items for the user."""
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"success": False, "error": "Authentication required."}), 401

    ok = db.clear_user_memory(user_id)
    return jsonify({"success": ok, "message": "All memory items cleared."})


# --------------------------------------------------
# 14. Skill Progress Tracker Endpoints
# --------------------------------------------------

@app.route("/api/skill-progress", methods=["GET"])
def get_skill_progress():
    """Get user's skill progress map."""
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"success": True, "logged_in": False, "skills": {}, "rows": []})

    skills_rows = db.get_user_skill_progress(user_id)
    skills_map = {row["skill_name"]: row["status"] for row in skills_rows}
    return jsonify({"success": True, "logged_in": True, "skills": skills_map, "rows": skills_rows})


@app.route("/api/skill-progress", methods=["POST"])
def update_skill_progress_route():
    """Update status of a skill."""
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"success": False, "error": "Sign in required to save skill progress."}), 401

    data = request.get_json(silent=True) or {}
    category_id = data.get("category_id", "").strip()
    skill_name = data.get("skill_name", "").strip()
    status = data.get("status", "Not Started").strip()

    valid_statuses = {"Not Started", "Beginner", "Intermediate", "Advanced", "Completed"}
    if status not in valid_statuses:
        return jsonify({"success": False, "error": f"Invalid status '{status}'."}), 400

    if not skill_name:
        return jsonify({"success": False, "error": "Skill name is required."}), 400

    ok = db.update_skill_progress(user_id, category_id, skill_name, status)
    return jsonify({"success": ok, "category_id": category_id, "skill_name": skill_name, "status": status})


# --------------------------------------------------
# 15. Bookmarks & Application Tracker Endpoints
# --------------------------------------------------

@app.route("/api/bookmarks", methods=["GET"])
def get_bookmarks_route():
    """List saved internship bookmarks."""
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"success": True, "logged_in": False, "bookmarks": []})

    bmarks = db.get_bookmarks(user_id)
    return jsonify({"success": True, "logged_in": True, "bookmarks": bmarks})


@app.route("/api/bookmarks", methods=["POST"])
def add_bookmark_route():
    """Add a new bookmark."""
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"success": False, "error": "Sign in required to save bookmarks."}), 401

    data = request.get_json(silent=True) or {}
    company = data.get("company", "").strip()
    title = data.get("title", "").strip()
    url = data.get("url", "").strip()
    category = data.get("category", "").strip()
    notes = data.get("notes", "").strip()

    if not company or not title:
        return jsonify({"success": False, "error": "Company and role title are required."}), 400

    b_record = db.add_bookmark(user_id, company, title, url, category, notes)
    b_id = b_record["id"] if isinstance(b_record, dict) else b_record
    return jsonify({"success": True, "id": b_id, "bookmark": b_record, "message": "Bookmark saved."})


@app.route("/api/bookmarks/<bookmark_id>", methods=["DELETE"])
def delete_bookmark_route(bookmark_id):
    """Delete a bookmark."""
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"success": False, "error": "Authentication required."}), 401

    ok = db.delete_bookmark(bookmark_id, user_id)
    return jsonify({"success": ok})


@app.route("/api/applications", methods=["GET"])
def get_applications_route():
    """List tracked internship applications."""
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"success": True, "logged_in": False, "applications": []})

    apps = db.get_applications(user_id)
    return jsonify({"success": True, "logged_in": True, "applications": apps})


@app.route("/api/applications", methods=["POST"])
def add_application_route():
    """Add a tracked application."""
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"success": False, "error": "Sign in required to track applications."}), 401

    data = request.get_json(silent=True) or {}
    company = data.get("company", "").strip()
    role = data.get("role", "").strip()
    url = data.get("url", "").strip()
    category = data.get("category", "").strip()
    status = data.get("status", "Saved").strip()
    applied_date = data.get("applied_date", "")
    deadline = data.get("deadline", "")
    notes = data.get("notes", "").strip()
    followup_date = data.get("followup_date", "")

    if not company or not role:
        return jsonify({"success": False, "error": "Company and role are required."}), 400

    app_record = db.add_application(
        user_id=user_id,
        company=company,
        role=role,
        url=url,
        category=category,
        status=status,
        applied_date=applied_date,
        deadline=deadline,
        notes=notes,
        followup_date=followup_date
    )
    app_id = app_record["id"] if isinstance(app_record, dict) else app_record
    return jsonify({"success": True, "id": app_id, "application": app_record, "message": "Application tracked."})


@app.route("/api/applications/<app_id>", methods=["PATCH"])
def update_application_route(app_id):
    """Update fields on a tracked application."""
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"success": False, "error": "Authentication required."}), 401

    data = request.get_json(silent=True) or {}
    ok = db.update_application(app_id, user_id, data)
    return jsonify({"success": ok})


@app.route("/api/applications/<app_id>", methods=["DELETE"])
def delete_application_route(app_id):
    """Delete a tracked application."""
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"success": False, "error": "Authentication required."}), 401

    ok = db.delete_application(app_id, user_id)
    return jsonify({"success": ok})


# --------------------------------------------------
# 16. Reminders & Alerts Endpoints
# --------------------------------------------------

@app.route("/api/reminders", methods=["GET"])
def get_reminders_route():
    """List in-app reminders and alerts."""
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"success": True, "logged_in": False, "reminders": []})

    reminders = db.get_reminders(user_id)
    return jsonify({"success": True, "logged_in": True, "reminders": reminders})


@app.route("/api/reminders", methods=["POST"])
def add_reminder_route():
    """Add a new reminder."""
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"success": False, "error": "Sign in required to save reminders."}), 401

    data = request.get_json(silent=True) or {}
    title = data.get("title", "").strip()
    due_date = data.get("due_date", "").strip()
    reminder_type = data.get("reminder_type", "deadline").strip()
    related_id = data.get("related_id")

    if not title:
        return jsonify({"success": False, "error": "Reminder title is required."}), 400

    r_record = db.add_reminder(user_id, title, due_date, reminder_type, related_id)
    r_id = r_record["id"] if isinstance(r_record, dict) else r_record
    return jsonify({"success": True, "id": r_id, "reminder": r_record, "message": "Reminder created."})


@app.route("/api/reminders/<reminder_id>/toggle", methods=["PATCH"])
def toggle_reminder_route(reminder_id):
    """Toggle completed status of a reminder."""
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"success": False, "error": "Authentication required."}), 401

    ok = db.toggle_reminder(reminder_id, user_id)
    return jsonify({"success": ok})


@app.route("/api/reminders/<reminder_id>", methods=["DELETE"])
def delete_reminder_route(reminder_id):
    """Delete a reminder."""
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"success": False, "error": "Authentication required."}), 401

    ok = db.delete_reminder(reminder_id, user_id)
    return jsonify({"success": ok})


# --------------------------------------------------
# 17. Interview Practice & MCQs Endpoints
# --------------------------------------------------

@app.route("/api/interview-topics", methods=["GET"])
def get_interview_topics():
    """Return categories with topic MCQs and interview questions."""
    cats = roadmaps_data.get_all_categories()
    topics = []
    for c in cats:
        topics.append({
            "id": c["id"],
            "title": c["title"],
            "icon": c["icon"],
            "mcqs": c.get("mcqs", []),
            "interview_questions": c.get("interview_questions", [])
        })
    return jsonify({"success": True, "topics": topics})


@app.route("/api/submit-interview", methods=["POST"])
def submit_interview_score():
    """Save user's MCQ / Mock interview practice score."""
    data = request.get_json(silent=True) or {}
    topic = data.get("topic", "General").strip()
    score = int(data.get("score", 0))
    total = int(data.get("total", 0))
    percentage = float(data.get("percentage", 0.0))
    answers = data.get("answers", [])

    user_id = session.get("user_id")
    saved_id = None
    if user_id:
        saved_id = db.save_interview_score(user_id, topic, score, total, percentage, answers)

    return jsonify({
        "success": True,
        "saved": bool(saved_id),
        "id": saved_id,
        "topic": topic,
        "score": score,
        "total": total,
        "percentage": percentage
    })


@app.route("/api/interview-scores", methods=["GET"])
def get_interview_scores():
    """Get history of interview practice scores."""
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"success": True, "logged_in": False, "scores": []})

    scores = db.get_user_interview_scores(user_id)
    return jsonify({"success": True, "logged_in": True, "scores": scores})


# --------------------------------------------------
# 18. Resume Checker Endpoint
# --------------------------------------------------

@app.route("/api/check-resume", methods=["POST"])
def check_resume_endpoint():
    """Validate and analyze an uploaded resume (PDF, DOCX, TXT) up to 5MB in-memory."""
    if "resume" not in request.files and "file" not in request.files:
        return jsonify({"success": False, "error": "No resume file provided."}), 400

    file = request.files.get("resume") or request.files.get("file")
    if not file or file.filename == "":
        return jsonify({"success": False, "error": "No file selected."}), 400

    filename = file.filename.lower()
    allowed_exts = {".pdf", ".docx", ".txt"}
    ext = Path(filename).suffix

    if ext not in allowed_exts:
        return jsonify({
            "success": False,
            "error": "Invalid format. Please upload a PDF, DOCX, or TXT resume."
        }), 400

    target_category = request.form.get("category", "general")

    try:
        text = resume_checker.extract_text_from_file(file)
        analysis = resume_checker.analyze_resume_text(text, target_category=target_category)
        if not analysis.get("success"):
            return jsonify(analysis), 400

        analysis["filename"] = file.filename
        return jsonify(analysis), 200
    except Exception as e:
        app.logger.exception("Resume checking error: %s", e)
        return jsonify({"success": False, "error": f"Failed to parse resume: {str(e)}"}), 500


# --------------------------------------------------
# 19. Data Controls & Account Deletion Endpoints
# --------------------------------------------------

@app.route("/api/export-data", methods=["GET"])
def export_user_data_route():
    """Export complete user data (conversations, settings, progress, bookmarks)."""
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"success": False, "error": "Sign in required to export cloud data."}), 401

    export = db.export_user_data(user_id)
    return jsonify(export)


@app.route("/api/delete-account", methods=["POST"])
def delete_account_route():
    """Permanently delete user account and associated personal data."""
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"success": False, "error": "Authentication required."}), 401

    db.delete_user_account(user_id)
    session.clear()
    return jsonify({"success": True, "message": "Account and all associated data permanently deleted."})


# --------------------------------------------------
# 20. Gemini Connection Diagnostics Endpoint
# --------------------------------------------------

@app.route("/api/test-gemini", methods=["POST"])
def test_gemini():
    """Test Gemini connection with the configured API key and return real diagnostics."""
    key = get_api_key()
    if not key or is_placeholder_key(key):
        return jsonify({
            "success": False,
            "connected": False,
            "error": "No API key configured or key is still a placeholder in .env.",
            "message": "Add a valid GEMINI_API_KEY from Google AI Studio to .env to enable live AI responses."
        })
    if not is_valid_format_key(key):
        return jsonify({
            "success": False,
            "connected": False,
            "error": f"API key format looks invalid (length {len(key)}, expected ~39 chars starting with AIza).",
            "message": "Please double-check your API key from Google AI Studio."
        })

    try:
        client = genai.Client(api_key=key)
        resp = client.models.generate_content(
            model="gemini-2.5-flash",
            contents="Say 'OK'",
            config=types.GenerateContentConfig(max_output_tokens=10)
        )
        return jsonify({
            "success": True,
            "connected": True,
            "model": "gemini-2.5-flash",
            "message": "Gemini connection active and verified successfully!",
            "response_preview": (resp.text or "").strip()
        })
    except Exception as e:
        app.logger.warning("Gemini live test failed: %s", e)
        return jsonify({
            "success": False,
            "connected": False,
            "error": str(e),
            "message": "Gemini rejected the connection (invalid key, closed quota, or network block)."
        })


# --------------------------------------------------
# 21. Backend Health Check
# --------------------------------------------------

@app.route("/test", methods=["GET"])
def test():
    key = get_api_key()
    placeholder = is_placeholder_key(key)
    valid_format = is_valid_format_key(key)

    if not key:
        status_msg = "No API key configured (Running in Offline FAQ mode)"
    elif placeholder:
        status_msg = "Placeholder key detected (Running in Offline FAQ mode)"
    elif not valid_format:
        status_msg = f"Key format invalid: length {len(key)} (Running in Offline FAQ mode)"
    else:
        status_msg = f"API Key formatted properly (length {len(key)}). Ready for Gemini AI requests."

    return jsonify({
        "status": "success",
        "flask_running": True,
        "api_key_configured": bool(key) and not placeholder,
        "api_key_length": len(key) if key else 0,
        "is_placeholder": placeholder,
        "is_valid_format": valid_format,
        "mode": "gemini" if valid_format else "faq_offline",
        "faq_intents_loaded": len(FAQ_DATA.get("intents", [])),
        "companies_loaded": len(COMPANIES_DIRECTORY),
        "categories_loaded": len(INTERNSHIP_CATEGORIES),
        "message": status_msg,
    })


# --------------------------------------------------
# 12. Run the application
# --------------------------------------------------

if __name__ == "__main__":
    # Disable the reloader to prevent endless reload loops caused by venv or scratch files
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False,
    )
