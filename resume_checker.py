"""
Resume Checker Engine for Internship FAQ Assistant.
Provides:
- Secure text extraction from PDF, DOCX, and TXT files
- In-memory parsing without storing user files on disk
- ATS keyword detection across Java, Python, JavaScript, Full-Stack, and Data Science
- Section detection (Education, Skills, Experience, Projects, Certifications)
- Action verb analysis, metric/quantifiable impact detection
- ATS score calculation (0 - 100) and actionable bulleted suggestions
"""

import io
import re
from pathlib import Path

# Core skills database for extraction
DOMAIN_KEYWORDS = {
    "Java": ["java", "spring boot", "spring", "hibernate", "jdbc", "jpa", "maven", "gradle", "junit", "mockito", "multithreading", "oop", "jvm"],
    "Python": ["python", "flask", "django", "fastapi", "pandas", "numpy", "scikit-learn", "pytest", "beautifulsoup", "selenium", "sqlalchemy"],
    "JavaScript & Frontend": ["javascript", "es6", "react", "next.js", "vue", "typescript", "html", "html5", "css", "css3", "tailwind", "redux", "node.js", "express"],
    "Databases & Cloud": ["sql", "mysql", "postgresql", "mongodb", "sqlite", "redis", "docker", "git", "github", "aws", "azure", "ci/cd", "rest api", "linux"],
    "Soft Skills & Process": ["agile", "scrum", "problem solving", "communication", "team collaboration", "leadership", "critical thinking"]
}

ACTION_VERBS = [
    "developed", "designed", "implemented", "built", "engineered", "optimized",
    "created", "spearheaded", "integrated", "managed", "deployed", "refactored",
    "collaborated", "automated", "reduced", "increased", "accelerated", "resolved"
]

ESSENTIAL_SECTIONS = {
    "education": ["education", "academic", "university", "college", "degree", "b.tech", "b.e", "bca", "mca", "b.sc"],
    "skills": ["skills", "technical skills", "technologies", "proficiencies", "core competencies"],
    "experience": ["experience", "work experience", "internship", "employment", "professional experience"],
    "projects": ["projects", "personal projects", "academic projects", "key projects"],
    "contact": ["email", "phone", "linkedin", "github", "portfolio", "contact"]
}


def extract_text_from_file(file_storage):
    """
    Extract text from uploaded FileStorage object in-memory.
    Supports PDF, DOCX, and TXT.
    """
    filename = file_storage.filename or ""
    ext = Path(filename).suffix.lower()
    stream = io.BytesIO(file_storage.read())

    text = ""
    if ext == ".txt":
        try:
            text = stream.getvalue().decode("utf-8", errors="ignore")
        except Exception as e:
            text = str(stream.getvalue())

    elif ext == ".pdf":
        try:
            import pypdf
            reader = pypdf.PdfReader(stream)
            extracted = []
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    extracted.append(page_text)
            text = "\n".join(extracted)
        except Exception as e:
            raise ValueError(f"Could not parse PDF file: {e}")

    elif ext in [".docx", ".doc"]:
        try:
            import docx
            doc = docx.Document(stream)
            extracted = [para.text for para in doc.paragraphs if para.text]
            for table in doc.tables:
                for row in table.rows:
                    for cell in row.cells:
                        if cell.text.strip():
                            extracted.append(cell.text.strip())
            text = "\n".join(extracted)
        except Exception as e:
            raise ValueError(f"Could not parse DOCX file: {e}")

    else:
        raise ValueError(f"Unsupported file format '{ext}'. Allowed: .pdf, .docx, .txt")

    return text.strip()


def analyze_resume_text(text, target_category="general"):
    """
    Analyze resume text and return structured ATS metrics, detected skills,
    missing keywords, score, and clear actionable improvements.
    """
    if not text or len(text.strip()) < 50:
        return {
            "success": False,
            "error": "Resume text is too short or empty. Please ensure the file contains legible text (not a scanned image)."
        }

    lower_text = text.lower()
    words = re.findall(r"\b[a-z0-9+#.-]+\b", lower_text)
    word_count = len(words)

    # 1. Detect Found Skills
    detected_skills = {}
    total_skills_found = 0
    for domain, skill_list in DOMAIN_KEYWORDS.items():
        matched = []
        for skill in skill_list:
            # Word boundary matching
            pattern = r"\b" + re.escape(skill) + r"\b"
            if re.search(pattern, lower_text):
                matched.append(skill.title() if len(skill) > 4 else skill.upper())
        if matched:
            detected_skills[domain] = matched
            total_skills_found += len(matched)

    # 2. Check for Sections
    found_sections = []
    missing_sections = []
    for section, triggers in ESSENTIAL_SECTIONS.items():
        if any(trig in lower_text for trig in triggers):
            found_sections.append(section.title())
        else:
            missing_sections.append(section.title())

    # 3. Action Verbs & Metrics Check
    found_action_verbs = []
    for verb in ACTION_VERBS:
        if re.search(r"\b" + re.escape(verb) + r"\b", lower_text):
            found_action_verbs.append(verb)

    # Quantifiable numbers check (percentages, metrics, multipliers like 20%, 5x, $500, 100+ users)
    metrics_matches = re.findall(r"\b\d+[%+xXkK]?\b|\$\d+", text)
    has_metrics = len(metrics_matches) >= 3

    # 4. Contact Details Verification
    has_email = bool(re.search(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", text))
    has_phone = bool(re.search(r"(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}", text))
    has_github_or_linkedin = "linkedin.com" in lower_text or "github.com" in lower_text

    # 5. Calculate ATS Score (0 to 100)
    score = 0
    # Length / word count (ideal 300 - 800 words for intern): 15 pts
    if 250 <= word_count <= 1000:
        score += 15
    elif 150 <= word_count < 250 or 1000 < word_count <= 1400:
        score += 8
    else:
        score += 4

    # Sections (5 sections * 6 pts): 30 pts
    score += len(found_sections) * 6

    # Technical Skills found: up to 25 pts
    score += min(25, total_skills_found * 2)

    # Action verbs: up to 10 pts
    score += min(10, len(found_action_verbs) * 2)

    # Quantifiable metrics: 10 pts
    if has_metrics:
        score += 10
    elif len(metrics_matches) > 0:
        score += 5

    # Contact & Links: 10 pts
    if has_email: score += 4
    if has_phone: score += 3
    if has_github_or_linkedin: score += 3

    score = min(100, max(15, score))

    # 6. Actionable Improvement Suggestions
    suggestions = []
    if "Experience" in missing_sections and "Projects" in missing_sections:
        suggestions.append("Add a dedicated **Projects** or **Work Experience** section highlighting 2-3 substantial projects.")
    if "Skills" in missing_sections:
        suggestions.append("Create a distinct **Technical Skills** section categorized by Languages, Frameworks, and Tools for ATS scanners.")
    if not has_metrics:
        suggestions.append("Quantify your impact using numbers and percentages (e.g. *'Improved API response time by 35%'* or *'Handled 500+ daily queries'*).")
    if len(found_action_verbs) < 3:
        suggestions.append("Begin project bullet points with strong past-tense action verbs like *'Engineered'*, *'Architected'*, *'Developed'*, or *'Deployed'*.")
    if not has_github_or_linkedin:
        suggestions.append("Include active **GitHub** and **LinkedIn** profile links at the top of your resume.")
    if word_count < 250:
        suggestions.append("Your resume appears brief. Add more technical depth to your project descriptions and responsibilities.")
    elif word_count > 900:
        suggestions.append("Keep your resume concise: ideally a single page (400-700 words) for student and entry-level internship roles.")

    # 7. Category Specific Missing Keywords
    target_lower = target_category.lower()
    recommended_keywords = []
    if "java" in target_lower:
        recommended_keywords = ["Spring Boot", "REST APIs", "SQL / Hibernate", "JUnit", "Git", "OOP"]
    elif "python" in target_lower:
        recommended_keywords = ["Python", "Flask / Django", "REST APIs", "SQLAlchemy", "Pytest", "Git"]
    elif "javascript" in target_lower or "front" in target_lower:
        recommended_keywords = ["JavaScript (ES6+)", "React", "HTML5 / CSS3", "Fetch / Axios", "Git", "Node.js"]
    elif "full" in target_lower:
        recommended_keywords = ["React", "Node.js / Express / Spring", "PostgreSQL / MongoDB", "REST APIs", "JWT Auth", "Docker"]
    else:
        recommended_keywords = ["Git / GitHub", "REST APIs", "SQL", "Unit Testing", "Problem Solving"]

    missing_keywords = [
        kw for kw in recommended_keywords
        if not re.search(r"\b" + re.escape(kw.lower().split()[0]) + r"\b", lower_text)
    ]

    return {
        "success": True,
        "score": score,
        "word_count": word_count,
        "found_sections": found_sections,
        "missing_sections": missing_sections,
        "detected_skills": detected_skills,
        "total_skills_count": total_skills_found,
        "found_action_verbs": found_action_verbs[:8],
        "has_metrics": has_metrics,
        "has_contact": {"email": has_email, "phone": has_phone, "links": has_github_or_linkedin},
        "suggestions": suggestions,
        "recommended_keywords": recommended_keywords,
        "missing_keywords": missing_keywords
    }
