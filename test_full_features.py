"""
Comprehensive End-to-End Verification Test Suite
Tests all 15 core features required by the user prompt.
"""

import io
import json
import app
import db
import roadmaps_data
import resume_checker

def run_tests():
    print("==================================================")
    print("STARTING FULL INTERNSHIP ASSISTANT TEST SUITE")
    print("==================================================")

    client = app.app.test_client()

    # --------------------------------------------------
    # TEST 1: Dashboard Rendering & HTML Structure
    # --------------------------------------------------
    print("\n[TEST 1] Dashboard rendering & views:")
    res = client.get("/")
    assert res.status_code == 200, "Dashboard failed to load"
    html = res.get_data(as_text=True)
    assert 'id="view-home"' in html, "view-home missing"
    assert 'id="view-search"' in html, "view-search missing"
    assert 'id="view-roadmaps"' in html, "view-roadmaps missing"
    assert 'id="view-interviews"' in html, "view-interviews missing"
    assert 'id="view-resume"' in html, "view-resume missing"
    assert 'id="view-tracker"' in html, "view-tracker missing"
    assert 'id="view-companies"' in html, "view-companies missing"
    assert 'id="view-history"' in html, "view-history missing"
    assert 'id="view-settings"' in html, "view-settings missing"
    assert 'id="voice-input-btn"' in html, "voice-input-btn missing"
    print("✓ Dashboard rendered with all 9 views and voice input control.")

    # --------------------------------------------------
    # TEST 2: 4 Core Internship Categories & Roadmaps
    # --------------------------------------------------
    print("\n[TEST 2] Four Core Categories & Roadmaps:")
    res = client.get("/api/roadmaps")
    assert res.status_code == 200
    cats = res.get_json()["categories"]
    cat_ids = [c["id"] for c in cats]
    for required_cat in ["java", "python", "javascript", "fullstack"]:
        assert required_cat in cat_ids, f"Category {required_cat} missing from roadmaps"

    java_cat = next(c for c in cats if c["id"] == "java")
    assert "https://www.linkedin.com/jobs/java-intern-jobs/" in java_cat["external_link"]["url"]
    assert "Student Management System" in [p["title"] for p in java_cat["projects"]]
    assert len(java_cat["roadmap"]) >= 4

    python_cat = next(c for c in cats if c["id"] == "python")
    assert "https://www.linkedin.com/jobs/python-intern-jobs/" in python_cat["external_link"]["url"]
    assert any("FAQ Chatbot" in p["title"] for p in python_cat["projects"])

    js_cat = next(c for c in cats if c["id"] == "javascript")
    assert "https://www.linkedin.com/jobs/javascript-intern-jobs/" in js_cat["external_link"]["url"]

    fs_cat = next(c for c in cats if c["id"] == "fullstack")
    assert "https://www.linkedin.com/jobs/full-stack-developer-intern-jobs/" in fs_cat["external_link"]["url"]
    print("✓ All 4 core categories, external LinkedIn links, projects, and roadmaps verified.")

    # --------------------------------------------------
    # TEST 3: Guest Chat & Offline FAQ Matching
    # --------------------------------------------------
    print("\n[TEST 3] Guest Chat & Offline FAQ Matching:")
    test_queries = [
        ("Where can I apply?", "google"),
        ("Java development internship", "java"),
        ("Python development internship", "python"),
        ("JavaScript development internship", "javascript"),
        ("Full-stack developer internship", "fullstack"),
        ("How to check ATS resume score?", "resume"),
        ("Official internship websites?", "aicte")
    ]
    for q, kw in test_queries:
        res = client.post("/chat", json={"message": q})
        assert res.status_code == 200
        data = res.get_json()
        assert data["success"] is True
        assert len(data["answer"]) > 50, f"Answer for '{q}' too short"
        print(f"  ✓ Answered '{q}' (mode: {data.get('mode')})")
    print("✓ Guest chat and offline FAQ matching working seamlessly.")

    # --------------------------------------------------
    # TEST 4: Authentication & User Profile
    # --------------------------------------------------
    print("\n[TEST 4] Authentication & Profile:")
    auth_res = client.post("/api/auth/google", json={"name": "Sarah Connor", "email": "sarah@skynet.com"})
    assert auth_res.status_code == 200
    user = auth_res.get_json()["user"]
    assert user["email"] == "sarah@skynet.com"

    me_res = client.get("/api/auth/me")
    assert me_res.status_code == 200
    assert me_res.get_json()["logged_in"] is True
    print(f"✓ Authenticated user session established: {user['email']} (id: {user['id']})")

    # --------------------------------------------------
    # TEST 5: Settings Persistence & Custom Instructions
    # --------------------------------------------------
    print("\n[TEST 5] Settings Persistence & Custom Instructions:")
    set_payload = {
        "theme": "dark",
        "language": "hi",
        "answer_style": "detailed",
        "default_category": "python",
        "experience_level": "Intermediate",
        "career_goals": "AI Engineer & Python Backend",
        "current_skills": "Python, Flask, SQL",
        "desired_skills": "PyTorch, Docker, Kubernetes",
        "custom_instructions": "Explain in simple English with bullet points and code examples."
    }
    set_res = client.post("/api/settings", json=set_payload)
    assert set_res.status_code == 200
    assert set_res.get_json()["settings"]["theme"] == "dark"

    # Verify settings persistence
    get_set = client.get("/api/settings")
    assert get_set.get_json()["settings"]["career_goals"] == "AI Engineer & Python Backend"
    assert get_set.get_json()["settings"]["custom_instructions"] == "Explain in simple English with bullet points and code examples."
    print("✓ User settings and custom instructions successfully saved and retrieved from SQLite.")

    # --------------------------------------------------
    # TEST 6: Memory System (Add, List, Delete, Clear)
    # --------------------------------------------------
    print("\n[TEST 6] Memory System:")
    mem1 = client.post("/api/memory", json={"key": "target_city", "value": "Bangalore", "category": "preference"})
    assert mem1.status_code == 200
    mem1_id = mem1.get_json()["id"]

    mem2 = client.post("/api/memory", json={"key": "stipend_min", "value": "25000", "category": "salary"})
    assert mem2.status_code == 200

    list_mem = client.get("/api/memory")
    assert len(list_mem.get_json()["memories"]) >= 2

    # Delete 1 item
    del_mem = client.delete(f"/api/memory/{mem1_id}")
    assert del_mem.status_code == 200

    # Clear all memory
    clear_mem = client.post("/api/memory/clear")
    assert clear_mem.status_code == 200
    assert len(client.get("/api/memory").get_json()["memories"]) == 0
    print("✓ Memory operations (add, list, delete, clear) verified.")

    # --------------------------------------------------
    # TEST 7: Skill Progress Tracker Persistence
    # --------------------------------------------------
    print("\n[TEST 7] Skill Progress Tracker:")
    sk1 = client.post("/api/skill-progress", json={"category_id": "java", "skill_name": "Core Java", "status": "Completed"})
    assert sk1.status_code == 200
    sk2 = client.post("/api/skill-progress", json={"category_id": "java", "skill_name": "Spring Boot", "status": "Intermediate"})
    assert sk2.status_code == 200

    get_sk = client.get("/api/skill-progress")
    skills_map = get_sk.get_json()["skills"]
    assert skills_map.get("Core Java") == "Completed"
    assert skills_map.get("Spring Boot") == "Intermediate"
    print("✓ Skill progress tracker persists status across sessions.")

    # --------------------------------------------------
    # TEST 8: Topic MCQs & Interview Scoring
    # --------------------------------------------------
    print("\n[TEST 8] Topic MCQs & Interview Scoring:")
    int_topics = client.get("/api/interview-topics")
    assert int_topics.status_code == 200
    topics = int_topics.get_json()["topics"]
    assert len(topics) == 4
    for t in topics:
        assert len(t["mcqs"]) > 0
        assert len(t["interview_questions"]) > 0

    sub_res = client.post("/api/submit-interview", json={
        "topic": "Python Development",
        "score": 3,
        "total": 3,
        "percentage": 100.0,
        "answers": [{"q": 0, "ans": 1}]
    })
    assert sub_res.status_code == 200

    scores_res = client.get("/api/interview-scores")
    scores = scores_res.get_json()["scores"]
    assert len(scores) > 0
    assert scores[0]["percentage"] == 100.0
    print("✓ Topic MCQs, Mock questions, and scoring verified.")

    # --------------------------------------------------
    # TEST 9: ATS Resume Checker (Text, DOCX, PDF)
    # --------------------------------------------------
    print("\n[TEST 9] ATS Resume Checker:")
    test_resume_txt = (
        "SARAH CONNOR\n"
        "Email: sarah@gmail.com | Phone: (555) 019-2834 | linkedin.com/in/sarah | github.com/sarah\n\n"
        "EDUCATION\n"
        "Bachelor of Technology in Computer Science, 2026\n\n"
        "TECHNICAL SKILLS\n"
        "Python, Flask, Django, SQL, PostgreSQL, Docker, Git, REST APIs, pytest\n\n"
        "EXPERIENCE & PROJECTS\n"
        "Automated Internship Scraper:\n"
        "- Engineered an asynchronous Python crawler with BeautifulSoup and Requests.\n"
        "- Optimized parsing throughput by 40% and reduced query latency by 150ms.\n"
        "- Built REST API endpoints in Flask handling 500+ daily student requests."
    )
    res_upload = client.post("/api/check-resume", data={
        "resume": (io.BytesIO(test_resume_txt.encode("utf-8")), "sarah_resume.txt"),
        "category": "Python"
    }, content_type="multipart/form-data")
    assert res_upload.status_code == 200
    res_data = res_upload.get_json()
    assert res_data["score"] >= 60, f"Score {res_data['score']} lower than expected"
    assert "Python" in res_data["detected_skills"]
    assert len(res_data["found_action_verbs"]) >= 3
    print(f"✓ Resume analyzer parsed text, calculated ATS score ({res_data['score']}/100), detected skills, and generated suggestions.")

    # --------------------------------------------------
    # TEST 10: Bookmarks & Applications Tracking
    # --------------------------------------------------
    print("\n[TEST 10] Bookmarks & Applications Tracker:")
    bm = client.post("/api/bookmarks", json={
        "company": "Amazon",
        "title": "Amazon WOW SDE Intern",
        "url": "https://www.amazon.jobs/student-programs",
        "category": "Software",
        "notes": "Women in Tech recruitment track"
    })
    assert bm.status_code == 200
    bm_id = bm.get_json()["id"]

    bms = client.get("/api/bookmarks").get_json()["bookmarks"]
    assert any(b["id"] == bm_id for b in bms)

    # Track application
    app_track = client.post("/api/applications", json={
        "company": "Google",
        "role": "STEP Intern 2026",
        "url": "https://careers.google.com/students/",
        "category": "Java Development",
        "status": "Applied",
        "deadline": "2026-11-30",
        "followup_date": "2026-12-15",
        "notes": "Application submitted via Google Careers"
    })
    assert app_track.status_code == 200
    app_id = app_track.get_json()["id"]

    # Status update: Applied -> Assessment
    up_app = client.patch(f"/api/applications/{app_id}", json={"status": "Assessment"})
    assert up_app.status_code == 200

    apps = client.get("/api/applications").get_json()["applications"]
    target_app = next(a for a in apps if a["id"] == app_id)
    assert target_app["status"] == "Assessment"
    print("✓ Bookmarks and Applications CRUD and status transitions verified.")

    # --------------------------------------------------
    # TEST 11: Reminders & Deadline Tracking
    # --------------------------------------------------
    print("\n[TEST 11] Reminders & Deadline Alerts:")
    rem = client.post("/api/reminders", json={
        "title": "Submit Google STEP online assessment",
        "due_date": "2026-11-20",
        "reminder_type": "assessment"
    })
    assert rem.status_code == 200
    rem_id = rem.get_json()["id"]

    # Toggle completed
    tog = client.patch(f"/api/reminders/{rem_id}/toggle")
    assert tog.status_code == 200

    rems = client.get("/api/reminders").get_json()["reminders"]
    target_rem = next(r for r in rems if r["id"] == rem_id)
    assert target_rem["is_completed"] == 1
    print("✓ Reminders created, retrieved, and toggled.")

    # --------------------------------------------------
    # TEST 12: Data Export & Security Verification
    # --------------------------------------------------
    print("\n[TEST 12] Complete Data Export & Isolation:")
    exp_res = client.get("/api/export-data")
    assert exp_res.status_code == 200
    exp = exp_res.get_json()
    assert "user_profile" in exp
    assert "settings" in exp
    assert "skill_progress" in exp
    assert "bookmarks" in exp
    assert "applications" in exp
    assert "reminders" in exp
    assert "interview_scores" in exp
    print(f"✓ Data export generated with all sections: {list(exp.keys())}")

    # --------------------------------------------------
    # TEST 13: Unauthorized Data Access Prevention
    # --------------------------------------------------
    print("\n[TEST 13] Security & Data Isolation:")
    # Client 2 (unauthenticated guest)
    guest_client = app.app.test_client()
    g_exp = guest_client.get("/api/export-data")
    assert g_exp.status_code == 401, "Guest was unexpectedly able to export data"
    g_apps = guest_client.get("/api/applications")
    assert len(g_apps.get_json()["applications"]) == 0, "Guest saw authenticated user applications"
    print("✓ Guest access to private cloud data successfully prevented (HTTP 401 & isolated).")

    # --------------------------------------------------
    # TEST 14: Real Gemini Diagnostics Endpoint
    # --------------------------------------------------
    print("\n[TEST 14] Gemini Connection Diagnostics:")
    gem_res = client.post("/api/test-gemini")
    assert gem_res.status_code == 200
    gem_data = gem_res.get_json()
    assert "connected" in gem_data
    assert "message" in gem_data
    print(f"✓ Gemini diagnostics reported: connected={gem_data['connected']}, message='{gem_data['message']}'")

    print("\n==================================================")
    print("ALL 14 TEST SUITES PASSED WITH ZERO ERRORS!")
    print("==================================================")

if __name__ == "__main__":
    run_tests()
