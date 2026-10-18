/**
 * Internship FAQ Assistant — Full Dashboard Logic & Features
 * Handles:
 * - View Navigation & Mobile Sidebar
 * - Voice Input (Speech Recognition) & Text-to-Speech Output
 * - Markdown Message Formatting with Copy & Regenerate Actions
 * - Unified Search across FAQs, 4 Categories, and Company Portals
 * - 4 Categories & Step-by-Step Roadmaps with Skill Progress Tracking
 * - Technical Interview Preparation: Topic MCQs & Mock Q&A Flashcards
 * - ATS Resume Checker with In-Memory Text Extraction & Scoring
 * - Application Tracker with Status Workflow, Bookmarks, and Reminders
 * - ChatGPT-Inspired 13-Section Settings Page with Theme, Memory, and Controls
 * - Google Identity OAuth & Demo Authentication
 */

// Global State
let currentSessionId = null;
let currentUser = null;
let currentSettings = {
    theme: "light",
    language: "en",
    answer_style: "balanced",
    default_category: "java",
    experience_level: "Beginner",
    career_goals: "Software Engineering Internship",
    current_skills: "Java, Python, Git",
    desired_skills: "Spring Boot, React, Docker",
    learning_style: "Hands-on projects",
    daily_learning_time: "1-2 hours",
    custom_instructions: "",
    memory_enabled: 1,
    enter_to_send: 1,
    delete_confirmation: 1,
    notifications_enabled: 1,
    font_size: "medium",
    reduced_motion: 0,
    contrast: "normal"
};

let userSkillProgress = {};
let roadmapsCache = [];
let activeRoadmapCat = "java";
let companiesCache = [];
let lastUserMessage = "";
let speechRecognizer = null;
let isRecording = false;

// Interview / MCQ Quiz State
let quizTopicsCache = [];
let activeQuizTopic = "java";
let currentQuizQuestions = [];
let currentQuizIndex = 0;
let userQuizScore = 0;
let userQuizAnswers = [];
let quizSubmitted = false;

// DOM Elements
const sidebar = document.getElementById("sidebar");
const mobileMenuBtn = document.getElementById("mobile-menu-btn");
const sidebarCloseBtn = document.getElementById("sidebar-close-btn");
const topbarHeading = document.getElementById("topbar-heading");
const navItems = document.querySelectorAll(".nav-item");
const viewPanels = document.querySelectorAll(".view-panel");

// Chat Elements
const chatBox = document.getElementById("chat-box");
const chatForm = document.getElementById("chat-form");
const messageInput = document.getElementById("message");
const sendBtn = document.getElementById("send-btn");
const suggestionsBox = document.getElementById("suggestions");
const newChatTopBtn = document.getElementById("new-chat-top-btn");
const voiceInputBtn = document.getElementById("voice-input-btn");

// Hero & Quick Actions
const heroSearchInput = document.getElementById("hero-search-input");
const quickCards = document.querySelectorAll(".quick-card");

// Auth Elements
const authGuestBox = document.getElementById("auth-guest-box");
const authUserBox = document.getElementById("auth-user-box");
const userNameDisplay = document.getElementById("user-name-display");
const userEmailDisplay = document.getElementById("user-email-display");
const userAvatarImg = document.getElementById("user-avatar-img");
const demoSigninBtn = document.getElementById("demo-signin-btn");
const logoutBtn = document.getElementById("logout-btn");

// Search View
const searchViewInput = document.getElementById("search-view-input");
const searchFilterPills = document.querySelectorAll(".filter-pill");
const searchResultsContainer = document.getElementById("search-results-container");

// Companies View
const companiesGrid = document.getElementById("companies-grid");
const companiesFilterBar = document.getElementById("companies-filter-bar");

// History View
const historyContainer = document.getElementById("history-container");

// Default Fallback Suggestions
const DEFAULT_SUGGESTIONS = [
    "Where can I apply?",
    "Java development internship",
    "Python development internship",
    "JavaScript development internship",
    "Full-stack developer internship",
    "Official internship websites?",
    "How to check ATS resume score?"
];

const WELCOME_MESSAGE = "Hello! 👋 I'm your Internship Assistant.\nAsk me about **Java, Python, JavaScript, Full-Stack internships**, company career portals (Google, Microsoft, Amazon, TCS), eligibility, stipends, or resume improvement.";


/* ==================================================
 * 1. View Navigation & Routing
 * ================================================== */

function switchView(viewName) {
    viewPanels.forEach(panel => {
        panel.classList.toggle("active", panel.id === `view-${viewName}`);
    });

    navItems.forEach(item => {
        item.classList.toggle("active", item.getAttribute("data-view") === viewName);
    });

    const titles = {
        home: "Internship FAQ Assistant",
        search: "Search Knowledge Base & Portals",
        roadmaps: "Categories & Learning Roadmaps",
        interviews: "Technical Interview Practice & MCQs",
        resume: "ATS Resume Checker",
        tracker: "Applications & Bookmarks Tracker",
        companies: "Official Company Career Portals",
        history: "Saved Chat History",
        settings: "Settings & Preferences"
    };

    if (topbarHeading) topbarHeading.textContent = titles[viewName] || "Internship FAQ Assistant";

    if (sidebar && sidebar.classList.contains("open")) {
        sidebar.classList.remove("open");
    }

    // Lazy load data for selected view
    if (viewName === "companies" && companiesCache.length === 0) loadCompanies();
    if (viewName === "roadmaps") loadRoadmapsView();
    if (viewName === "interviews") loadInterviewTopics();
    if (viewName === "tracker") loadTrackerView();
    if (viewName === "history") loadHistory();
    if (viewName === "settings") loadSettingsView();
    if (viewName === "search" && searchViewInput) searchViewInput.focus();
}

navItems.forEach(btn => {
    btn.addEventListener("click", () => {
        const view = btn.getAttribute("data-view");
        switchView(view);
    });
});

if (mobileMenuBtn) {
    mobileMenuBtn.addEventListener("click", () => sidebar.classList.add("open"));
}
if (sidebarCloseBtn) {
    sidebarCloseBtn.addEventListener("click", () => sidebar.classList.remove("open"));
}

// Quick cards in hero
quickCards.forEach(card => {
    card.addEventListener("click", () => {
        const action = card.getAttribute("data-action");
        if (action === "open-chat") {
            if (messageInput) messageInput.focus();
        } else if (action === "goto-roadmaps") {
            switchView("roadmaps");
        } else if (action === "goto-resume") {
            switchView("resume");
        } else if (action === "goto-companies") {
            switchView("companies");
        }
    });
});

if (heroSearchInput) {
    heroSearchInput.addEventListener("keydown", (e) => {
        if (e.key === "Enter" && heroSearchInput.value.trim()) {
            switchView("search");
            if (searchViewInput) {
                searchViewInput.value = heroSearchInput.value.trim();
                performSearch(searchViewInput.value.trim());
            }
        }
    });
}


/* ==================================================
 * 2. Message Formatting, Chat & Voice Controls
 * ================================================== */

function formatBotMessage(text) {
    if (!text) return "";

    let safe = text
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;");

    // Markdown Links: [text](https://...)
    safe = safe.replace(
        /\[([^\]]+)\]\((https?:\/\/[^\s)]+)\)/g,
        '<a href="$2" target="_blank" rel="noopener noreferrer">$1</a>'
    );

    // Bare URLs
    safe = safe.replace(
        /(^|[^">])(https?:\/\/[^\s<]+)/g,
        '$1<a href="$2" target="_blank" rel="noopener noreferrer">$2</a>'
    );

    // Bold text: **text**
    safe = safe.replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");

    // Code blocks / inline code
    safe = safe.replace(/`([^`]+)`/g, "<code>$1</code>");

    // Lists with bullet points
    safe = safe.replace(/^\s*-\s+(.+)$/gm, "<li>$1</li>");
    safe = safe.replace(/(<li>.+<\/li>)/s, "<ul>$1</ul>");

    return safe;
}

function timeNow() {
    return new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

function scrollToBottom() {
    if (chatBox) chatBox.scrollTop = chatBox.scrollHeight;
}

function speakText(text) {
    if (!("speechSynthesis" in window)) {
        alert("Text-to-speech is not supported in this browser.");
        return;
    }
    window.speechSynthesis.cancel();
    // Clean markdown before speaking
    const clean = text.replace(/[*_#`[\]()]/g, " ").replace(/https?:\/\/\S+/g, "link");
    const utterance = new SpeechSynthesisUtterance(clean);
    utterance.rate = 1.0;
    utterance.pitch = 1.0;
    window.speechSynthesis.speak(utterance);
}

function addMessage(text, sender, canRegenerate = false) {
    const row = document.createElement("div");
    row.className = `row ${sender}`;

    if (sender === "bot") {
        const avatar = document.createElement("div");
        avatar.className = "avatar bot-avatar";
        avatar.textContent = "🎓";
        row.appendChild(avatar);
    }

    const wrap = document.createElement("div");
    wrap.className = "bubble-wrap";

    const bubble = document.createElement("div");
    bubble.className = "message";

    if (sender === "bot") {
        bubble.innerHTML = formatBotMessage(text);
    } else {
        bubble.textContent = text;
    }

    const meta = document.createElement("div");
    meta.className = "message-meta";

    const time = document.createElement("span");
    time.className = "time";
    time.textContent = timeNow();
    meta.appendChild(time);

    // Bot message actions: Copy, Speak, Regenerate
    if (sender === "bot") {
        const actionsDiv = document.createElement("div");
        actionsDiv.className = "message-actions";

        // Copy button
        const copyBtn = document.createElement("button");
        copyBtn.type = "button";
        copyBtn.className = "msg-action-btn";
        copyBtn.innerHTML = "<span>📋</span> Copy";
        copyBtn.title = "Copy answer to clipboard";
        copyBtn.addEventListener("click", () => {
            navigator.clipboard.writeText(text).then(() => {
                copyBtn.innerHTML = "<span>✓</span> Copied!";
                setTimeout(() => { copyBtn.innerHTML = "<span>📋</span> Copy"; }, 2000);
            });
        });
        actionsDiv.appendChild(copyBtn);

        // Speak button (TTS)
        const speakBtn = document.createElement("button");
        speakBtn.type = "button";
        speakBtn.className = "msg-action-btn";
        speakBtn.innerHTML = "<span>🔊</span> Read";
        speakBtn.title = "Listen to answer";
        speakBtn.addEventListener("click", () => {
            speakText(text);
        });
        actionsDiv.appendChild(speakBtn);

        // Regenerate button
        if (canRegenerate && lastUserMessage) {
            const regenBtn = document.createElement("button");
            regenBtn.type = "button";
            regenBtn.className = "msg-action-btn";
            regenBtn.innerHTML = "<span>↻</span> Regenerate";
            regenBtn.title = "Regenerate AI answer";
            regenBtn.addEventListener("click", () => {
                sendMessage(lastUserMessage);
            });
            actionsDiv.appendChild(regenBtn);
        }

        meta.appendChild(actionsDiv);
    }

    wrap.appendChild(bubble);
    wrap.appendChild(meta);
    row.appendChild(wrap);
    chatBox.appendChild(row);
    scrollToBottom();
}

function showTyping() {
    hideTyping();
    const row = document.createElement("div");
    row.className = "row bot";
    row.id = "typing-row";
    row.innerHTML = `
        <div class="avatar bot-avatar">🎓</div>
        <div class="bubble-wrap">
            <div class="message typing">
                <span></span><span></span><span></span>
            </div>
        </div>
    `;
    chatBox.appendChild(row);
    scrollToBottom();
}

function hideTyping() {
    const el = document.getElementById("typing-row");
    if (el) el.remove();
}

function renderSuggestions(list) {
    if (!suggestionsBox) return;
    suggestionsBox.innerHTML = "";
    const items = list && list.length ? list : DEFAULT_SUGGESTIONS;
    items.forEach(txt => {
        const chip = document.createElement("button");
        chip.type = "button";
        chip.className = "suggestion-chip";
        chip.textContent = txt;
        chip.addEventListener("click", () => {
            sendMessage(txt);
        });
        suggestionsBox.appendChild(chip);
    });
}

async function sendMessage(text) {
    if (!text || !text.trim()) return;
    const clean = text.trim();
    lastUserMessage = clean;

    addMessage(clean, "user");
    if (messageInput) messageInput.value = "";
    showTyping();

    try {
        const payload = {
            message: clean,
            session_id: currentSessionId,
            custom_instructions: currentSettings.custom_instructions || "",
            answer_style: currentSettings.answer_style || "balanced",
            language: currentSettings.language || "en"
        };

        const res = await fetch("/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });

        const data = await res.json();
        hideTyping();

        if (data && data.answer) {
            addMessage(data.answer, "bot", true);
            renderSuggestions(data.suggestions || DEFAULT_SUGGESTIONS);
        } else {
            addMessage("I couldn't process your request. Please try asking again.", "bot");
        }
    } catch (err) {
        hideTyping();
        console.error("Chat error:", err);
        addMessage("Network connection issue. Please verify your connection and try again.", "bot");
    }
}

// Chat Form Submit
if (chatForm) {
    chatForm.addEventListener("submit", (e) => {
        e.preventDefault();
        const text = messageInput ? messageInput.value : "";
        sendMessage(text);
    });
}

// Enter-to-send vs Shift+Enter handler
if (messageInput) {
    messageInput.addEventListener("keydown", (e) => {
        if (e.key === "Enter" && !e.shiftKey && currentSettings.enter_to_send) {
            e.preventDefault();
            chatForm.dispatchEvent(new Event("submit"));
        }
    });
}

// Topbar New Chat Button
if (newChatTopBtn) {
    newChatTopBtn.addEventListener("click", () => {
        if (currentUser) {
            createSession("New Conversation");
        } else {
            chatBox.innerHTML = "";
            addMessage(WELCOME_MESSAGE, "bot");
            renderSuggestions(DEFAULT_SUGGESTIONS);
        }
        switchView("home");
    });
}

// Voice Input (Web Speech API)
function initVoiceInput() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
        if (voiceInputBtn) {
            voiceInputBtn.title = "Voice input is not supported in this browser";
            voiceInputBtn.addEventListener("click", () => {
                alert("Voice speech recognition is not supported in this browser. Please use Chrome or Edge.");
            });
        }
        return;
    }

    speechRecognizer = new SpeechRecognition();
    speechRecognizer.continuous = false;
    speechRecognizer.interimResults = false;
    speechRecognizer.lang = currentSettings.language === "hi" ? "hi-IN" : "en-US";

    speechRecognizer.onstart = () => {
        isRecording = true;
        if (voiceInputBtn) {
            voiceInputBtn.classList.add("recording");
            voiceInputBtn.title = "Listening... Speak now";
        }
    };

    speechRecognizer.onresult = (e) => {
        const transcript = e.results[0][0].transcript;
        if (messageInput) {
            messageInput.value = transcript;
            messageInput.focus();
        }
    };

    speechRecognizer.onerror = (e) => {
        console.warn("Speech recognition error:", e.error);
        stopRecording();
    };

    speechRecognizer.onend = () => {
        stopRecording();
    };

    if (voiceInputBtn) {
        voiceInputBtn.addEventListener("click", () => {
            if (isRecording) {
                speechRecognizer.stop();
            } else {
                try {
                    speechRecognizer.lang = currentSettings.language === "hi" ? "hi-IN" : "en-US";
                    speechRecognizer.start();
                } catch (err) {
                    console.error("Cannot start speech recognition:", err);
                }
            }
        });
    }
}

function stopRecording() {
    isRecording = false;
    if (voiceInputBtn) {
        voiceInputBtn.classList.remove("recording");
        voiceInputBtn.title = "Speak to type (Voice input)";
    }
}


/* ==================================================
 * 3. Search & Filter View
 * ================================================== */

let searchTimeout = null;

function initSearchControls() {
    if (searchViewInput) {
        searchViewInput.addEventListener("input", () => {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                performSearch(searchViewInput.value.trim());
            }, 250);
        });
    }

    searchFilterPills.forEach(pill => {
        pill.addEventListener("click", () => {
            searchFilterPills.forEach(p => p.classList.remove("active"));
            pill.classList.add("active");
            const cat = pill.getAttribute("data-cat");
            if (cat !== "all") {
                if (searchViewInput) searchViewInput.value = cat;
                performSearch(cat);
            } else {
                performSearch(searchViewInput ? searchViewInput.value.trim() : "");
            }
        });
    });
}

async function performSearch(query) {
    if (!searchResultsContainer) return;
    if (!query) {
        searchResultsContainer.innerHTML = '<div class="search-placeholder">Start typing above or select a filter pill to explore verified FAQs, roadmaps, and portals.</div>';
        return;
    }

    searchResultsContainer.innerHTML = '<div class="search-placeholder">Searching knowledge base...</div>';

    try {
        const res = await fetch(`/api/search?q=${encodeURIComponent(query)}`);
        const data = await res.json();

        let html = "";

        // FAQs
        if (data.faqs && data.faqs.length > 0) {
            html += `<div class="search-section">
                <h3>💬 Verified FAQs (${data.faqs.length})</h3>
                <div class="search-results-list">`;
            data.faqs.forEach(f => {
                html += `
                    <div class="search-result-item" onclick="searchAsk('${encodeURIComponent(f.query)}')">
                        <h4>${f.title}</h4>
                        <p>${f.snippet}</p>
                        <span class="result-action">Ask Assistant →</span>
                    </div>`;
            });
            html += `</div></div>`;
        }

        // Categories & Roadmaps
        if (data.categories && data.categories.length > 0) {
            html += `<div class="search-section">
                <h3>🗺️ Categories & Roadmaps (${data.categories.length})</h3>
                <div class="search-results-list">`;
            data.categories.forEach(c => {
                html += `
                    <div class="search-result-item" onclick="openRoadmapCategory('${c.id}')">
                        <h4>${c.icon || "💻"} ${c.title}</h4>
                        <p><strong>Skills:</strong> ${c.skills}</p>
                        <span class="result-action">View Learning Roadmap →</span>
                    </div>`;
            });
            html += `</div></div>`;
        }

        // Companies
        if (data.companies && data.companies.length > 0) {
            html += `<div class="search-section">
                <h3>🏢 Verified Career Portals (${data.companies.length})</h3>
                <div class="search-results-list">`;
            data.companies.forEach(comp => {
                html += `
                    <div class="search-result-item">
                        <h4>${comp.badge || "🌐"} ${comp.name}</h4>
                        <p>${comp.description}</p>
                        <a href="${comp.url}" target="_blank" rel="noopener noreferrer" class="btn btn-outline btn-sm">Official Portal ↗</a>
                    </div>`;
            });
            html += `</div></div>`;
        }

        if (!html) {
            html = `<div class="search-placeholder">No exact matches found for "<strong>${query}</strong>". Try searching for Java, Python, JavaScript, Full-Stack, Google, or resume.</div>`;
        }

        searchResultsContainer.innerHTML = html;
    } catch (err) {
        console.error("Search error:", err);
        searchResultsContainer.innerHTML = '<div class="search-placeholder text-danger">Search failed. Please try again.</div>';
    }
}

window.searchAsk = function(queryEncoded) {
    const query = decodeURIComponent(queryEncoded);
    switchView("home");
    sendMessage(query);
};

window.openRoadmapCategory = function(catId) {
    activeRoadmapCat = catId;
    switchView("roadmaps");
};


/* ==================================================
 * 4. Categories & Roadmaps Controller
 * ================================================== */

async function loadRoadmapsView() {
    const container = document.getElementById("roadmap-category-content");
    if (!container) return;

    if (roadmapsCache.length === 0) {
        try {
            const res = await fetch("/api/roadmaps");
            const data = await res.json();
            if (data.categories) {
                roadmapsCache = data.categories;
            }
        } catch (e) {
            console.error("Failed to load roadmaps:", e);
        }
    }

    // Load user's skill progress map
    if (currentUser) {
        try {
            const skRes = await fetch("/api/skill-progress");
            const skData = await skRes.json();
            if (skData.skills) userSkillProgress = skData.skills;
        } catch (e) {
            console.error("Failed to load skill progress:", e);
        }
    } else {
        const local = localStorage.getItem("internbot_skill_progress");
        if (local) {
            try { userSkillProgress = JSON.parse(local); } catch (e) {}
        }
    }

    renderRoadmapTabs();
    renderActiveRoadmapCategory();
}

function renderRoadmapTabs() {
    const tabButtons = document.querySelectorAll(".cat-tab-btn");
    tabButtons.forEach(btn => {
        const cat = btn.getAttribute("data-cat");
        btn.classList.toggle("active", cat === activeRoadmapCat);
        btn.onclick = () => {
            activeRoadmapCat = cat;
            renderRoadmapTabs();
            renderActiveRoadmapCategory();
        };
    });
}

function renderActiveRoadmapCategory() {
    const container = document.getElementById("roadmap-category-content");
    if (!container) return;

    const cat = roadmapsCache.find(c => c.id === activeRoadmapCat) || roadmapsCache[0];
    if (!cat) {
        container.innerHTML = "<p>Loading roadmap...</p>";
        return;
    }

    let skillsHtml = "";
    (cat.skills || []).forEach(sk => {
        const currentStatus = userSkillProgress[sk] || "Not Started";
        skillsHtml += `
            <div class="skill-tracker-item">
                <span class="skill-name">${sk}</span>
                <select class="skill-status-select ${currentStatus.toLowerCase()}" onchange="updateSkillStatus('${cat.id}', '${sk}', this.value, this)">
                    <option value="Not Started" ${currentStatus === "Not Started" ? "selected" : ""}>Not Started</option>
                    <option value="Beginner" ${currentStatus === "Beginner" ? "selected" : ""}>Beginner</option>
                    <option value="Intermediate" ${currentStatus === "Intermediate" ? "selected" : ""}>Intermediate</option>
                    <option value="Advanced" ${currentStatus === "Advanced" ? "selected" : ""}>Advanced</option>
                    <option value="Completed" ${currentStatus === "Completed" ? "selected" : ""}>Completed ✓</option>
                </select>
            </div>
        `;
    });

    let timelineHtml = "";
    (cat.roadmap || []).forEach(step => {
        timelineHtml += `
            <div class="roadmap-step-card">
                <div class="step-card-header">
                    <h4>Step ${step.step}: ${step.title}</h4>
                    <span class="step-duration-badge">⏱️ ${step.duration}</span>
                </div>
                <ul class="step-topics-list">
                    ${(step.topics || []).map(t => `<li>${t}</li>`).join("")}
                </ul>
            </div>
        `;
    });

    let projectsHtml = "";
    (cat.projects || []).forEach(proj => {
        const diffClass = proj.difficulty.toLowerCase();
        projectsHtml += `
            <div class="project-rec-card">
                <div class="project-rec-header">
                    <h4>${proj.title}</h4>
                    <span class="difficulty-badge ${diffClass}">${proj.difficulty}</span>
                </div>
                <p class="text-muted">${proj.description}</p>
                <div class="project-tech-tags">
                    ${(proj.tech_stack || []).map(t => `<span class="tech-tag">${t}</span>`).join("")}
                </div>
                <div class="project-why-box">
                    <strong>💡 Why this project:</strong> ${proj.why}
                </div>
            </div>
        `;
    });

    container.innerHTML = `
        <div class="category-overview-card">
            <div class="cat-overview-header">
                <div>
                    <h3>${cat.icon || "💻"} ${cat.title}</h3>
                    <p class="text-muted">${cat.description}</p>
                </div>
                <div>
                    <a href="${cat.external_link.url}" target="_blank" rel="noopener noreferrer" class="external-discovery-banner">
                        <span>🔗</span> ${cat.external_link.title} ↗
                    </a>
                    <div class="external-disclaimer-note">⚠️ ${cat.external_link.disclaimer}</div>
                </div>
            </div>

            <div class="skills-tracker-section">
                <h4>🎯 Skill Progress Tracker & Self-Assessment</h4>
                <p class="text-muted" style="margin-bottom: 12px; font-size: 0.85rem;">Mark your current mastery for each required competency. Changes save to your profile automatically.</p>
                <div class="skills-tracker-grid">
                    ${skillsHtml}
                </div>
            </div>
        </div>

        <div class="section-title-wrap">
            <h3>📍 Step-by-Step Learning Roadmap</h3>
            <p class="text-muted">Structured curriculum designed for internship test rounds and hiring bars.</p>
        </div>
        <div class="roadmap-timeline">
            ${timelineHtml}
        </div>

        <div class="section-title-wrap">
            <h3>⭐ Recommended Portfolio Projects</h3>
            <p class="text-muted">High-impact projects with transparent architectural reasoning to wow technical recruiters.</p>
        </div>
        <div class="projects-rec-grid">
            ${projectsHtml}
        </div>
    `;
}

window.updateSkillStatus = async function(catId, skillName, status, selectEl) {
    userSkillProgress[skillName] = status;
    if (selectEl) {
        selectEl.className = `skill-status-select ${status.toLowerCase()}`;
    }

    if (currentUser) {
        try {
            await fetch("/api/skill-progress", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ category_id: catId, skill_name: skillName, status: status })
            });
        } catch (e) {
            console.error("Failed to save skill progress:", e);
        }
    } else {
        localStorage.setItem("internbot_skill_progress", JSON.stringify(userSkillProgress));
    }
};


/* ==================================================
 * 5. Technical Interview & MCQ Controller
 * ================================================== */

async function loadInterviewTopics() {
    const topicSelect = document.getElementById("interview-topic-select");
    const modeMcqBtn = document.getElementById("mode-mcq-btn");
    const modeMockBtn = document.getElementById("mode-mock-btn");
    const mcqContainer = document.getElementById("mcq-container");
    const mockContainer = document.getElementById("mock-qa-container");

    if (quizTopicsCache.length === 0) {
        try {
            const res = await fetch("/api/interview-topics");
            const data = await res.json();
            if (data.topics) {
                quizTopicsCache = data.topics;
            }
        } catch (e) {
            console.error("Failed to load interview topics:", e);
        }
    }

    if (topicSelect) {
        topicSelect.value = activeQuizTopic;
        topicSelect.onchange = () => {
            activeQuizTopic = topicSelect.value;
            startQuizForTopic(activeQuizTopic);
            renderMockQA(activeQuizTopic);
        };
    }

    if (modeMcqBtn && modeMockBtn) {
        modeMcqBtn.onclick = () => {
            modeMcqBtn.classList.add("active");
            modeMockBtn.classList.remove("active");
            if (mcqContainer) mcqContainer.classList.remove("hidden");
            if (mockContainer) mockContainer.classList.add("hidden");
        };

        modeMockBtn.onclick = () => {
            modeMockBtn.classList.add("active");
            modeMcqBtn.classList.remove("active");
            if (mcqContainer) mcqContainer.classList.add("hidden");
            if (mockContainer) mockContainer.classList.remove("hidden");
            renderMockQA(activeQuizTopic);
        };
    }

    startQuizForTopic(activeQuizTopic);
    renderMockQA(activeQuizTopic);
    loadPastScores();
}

function startQuizForTopic(topicId) {
    const topicData = quizTopicsCache.find(t => t.id === topicId) || quizTopicsCache[0];
    if (!topicData || !topicData.mcqs) return;

    currentQuizQuestions = topicData.mcqs;
    currentQuizIndex = 0;
    userQuizScore = 0;
    userQuizAnswers = [];
    quizSubmitted = false;

    renderCurrentQuizQuestion();
}

function renderCurrentQuizQuestion() {
    const progressText = document.getElementById("quiz-progress-text");
    const scoreBadge = document.getElementById("quiz-score-badge");
    const questionText = document.getElementById("quiz-question-text");
    const optionsList = document.getElementById("quiz-options-list");
    const explanationBox = document.getElementById("quiz-explanation");
    const prevBtn = document.getElementById("quiz-prev-btn");
    const nextBtn = document.getElementById("quiz-next-btn");
    const submitBtn = document.getElementById("quiz-submit-btn");

    if (!currentQuizQuestions.length) return;

    const q = currentQuizQuestions[currentQuizIndex];
    if (progressText) progressText.textContent = `Question ${currentQuizIndex + 1} of ${currentQuizQuestions.length}`;
    if (scoreBadge) scoreBadge.textContent = `Score: ${userQuizScore}/${currentQuizQuestions.length}`;
    if (questionText) questionText.textContent = q.question;

    if (explanationBox) explanationBox.classList.add("hidden");

    if (optionsList) {
        optionsList.innerHTML = "";
        const savedAnswer = userQuizAnswers[currentQuizIndex];

        q.options.forEach((opt, idx) => {
            const optDiv = document.createElement("div");
            optDiv.className = "quiz-option";
            optDiv.textContent = `${String.fromCharCode(65 + idx)}. ${opt}`;

            if (savedAnswer !== undefined) {
                if (idx === q.answer_index) optDiv.classList.add("correct");
                else if (idx === savedAnswer) optDiv.classList.add("incorrect");
            } else {
                optDiv.onclick = () => selectQuizOption(idx);
            }
            optionsList.appendChild(optDiv);
        });

        if (savedAnswer !== undefined && explanationBox) {
            explanationBox.classList.remove("hidden");
            document.getElementById("quiz-explanation-text").textContent = q.explanation;
        }
    }

    if (prevBtn) prevBtn.disabled = currentQuizIndex === 0;

    const isLast = currentQuizIndex === currentQuizQuestions.length - 1;
    if (nextBtn) {
        nextBtn.classList.toggle("hidden", isLast);
        nextBtn.onclick = () => {
            if (currentQuizIndex < currentQuizQuestions.length - 1) {
                currentQuizIndex++;
                renderCurrentQuizQuestion();
            }
        };
    }

    if (prevBtn) {
        prevBtn.onclick = () => {
            if (currentQuizIndex > 0) {
                currentQuizIndex--;
                renderCurrentQuizQuestion();
            }
        };
    }

    if (submitBtn) {
        submitBtn.classList.toggle("hidden", !isLast);
        submitBtn.disabled = quizSubmitted;
        submitBtn.onclick = submitQuizScore;
    }
}

function selectQuizOption(selectedIndex) {
    const q = currentQuizQuestions[currentQuizIndex];
    userQuizAnswers[currentQuizIndex] = selectedIndex;

    if (selectedIndex === q.answer_index) {
        userQuizScore++;
    }

    renderCurrentQuizQuestion();
}

async function submitQuizScore() {
    if (quizSubmitted) return;
    quizSubmitted = true;

    const total = currentQuizQuestions.length;
    const percentage = total > 0 ? Math.round((userQuizScore / total) * 100) : 0;
    const topicTitle = (quizTopicsCache.find(t => t.id === activeQuizTopic) || {}).title || "General";

    try {
        await fetch("/api/submit-interview", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                topic: topicTitle,
                score: userQuizScore,
                total: total,
                percentage: percentage,
                answers: userQuizAnswers
            })
        });
        alert(`Quiz Finished! Your Score: ${userQuizScore} / ${total} (${percentage}%)`);
        loadPastScores();
    } catch (e) {
        console.error("Failed to submit score:", e);
    }
}

function renderMockQA(topicId) {
    const list = document.getElementById("mock-qa-list");
    if (!list) return;

    const topicData = quizTopicsCache.find(t => t.id === topicId) || quizTopicsCache[0];
    if (!topicData || !topicData.interview_questions) {
        list.innerHTML = "<p>No questions available for this domain.</p>";
        return;
    }

    let html = "";
    topicData.interview_questions.forEach((item, idx) => {
        html += `
            <div class="mock-qa-item">
                <h4>Q${idx + 1}: ${item.question}</h4>
                <ul>
                    ${(item.key_points || []).map(pt => `<li>${pt}</li>`).join("")}
                </ul>
            </div>
        `;
    });
    list.innerHTML = html;
}

async function loadPastScores() {
    const wrap = document.getElementById("past-scores-table-wrap");
    if (!wrap) return;

    if (!currentUser) {
        wrap.innerHTML = '<p class="text-muted">Sign in with Google or Demo Account to automatically save and track your quiz scores over time.</p>';
        return;
    }

    try {
        const res = await fetch("/api/interview-scores");
        const data = await res.json();
        if (!data.scores || data.scores.length === 0) {
            wrap.innerHTML = '<p class="text-muted">No quiz attempts saved yet. Complete a topic quiz above to see your scores.</p>';
            return;
        }

        let html = `
            <table class="data-table" style="width: 100%; border-collapse: collapse; font-size: 0.9rem;">
                <thead>
                    <tr style="text-align: left; border-bottom: 2px solid var(--border);">
                        <th style="padding: 8px;">Topic</th>
                        <th style="padding: 8px;">Score</th>
                        <th style="padding: 8px;">Percentage</th>
                        <th style="padding: 8px;">Date</th>
                    </tr>
                </thead>
                <tbody>
        `;
        data.scores.forEach(sc => {
            const dateStr = sc.completed_at ? new Date(sc.completed_at).toLocaleDateString() : "-";
            html += `
                <tr style="border-bottom: 1px solid var(--border-subtle);">
                    <td style="padding: 8px;">${sc.topic || sc.category}</td>
                    <td style="padding: 8px;">${sc.score} / ${sc.total || sc.total_questions || "-"}</td>
                    <td style="padding: 8px;"><strong style="color: var(--primary);">${sc.percentage}%</strong></td>
                    <td style="padding: 8px; color: var(--text-muted);">${dateStr}</td>
                </tr>
            `;
        });
        html += "</tbody></table>";
        wrap.innerHTML = html;
    } catch (e) {
        console.error("Failed to load scores:", e);
    }
}


/* ==================================================
 * 6. ATS Resume Checker Controller
 * ================================================== */

let selectedResumeFile = null;

function initResumeChecker() {
    const dropzone = document.getElementById("resume-dropzone");
    const fileInput = document.getElementById("resume-file-input");
    const chosenWrap = document.getElementById("resume-file-chosen");
    const dropContent = document.getElementById("resume-dropzone-content");
    const chosenName = document.getElementById("chosen-filename");
    const removeBtn = document.getElementById("remove-resume-btn");
    const analyzeBtn = document.getElementById("analyze-resume-btn");
    const targetSelect = document.getElementById("resume-target-category");

    if (dropzone && fileInput) {
        dropzone.addEventListener("click", () => fileInput.click());

        dropzone.addEventListener("dragover", (e) => {
            e.preventDefault();
            dropzone.style.borderColor = "var(--primary)";
        });

        dropzone.addEventListener("dragleave", () => {
            dropzone.style.borderColor = "var(--border)";
        });

        dropzone.addEventListener("drop", (e) => {
            e.preventDefault();
            dropzone.style.borderColor = "var(--border)";
            if (e.dataTransfer.files.length > 0) {
                handleResumeSelect(e.dataTransfer.files[0]);
            }
        });

        fileInput.addEventListener("change", () => {
            if (fileInput.files.length > 0) {
                handleResumeSelect(fileInput.files[0]);
            }
        });
    }

    function handleResumeSelect(file) {
        const allowed = [".pdf", ".docx", ".doc", ".txt"];
        const ext = file.name.slice(file.name.lastIndexOf(".")).toLowerCase();
        if (!allowed.includes(ext)) {
            alert("Please upload a PDF, DOCX, or TXT resume file.");
            return;
        }

        selectedResumeFile = file;
        if (chosenName) chosenName.textContent = file.name;
        if (dropContent) dropContent.classList.add("hidden");
        if (chosenWrap) chosenWrap.classList.remove("hidden");
        if (analyzeBtn) analyzeBtn.disabled = false;
    }

    if (removeBtn) {
        removeBtn.addEventListener("click", (e) => {
            e.stopPropagation();
            selectedResumeFile = null;
            if (fileInput) fileInput.value = "";
            if (dropContent) dropContent.classList.remove("hidden");
            if (chosenWrap) chosenWrap.classList.add("hidden");
            if (analyzeBtn) analyzeBtn.disabled = true;
        });
    }

    if (analyzeBtn) {
        analyzeBtn.addEventListener("click", async () => {
            if (!selectedResumeFile) return;

            analyzeBtn.disabled = true;
            analyzeBtn.innerHTML = "<span>⏳</span> Analyzing ATS Score...";

            const formData = new FormData();
            formData.append("resume", selectedResumeFile);
            formData.append("category", targetSelect ? targetSelect.value : "General");

            try {
                const res = await fetch("/api/check-resume", {
                    method: "POST",
                    body: formData
                });

                const data = await res.json();
                analyzeBtn.disabled = false;
                analyzeBtn.innerHTML = "<span>⚡</span> Analyze Resume ATS Score";

                if (data.success) {
                    renderResumeReport(data);
                } else {
                    alert(data.error || "Failed to analyze resume.");
                }
            } catch (err) {
                analyzeBtn.disabled = false;
                analyzeBtn.innerHTML = "<span>⚡</span> Analyze Resume ATS Score";
                console.error("Resume analysis error:", err);
                alert("Failed to analyze resume. Please check the file and try again.");
            }
        });
    }
}

function renderResumeReport(report) {
    const placeholder = document.getElementById("report-placeholder");
    const resultsWrap = document.getElementById("report-results");
    if (placeholder) placeholder.classList.add("hidden");
    if (!resultsWrap) return;

    resultsWrap.classList.remove("hidden");

    let scoreColor = "score-green";
    if (report.score < 50) scoreColor = "score-red";
    else if (report.score < 75) scoreColor = "score-amber";

    let skillsHtml = "";
    for (const domain in report.detected_skills) {
        report.detected_skills[domain].forEach(sk => {
            skillsHtml += `<span class="detected-skill-pill">${sk}</span>`;
        });
    }

    let missingHtml = "";
    (report.missing_keywords || []).forEach(kw => {
        missingHtml += `<span class="missing-keyword-pill">+ ${kw}</span>`;
    });

    let suggestionsHtml = "";
    (report.suggestions || []).forEach(sug => {
        suggestionsHtml += `<li>${sug}</li>`;
    });

    resultsWrap.innerHTML = `
        <div class="report-header-banner">
            <div class="score-circle ${scoreColor}">
                ${report.score}
                <span>ATS SCORE</span>
            </div>
            <div>
                <h3>ATS Match Analysis: ${report.score}/100</h3>
                <p class="text-muted">Analyzed <strong>${report.filename}</strong> (${report.word_count} words)</p>
                <div style="font-size: 0.85rem; margin-top: 6px;">
                    ${report.found_sections.map(s => `✓ ${s}`).join(" &nbsp;·&nbsp; ")}
                </div>
            </div>
        </div>

        <div class="report-section" style="margin-bottom: 18px;">
            <h4>✅ Detected Technical Skills (${report.total_skills_count})</h4>
            <div class="report-tags-wrap">
                ${skillsHtml || '<span class="text-muted">No specific tech skills recognized.</span>'}
            </div>
        </div>

        ${report.missing_keywords && report.missing_keywords.length > 0 ? `
            <div class="report-section" style="margin-bottom: 18px;">
                <h4>⚠️ Recommended Missing Keywords</h4>
                <p class="text-muted" style="font-size: 0.85rem;">Consider naturally integrating these role-specific competencies:</p>
                <div class="report-tags-wrap">
                    ${missingHtml}
                </div>
            </div>
        ` : ''}

        <div class="report-section">
            <h4>💡 Actionable Improvement Suggestions</h4>
            <ul class="actionable-suggestions-list">
                ${suggestionsHtml}
            </ul>
        </div>
    `;
}


/* ==================================================
 * 7. Application Tracker & Bookmarks Controller
 * ================================================== */

let applicationsCache = [];
let bookmarksCache = [];
let remindersCache = [];
let activeAppFilter = "all";

function loadTrackerView() {
    const subnavBtns = document.querySelectorAll(".tracker-tab-btn");
    subnavBtns.forEach(btn => {
        btn.onclick = () => {
            subnavBtns.forEach(b => b.classList.remove("active"));
            btn.classList.add("active");
            const tab = btn.getAttribute("data-tab");
            document.querySelectorAll(".tracker-tab-content").forEach(c => c.classList.remove("active"));
            const target = document.getElementById(`tab-${tab}`);
            if (target) target.classList.add("active");
        };
    });

    loadApplications();
    loadBookmarks();
    loadReminders();
    initAppModal();
    initBookmarkModal();
    initRemindersInline();
}

async function loadApplications() {
    const grid = document.getElementById("applications-grid");
    const countEl = document.getElementById("apps-count");
    if (!grid) return;

    if (!currentUser) {
        grid.innerHTML = '<div class="search-placeholder">Sign in to track your internship applications, interview rounds, and offer letters.</div>';
        if (countEl) countEl.textContent = "0";
        return;
    }

    try {
        const res = await fetch("/api/applications");
        const data = await res.json();
        applicationsCache = data.applications || [];
        if (countEl) countEl.textContent = applicationsCache.length;
        renderApplicationsList();
    } catch (e) {
        console.error("Failed to load applications:", e);
    }
}

function renderApplicationsList() {
    const grid = document.getElementById("applications-grid");
    if (!grid) return;

    const filtered = activeAppFilter === "all"
        ? applicationsCache
        : applicationsCache.filter(a => a.status === activeAppFilter);

    if (filtered.length === 0) {
        grid.innerHTML = '<div class="search-placeholder">No applications recorded in this status. Click "+ Track Application" to add one.</div>';
        return;
    }

    let html = "";
    filtered.forEach(app => {
        html += `
            <div class="app-tracker-card">
                <div class="app-card-header">
                    <div>
                        <h4 style="font-weight: 700; font-size: 1.05rem;">${app.company}</h4>
                        <span class="text-muted" style="font-size: 0.9rem;">${app.role}</span>
                    </div>
                    <span class="app-status-badge ${app.status}">${app.status}</span>
                </div>

                <div class="app-card-meta">
                    ${app.category ? `<div>🏷️ ${app.category}</div>` : ''}
                    ${app.deadline ? `<div>📅 Deadline: ${app.deadline}</div>` : ''}
                    ${app.follow_up_date ? `<div>⏰ Follow-up: ${app.follow_up_date}</div>` : ''}
                    ${app.notes ? `<div style="margin-top: 4px; font-style: italic;">"${app.notes}"</div>` : ''}
                </div>

                <div class="app-card-actions">
                    <select class="form-select" style="font-size: 0.75rem; padding: 2px 6px;" onchange="changeAppStatus('${app.id}', this.value)">
                        <option value="Saved" ${app.status === "Saved" ? "selected" : ""}>Saved</option>
                        <option value="Applied" ${app.status === "Applied" ? "selected" : ""}>Applied</option>
                        <option value="Assessment" ${app.status === "Assessment" ? "selected" : ""}>Assessment</option>
                        <option value="Interview" ${app.status === "Interview" ? "selected" : ""}>Interview</option>
                        <option value="Offer" ${app.status === "Offer" ? "selected" : ""}>Offer</option>
                        <option value="Rejected" ${app.status === "Rejected" ? "selected" : ""}>Rejected</option>
                    </select>
                    ${app.url ? `<a href="${app.url}" target="_blank" rel="noopener noreferrer" class="btn btn-outline btn-sm">URL ↗</a>` : ''}
                    <button class="btn btn-ghost btn-sm text-danger" onclick="deleteApplication('${app.id}')">✕</button>
                </div>
            </div>
        `;
    });

    grid.innerHTML = html;
}

// App Status Filter Chips
const statusChips = document.querySelectorAll("#app-status-filters .filter-chip");
statusChips.forEach(chip => {
    chip.addEventListener("click", () => {
        statusChips.forEach(c => c.classList.remove("active"));
        chip.classList.add("active");
        activeAppFilter = chip.getAttribute("data-status");
        renderApplicationsList();
    });
});

window.changeAppStatus = async function(appId, newStatus) {
    try {
        await fetch(`/api/applications/${appId}`, {
            method: "PATCH",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ status: newStatus })
        });
        const target = applicationsCache.find(a => a.id === appId);
        if (target) target.status = newStatus;
        renderApplicationsList();
    } catch (e) {
        console.error("Failed to update status:", e);
    }
};

window.deleteApplication = async function(appId) {
    if (currentSettings.delete_confirmation && !confirm("Delete this application record?")) return;
    try {
        await fetch(`/api/applications/${appId}`, { method: "DELETE" });
        applicationsCache = applicationsCache.filter(a => a.id !== appId);
        const countEl = document.getElementById("apps-count");
        if (countEl) countEl.textContent = applicationsCache.length;
        renderApplicationsList();
    } catch (e) {
        console.error("Failed to delete application:", e);
    }
};

function initAppModal() {
    const modal = document.getElementById("app-modal");
    const openBtn = document.getElementById("open-add-app-modal-btn");
    const closeBtn = document.getElementById("app-modal-close");
    const cancelBtn = document.getElementById("app-modal-cancel");
    const form = document.getElementById("app-form");

    if (openBtn) {
        openBtn.onclick = () => {
            if (!currentUser) {
                alert("Please sign in to track applications in your private database.");
                return;
            }
            if (modal) modal.classList.remove("hidden");
        };
    }

    if (closeBtn) closeBtn.onclick = () => modal.classList.add("hidden");
    if (cancelBtn) cancelBtn.onclick = () => modal.classList.add("hidden");

    if (form) {
        form.onsubmit = async (e) => {
            e.preventDefault();
            const payload = {
                company: document.getElementById("app-company").value.trim(),
                role: document.getElementById("app-role").value.trim(),
                url: document.getElementById("app-url").value.trim(),
                category: document.getElementById("app-category").value,
                status: document.getElementById("app-status").value,
                deadline: document.getElementById("app-deadline").value,
                followup_date: document.getElementById("app-followup").value,
                notes: document.getElementById("app-notes").value.trim()
            };

            try {
                const res = await fetch("/api/applications", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(payload)
                });
                const data = await res.json();
                if (data.success) {
                    modal.classList.add("hidden");
                    form.reset();
                    loadApplications();
                }
            } catch (err) {
                console.error("Add application error:", err);
            }
        };
    }
}

// Bookmarks Controller
async function loadBookmarks() {
    const grid = document.getElementById("bookmarks-grid");
    const countEl = document.getElementById("bookmarks-count");
    if (!grid) return;

    if (!currentUser) {
        grid.innerHTML = '<div class="search-placeholder">Sign in to save and sync internship bookmarks across devices.</div>';
        if (countEl) countEl.textContent = "0";
        return;
    }

    try {
        const res = await fetch("/api/bookmarks");
        const data = await res.json();
        bookmarksCache = data.bookmarks || [];
        if (countEl) countEl.textContent = bookmarksCache.length;

        if (bookmarksCache.length === 0) {
            grid.innerHTML = '<div class="search-placeholder">No bookmarks saved yet. Click "+ Add Bookmark" to bookmark a listing.</div>';
            return;
        }

        let html = "";
        bookmarksCache.forEach(bm => {
            html += `
                <div class="bookmark-card">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                        <div>
                            <h4 style="font-weight: 700;">${bm.title}</h4>
                            <span class="text-muted" style="font-size: 0.85rem;">🏢 ${bm.company} · ${bm.category || "General"}</span>
                        </div>
                        <button class="btn btn-ghost btn-sm text-danger" onclick="deleteBookmark('${bm.id}')">✕</button>
                    </div>
                    ${bm.notes ? `<p style="font-size: 0.85rem; color: var(--text-muted);">${bm.notes}</p>` : ''}
                    <div style="display: flex; justify-content: flex-end; margin-top: 6px;">
                        <a href="${bm.url}" target="_blank" rel="noopener noreferrer" class="btn btn-outline btn-sm">Visit Opportunity ↗</a>
                    </div>
                </div>
            `;
        });
        grid.innerHTML = html;
    } catch (e) {
        console.error("Failed to load bookmarks:", e);
    }
}

window.deleteBookmark = async function(bmId) {
    try {
        await fetch(`/api/bookmarks/${bmId}`, { method: "DELETE" });
        loadBookmarks();
    } catch (e) {
        console.error("Failed to delete bookmark:", e);
    }
};

function initBookmarkModal() {
    const modal = document.getElementById("bookmark-modal");
    const openBtn = document.getElementById("open-add-bookmark-modal-btn");
    const closeBtn = document.getElementById("bookmark-modal-close");
    const cancelBtn = document.getElementById("bookmark-modal-cancel");
    const form = document.getElementById("bookmark-form");

    if (openBtn) {
        openBtn.onclick = () => {
            if (!currentUser) {
                alert("Please sign in to save personal bookmarks.");
                return;
            }
            if (modal) modal.classList.remove("hidden");
        };
    }

    if (closeBtn) closeBtn.onclick = () => modal.classList.add("hidden");
    if (cancelBtn) cancelBtn.onclick = () => modal.classList.add("hidden");

    if (form) {
        form.onsubmit = async (e) => {
            e.preventDefault();
            const payload = {
                company: document.getElementById("bm-company").value.trim(),
                title: document.getElementById("bm-title").value.trim(),
                url: document.getElementById("bm-url").value.trim(),
                category: document.getElementById("bm-category").value,
                notes: document.getElementById("bm-notes").value.trim()
            };

            try {
                const res = await fetch("/api/bookmarks", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(payload)
                });
                const data = await res.json();
                if (data.success) {
                    modal.classList.add("hidden");
                    form.reset();
                    loadBookmarks();
                }
            } catch (err) {
                console.error("Bookmark add error:", err);
            }
        };
    }
}

// Reminders Controller
async function loadReminders() {
    const list = document.getElementById("reminders-list");
    const countEl = document.getElementById("reminders-count");
    if (!list) return;

    if (!currentUser) {
        list.innerHTML = '<p class="text-muted">Sign in to schedule deadlines and reminders.</p>';
        if (countEl) countEl.textContent = "0";
        return;
    }

    try {
        const res = await fetch("/api/reminders");
        const data = await res.json();
        remindersCache = data.reminders || [];
        if (countEl) countEl.textContent = remindersCache.length;

        if (remindersCache.length === 0) {
            list.innerHTML = '<p class="text-muted">No reminders set. Use the form above to add an application deadline or follow-up alert.</p>';
            return;
        }

        let html = "";
        remindersCache.forEach(rem => {
            const isDone = rem.is_completed === 1;
            html += `
                <div class="reminder-item ${isDone ? 'completed' : ''}">
                    <div style="display: flex; align-items: center; gap: 12px;">
                        <input type="checkbox" ${isDone ? 'checked' : ''} onchange="toggleReminder('${rem.id}')">
                        <div>
                            <strong>${rem.title}</strong>
                            <div style="font-size: 0.8rem; color: var(--text-muted);">
                                🏷️ ${rem.reminder_type} · 📅 Due: ${rem.due_date || "No date"}
                            </div>
                        </div>
                    </div>
                    <button class="btn btn-ghost btn-sm text-danger" onclick="deleteReminder('${rem.id}')">✕</button>
                </div>
            `;
        });
        list.innerHTML = html;
    } catch (e) {
        console.error("Failed to load reminders:", e);
    }
}

window.toggleReminder = async function(remId) {
    try {
        await fetch(`/api/reminders/${remId}/toggle`, { method: "PATCH" });
        loadReminders();
    } catch (e) {
        console.error("Toggle reminder error:", e);
    }
};

window.deleteReminder = async function(remId) {
    try {
        await fetch(`/api/reminders/${remId}`, { method: "DELETE" });
        loadReminders();
    } catch (e) {
        console.error("Delete reminder error:", e);
    }
};

function initRemindersInline() {
    const form = document.getElementById("inline-reminder-form");
    const notifBtn = document.getElementById("request-browser-notif-btn");

    if (form) {
        form.onsubmit = async (e) => {
            e.preventDefault();
            if (!currentUser) {
                alert("Sign in required to save reminders.");
                return;
            }

            const title = document.getElementById("reminder-title-input").value.trim();
            const dueDate = document.getElementById("reminder-date-input").value;
            const type = document.getElementById("reminder-type-input").value;

            try {
                const res = await fetch("/api/reminders", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ title, due_date: dueDate, reminder_type: type })
                });
                const data = await res.json();
                if (data.success) {
                    form.reset();
                    loadReminders();
                }
            } catch (err) {
                console.error("Add reminder error:", err);
            }
        };
    }

    if (notifBtn) {
        notifBtn.onclick = () => {
            if (!("Notification" in window)) {
                alert("This browser does not support desktop notifications.");
                return;
            }
            Notification.requestPermission().then(permission => {
                if (permission === "granted") {
                    new Notification("InternBot Notifications Enabled", {
                        body: "You will receive desktop alerts for approaching internship deadlines."
                    });
                    notifBtn.textContent = "✓ Notifications Enabled";
                    notifBtn.disabled = true;
                } else {
                    alert("Notification permission was not granted.");
                }
            });
        };
    }
}


/* ==================================================
 * 8. ChatGPT-Inspired Settings Page Controller
 * ================================================== */

function initSettingsSubnav() {
    const subnavButtons = document.querySelectorAll(".settings-tab-btn");
    const panes = document.querySelectorAll(".settings-pane");

    subnavButtons.forEach(btn => {
        btn.addEventListener("click", () => {
            subnavButtons.forEach(b => b.classList.remove("active"));
            panes.forEach(p => p.classList.remove("active"));

            btn.classList.add("active");
            const section = btn.getAttribute("data-section");
            const targetPane = document.getElementById(`pane-${section}`);
            if (targetPane) targetPane.classList.add("active");
        });
    });
}

async function loadSettingsView() {
    try {
        const res = await fetch("/api/settings");
        const data = await res.json();
        if (data.settings) {
            currentSettings = Object.assign(currentSettings, data.settings);
        }
    } catch (e) {
        console.error("Failed to fetch settings:", e);
    }

    applySettingsToUI();
    loadMemoryItems();
    checkGeminiStatus();
}

function applySettingsToUI() {
    // 1. General & Appearance
    const themeSelect = document.getElementById("setting-theme");
    if (themeSelect) themeSelect.value = currentSettings.theme || "system";
    setTheme(currentSettings.theme || "system", false);

    const langSelect = document.getElementById("setting-language");
    if (langSelect) langSelect.value = currentSettings.language || "en";

    const styleSelect = document.getElementById("setting-answer-style");
    if (styleSelect) styleSelect.value = currentSettings.answer_style || "balanced";

    const defCatSelect = document.getElementById("setting-default-cat");
    if (defCatSelect) defCatSelect.value = currentSettings.default_category || "java";

    // 2. Personalization
    const expSelect = document.getElementById("setting-exp-level");
    if (expSelect) expSelect.value = currentSettings.experience_level || "Beginner";

    const goalInput = document.getElementById("setting-career-goals");
    if (goalInput) goalInput.value = currentSettings.career_goals || "";

    const curSkillsInput = document.getElementById("setting-current-skills");
    if (curSkillsInput) curSkillsInput.value = currentSettings.current_skills || "";

    const desSkillsInput = document.getElementById("setting-desired-skills");
    if (desSkillsInput) desSkillsInput.value = currentSettings.desired_skills || "";

    const lStyleSelect = document.getElementById("setting-learning-style");
    if (lStyleSelect) lStyleSelect.value = currentSettings.learning_style || "Hands-on projects";

    const dTimeSelect = document.getElementById("setting-daily-time");
    if (dTimeSelect) dTimeSelect.value = currentSettings.daily_learning_time || "1-2 hours";

    // 3. Custom Instructions
    const customInstArea = document.getElementById("setting-custom-instructions");
    if (customInstArea) customInstArea.value = currentSettings.custom_instructions || "";

    // 4. Memory Toggle
    const memToggle = document.getElementById("setting-memory-enabled");
    if (memToggle) memToggle.checked = Boolean(currentSettings.memory_enabled);

    // 5. Chat Prefs
    const enterSendToggle = document.getElementById("setting-enter-to-send");
    if (enterSendToggle) enterSendToggle.checked = Boolean(currentSettings.enter_to_send);

    const delConfirmToggle = document.getElementById("setting-delete-confirm");
    if (delConfirmToggle) delConfirmToggle.checked = Boolean(currentSettings.delete_confirmation);

    // 6. Notifications
    const notifToggle = document.getElementById("setting-notifications-enabled");
    if (notifToggle) notifToggle.checked = Boolean(currentSettings.notifications_enabled);

    // 7. Voice & Accessibility
    const fontSelect = document.getElementById("setting-font-size");
    if (fontSelect) fontSelect.value = currentSettings.font_size || "medium";
    document.documentElement.setAttribute("data-font-size", currentSettings.font_size || "medium");

    const motionToggle = document.getElementById("setting-reduced-motion");
    if (motionToggle) motionToggle.checked = Boolean(currentSettings.reduced_motion);
    document.documentElement.setAttribute("data-reduced-motion", Boolean(currentSettings.reduced_motion));

    const contrastToggle = document.getElementById("setting-high-contrast");
    if (contrastToggle) contrastToggle.checked = currentSettings.contrast === "high";

    // 8. Account details
    const accName = document.getElementById("account-name-val");
    const accEmail = document.getElementById("account-email-val");
    const accBadge = document.getElementById("account-status-badge");
    const googleStatus = document.getElementById("google-service-status");
    const googleAction = document.getElementById("google-service-action-btn");

    if (currentUser) {
        if (accName) accName.textContent = currentUser.name;
        if (accEmail) accEmail.textContent = currentUser.email;
        if (accBadge) {
            accBadge.textContent = "Google Authenticated";
            accBadge.className = "badge-success";
        }
        if (googleStatus) googleStatus.textContent = `Connected as ${currentUser.email}`;
        if (googleAction) {
            googleAction.textContent = "Sign Out";
            googleAction.onclick = signOutUser;
        }
    } else {
        if (accName) accName.textContent = "Guest Student";
        if (accEmail) accEmail.textContent = "No account linked";
        if (accBadge) {
            accBadge.textContent = "Guest Session";
            accBadge.className = "badge-neutral";
        }
        if (googleStatus) googleStatus.textContent = "Status: Guest session";
        if (googleAction) {
            googleAction.textContent = "Sign In";
            googleAction.onclick = () => {
                if (demoSigninBtn) demoSigninBtn.click();
            };
        }
    }
}

/* ==================================================
 * Theme Management Controller (Light, Dark, System)
 * ================================================== */

let currentThemePref = localStorage.getItem("internbot_theme") || "system";

function resolveActiveTheme(preference) {
    if (preference === "system") {
        return (window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches) ? "dark" : "light";
    }
    return preference === "dark" ? "dark" : "light";
}

function setTheme(preference, saveToServer = false) {
    if (!["light", "dark", "system"].includes(preference)) {
        preference = "system";
    }

    currentThemePref = preference;
    const active = resolveActiveTheme(preference);

    // 1. Immediately apply to HTML root attributes
    document.documentElement.setAttribute("data-theme", active);
    document.documentElement.setAttribute("data-theme-preference", preference);

    // 2. Persist to localStorage immediately
    try {
        localStorage.setItem("internbot_theme", preference);
    } catch (e) {}

    // Update in-memory settings object
    currentSettings.theme = preference;

    // 3. Synchronize all UI selectors across the dashboard
    syncThemeUI(preference, active);

    // 4. Optionally save to cloud database / server endpoint
    if (saveToServer) {
        saveSettingsPayload(currentSettings).then(() => {
            showThemeSaveFeedback(preference);
        }).catch(err => {
            console.error("Failed to save theme setting to server:", err);
        });
    }
}

function syncThemeUI(preference, active) {
    // A. Topbar theme buttons
    const topbarBtns = document.querySelectorAll("#topbar-theme-switcher .theme-pill-btn");
    topbarBtns.forEach(btn => {
        const val = btn.getAttribute("data-theme-val");
        if (val === preference) {
            btn.classList.add("active");
            btn.setAttribute("aria-pressed", "true");
        } else {
            btn.classList.remove("active");
            btn.setAttribute("aria-pressed", "false");
        }
    });

    // B. Sidebar theme buttons & indicator
    const sidebarBtns = document.querySelectorAll("#sidebar-theme-pill .sidebar-theme-btn");
    sidebarBtns.forEach(btn => {
        const val = btn.getAttribute("data-theme-val");
        if (val === preference) {
            btn.classList.add("active");
            btn.setAttribute("aria-pressed", "true");
        } else {
            btn.classList.remove("active");
            btn.setAttribute("aria-pressed", "false");
        }
    });

    const sidebarCurrentText = document.getElementById("sidebar-theme-current-text");
    if (sidebarCurrentText) {
        if (preference === "system") {
            sidebarCurrentText.textContent = `Auto (${active === "dark" ? "Dark" : "Light"})`;
        } else if (preference === "dark") {
            sidebarCurrentText.textContent = "Dark";
        } else {
            sidebarCurrentText.textContent = "Light";
        }
    }

    // C. Settings Appearance Cards
    const themeCards = document.querySelectorAll(".theme-option-card");
    themeCards.forEach(card => {
        const choice = card.getAttribute("data-theme-choice");
        if (choice === preference) {
            card.classList.add("active");
            card.setAttribute("aria-checked", "true");
        } else {
            card.classList.remove("active");
            card.setAttribute("aria-checked", "false");
        }
    });

    // D. Settings General dropdown
    const generalSelect = document.getElementById("setting-theme");
    if (generalSelect && generalSelect.value !== preference) {
        generalSelect.value = preference;
    }

    // E. Appearance status banner
    const activeLabel = document.getElementById("appearance-active-label");
    const activeSub = document.getElementById("appearance-active-sub");
    if (activeLabel) {
        if (preference === "system") {
            activeLabel.textContent = `System (${active === "dark" ? "Dark Mode Active" : "Light Mode Active"})`;
        } else if (preference === "dark") {
            activeLabel.textContent = "Dark Theme Active";
        } else {
            activeLabel.textContent = "Light Theme Active";
        }
    }
    if (activeSub) {
        if (preference === "system") {
            activeSub.textContent = `Automatically matching your operating system color scheme (${active}).`;
        } else if (preference === "dark") {
            activeSub.textContent = "Comfortable #212121 dark interface enabled for low-light environments.";
        } else {
            activeSub.textContent = "Crisp white background palette enabled for high clarity.";
        }
    }
}

function showThemeSaveFeedback(preference) {
    const toast = document.getElementById("theme-save-toast");
    const feedback = document.getElementById("appearance-save-feedback");
    
    if (toast) {
        toast.classList.remove("hidden");
        setTimeout(() => toast.classList.add("hidden"), 3000);
    }
    if (feedback) {
        feedback.textContent = `✓ Saved ${preference.charAt(0).toUpperCase() + preference.slice(1)} theme preference.`;
        setTimeout(() => { feedback.textContent = ""; }, 3000);
    }
}

function applyTheme(theme) {
    setTheme(theme, false);
}

function initThemeManager() {
    // 1. Resolve initial theme preference
    const saved = localStorage.getItem("internbot_theme") || currentSettings.theme || "system";
    setTheme(saved, false);

    // 2. Attach system OS change listener
    if (window.matchMedia) {
        const osDarkQuery = window.matchMedia("(prefers-color-scheme: dark)");
        const handleOsChange = () => {
            if (currentThemePref === "system") {
                const active = resolveActiveTheme("system");
                document.documentElement.setAttribute("data-theme", active);
                syncThemeUI("system", active);
            }
        };

        if (osDarkQuery.addEventListener) {
            osDarkQuery.addEventListener("change", handleOsChange);
        } else if (osDarkQuery.addListener) {
            osDarkQuery.addListener(handleOsChange);
        }
    }

    // 3. Topbar theme button clicks
    const topbarBtns = document.querySelectorAll("#topbar-theme-switcher .theme-pill-btn");
    topbarBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            const val = btn.getAttribute("data-theme-val");
            setTheme(val, true);
        });
    });

    // 4. Sidebar theme button clicks
    const sidebarBtns = document.querySelectorAll("#sidebar-theme-pill .sidebar-theme-btn");
    sidebarBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            const val = btn.getAttribute("data-theme-val");
            setTheme(val, true);
        });
    });

    // 5. Settings Appearance Cards
    const themeCards = document.querySelectorAll(".theme-option-card");
    themeCards.forEach(card => {
        const selectCard = () => {
            const choice = card.getAttribute("data-theme-choice");
            setTheme(choice, true);
        };

        card.addEventListener("click", selectCard);
        card.addEventListener("keydown", (e) => {
            if (e.key === "Enter" || e.key === " ") {
                e.preventDefault();
                selectCard();
            }
        });
    });

    // 6. Settings Appearance Save Button
    const saveAppearanceBtn = document.getElementById("save-appearance-btn");
    if (saveAppearanceBtn) {
        saveAppearanceBtn.addEventListener("click", () => {
            setTheme(currentThemePref, true);
        });
    }

    // 7. General Settings dropdown change
    const themeSelect = document.getElementById("setting-theme");
    if (themeSelect) {
        themeSelect.addEventListener("change", () => {
            setTheme(themeSelect.value, true);
        });
    }
}

// Settings Action Buttons Handlers
function initSettingsActions() {
    // Save General Settings
    const saveGenBtn = document.getElementById("save-general-btn");
    if (saveGenBtn) {
        saveGenBtn.onclick = async () => {
            const theme = document.getElementById("setting-theme").value;
            const lang = document.getElementById("setting-language").value;
            const style = document.getElementById("setting-answer-style").value;
            const cat = document.getElementById("setting-default-cat").value;

            currentSettings.theme = theme;
            currentSettings.language = lang;
            currentSettings.answer_style = style;
            currentSettings.default_category = cat;

            setTheme(theme, false);
            await saveSettingsPayload(currentSettings);
            alert("General settings saved successfully.");
        };
    }

    // Reset All Settings
    const resetBtn = document.getElementById("reset-settings-btn");
    if (resetBtn) {
        resetBtn.onclick = async () => {
            if (!confirm("Reset all settings to default values?")) return;
            currentSettings = {
                theme: "light",
                language: "en",
                answer_style: "balanced",
                default_category: "java",
                experience_level: "Beginner",
                career_goals: "Software Engineering Internship",
                current_skills: "Java, Python, Git",
                desired_skills: "Spring Boot, React, Docker",
                learning_style: "Hands-on projects",
                daily_learning_time: "1-2 hours",
                custom_instructions: "",
                memory_enabled: 1,
                enter_to_send: 1,
                delete_confirmation: 1,
                notifications_enabled: 1,
                font_size: "medium",
                reduced_motion: 0,
                contrast: "normal"
            };
            applySettingsToUI();
            await saveSettingsPayload(currentSettings);
            alert("Settings reset to defaults.");
        };
    }

    // Save Personalization
    const savePersBtn = document.getElementById("save-personalization-btn");
    if (savePersBtn) {
        savePersBtn.onclick = async () => {
            currentSettings.experience_level = document.getElementById("setting-exp-level").value;
            currentSettings.career_goals = document.getElementById("setting-career-goals").value.trim();
            currentSettings.current_skills = document.getElementById("setting-current-skills").value.trim();
            currentSettings.desired_skills = document.getElementById("setting-desired-skills").value.trim();
            currentSettings.learning_style = document.getElementById("setting-learning-style").value;
            currentSettings.daily_learning_time = document.getElementById("setting-daily-time").value;

            await saveSettingsPayload(currentSettings);
            alert("Personalization profile saved.");
        };
    }

    // Save Custom Instructions
    const saveInstBtn = document.getElementById("save-custom-instructions-btn");
    if (saveInstBtn) {
        saveInstBtn.onclick = async () => {
            currentSettings.custom_instructions = document.getElementById("setting-custom-instructions").value.trim();
            await saveSettingsPayload(currentSettings);
            alert("Custom instructions saved and applied to AI answers.");
        };
    }

    // Save Chat Prefs
    const saveChatPrefsBtn = document.getElementById("save-chat-prefs-btn");
    if (saveChatPrefsBtn) {
        saveChatPrefsBtn.onclick = async () => {
            currentSettings.enter_to_send = document.getElementById("setting-enter-to-send").checked ? 1 : 0;
            currentSettings.delete_confirmation = document.getElementById("setting-delete-confirm").checked ? 1 : 0;
            await saveSettingsPayload(currentSettings);
            alert("Chat preferences saved.");
        };
    }

    // Save Accessibility
    const saveVoiceBtn = document.getElementById("save-voice-access-btn");
    if (saveVoiceBtn) {
        saveVoiceBtn.onclick = async () => {
            const font = document.getElementById("setting-font-size").value;
            const motion = document.getElementById("setting-reduced-motion").checked ? 1 : 0;
            const contrast = document.getElementById("setting-high-contrast").checked ? "high" : "normal";

            currentSettings.font_size = font;
            currentSettings.reduced_motion = motion;
            currentSettings.contrast = contrast;

            document.documentElement.setAttribute("data-font-size", font);
            document.documentElement.setAttribute("data-reduced-motion", Boolean(motion));

            await saveSettingsPayload(currentSettings);
            alert("Accessibility settings saved.");
        };
    }

    // Export Data (JSON)
    const exportBtn = document.getElementById("export-data-btn");
    if (exportBtn) {
        exportBtn.onclick = async () => {
            if (!currentUser) {
                alert("Sign in required to export cloud saved data.");
                return;
            }
            try {
                const res = await fetch("/api/export-data");
                const data = await res.json();
                const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
                const url = URL.createObjectURL(blob);
                const a = document.createElement("a");
                a.href = url;
                a.download = `internbot_export_${new Date().toISOString().slice(0, 10)}.json`;
                a.click();
                URL.revokeObjectURL(url);
            } catch (e) {
                console.error("Export error:", e);
                alert("Failed to export data.");
            }
        };
    }

    // Clear Local Chat
    const clearChatBtn = document.getElementById("clear-local-chat-btn");
    if (clearChatBtn) {
        clearChatBtn.onclick = () => {
            if (confirm("Clear local active chat window?")) {
                chatBox.innerHTML = "";
                addMessage(WELCOME_MESSAGE, "bot");
                renderSuggestions(DEFAULT_SUGGESTIONS);
                switchView("home");
            }
        };
    }

    // Delete Account
    const deleteAccBtn = document.getElementById("delete-account-btn");
    if (deleteAccBtn) {
        deleteAccBtn.onclick = async () => {
            const conf = prompt("WARNING: This will permanently delete your account, saved chats, bookmarks, and skill tracker. Type 'DELETE' to confirm:");
            if (conf === "DELETE") {
                try {
                    await fetch("/api/delete-account", { method: "POST" });
                    alert("Account and associated data deleted.");
                    window.location.reload();
                } catch (e) {
                    alert("Account deletion failed.");
                }
            }
        };
    }

    // Real Gemini Test Button
    const testGeminiBtn = document.getElementById("test-gemini-btn");
    if (testGeminiBtn) {
        testGeminiBtn.onclick = async () => {
            testGeminiBtn.disabled = true;
            testGeminiBtn.textContent = "Testing Gemini Connection...";
            try {
                const res = await fetch("/api/test-gemini", { method: "POST" });
                const data = await res.json();
                testGeminiBtn.disabled = false;
                testGeminiBtn.textContent = "Run Real Connection Test";

                const badge = document.getElementById("gemini-status-badge");
                const desc = document.getElementById("gemini-status-desc");
                const meta = document.getElementById("gemini-status-meta");

                if (data.connected) {
                    if (badge) {
                        badge.className = "badge-success";
                        badge.textContent = `Connected (${data.model})`;
                    }
                    if (desc) desc.textContent = data.message;
                    if (meta) meta.innerHTML = `<strong>Response verification:</strong> "${data.response_preview}"`;
                } else {
                    if (badge) {
                        badge.className = "badge-status-neutral";
                        badge.textContent = "Not Connected / Offline FAQ Active";
                    }
                    if (desc) desc.textContent = data.message;
                    if (meta) meta.innerHTML = `<span class="text-danger">${data.error}</span>`;
                }
            } catch (e) {
                testGeminiBtn.disabled = false;
                testGeminiBtn.textContent = "Run Real Connection Test";
                console.error("Gemini test failed:", e);
            }
        };
    }
}

async function saveSettingsPayload(settings) {
    if (currentUser) {
        try {
            await fetch("/api/settings", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(settings)
            });
        } catch (e) {
            console.error("Failed to save settings to server:", e);
        }
    } else {
        localStorage.setItem("internbot_guest_settings", JSON.stringify(settings));
    }
}

// Memory Manager
async function loadMemoryItems() {
    const list = document.getElementById("memory-items-list");
    if (!list) return;

    if (!currentUser) {
        list.innerHTML = '<p class="text-muted">Sign in to review and manage remembered preferences.</p>';
        return;
    }

    try {
        const res = await fetch("/api/memory");
        const data = await res.json();
        if (!data.memories || data.memories.length === 0) {
            list.innerHTML = '<p class="text-muted">No memory items saved yet.</p>';
            return;
        }

        let html = '<div style="display: flex; flex-direction: column; gap: 8px;">';
        data.memories.forEach(m => {
            html += `
                <div style="display: flex; justify-content: space-between; align-items: center; padding: 6px 12px; background: var(--card-bg); border: 1px solid var(--border); border-radius: 6px;">
                    <span><strong>${m.key}:</strong> ${m.value}</span>
                    <button class="btn btn-ghost btn-sm text-danger" onclick="deleteMemoryItem(${m.id})">✕</button>
                </div>
            `;
        });
        html += "</div>";
        list.innerHTML = html;
    } catch (e) {
        console.error("Failed to load memory:", e);
    }
}

window.deleteMemoryItem = async function(id) {
    try {
        await fetch(`/api/memory/${id}`, { method: "DELETE" });
        loadMemoryItems();
    } catch (e) {
        console.error("Failed to delete memory item:", e);
    }
};

const addMemoryBtn = document.getElementById("add-memory-btn");
if (addMemoryBtn) {
    addMemoryBtn.onclick = async () => {
        if (!currentUser) {
            alert("Sign in required to save memory items.");
            return;
        }
        const key = document.getElementById("new-mem-key").value.trim();
        const value = document.getElementById("new-mem-val").value.trim();
        if (!key || !value) return;

        try {
            await fetch("/api/memory", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ key, value, category: "preference" })
            });
            document.getElementById("new-mem-key").value = "";
            document.getElementById("new-mem-val").value = "";
            loadMemoryItems();
        } catch (e) {
            console.error("Failed to add memory:", e);
        }
    };
}

const clearMemBtn = document.getElementById("clear-all-memory-btn");
if (clearMemBtn) {
    clearMemBtn.onclick = async () => {
        if (!confirm("Clear all saved preferences and memories?")) return;
        try {
            await fetch("/api/memory/clear", { method: "POST" });
            loadMemoryItems();
        } catch (e) {
            console.error("Clear memory error:", e);
        }
    };
}

async function checkGeminiStatus() {
    try {
        const res = await fetch("/test");
        const data = await res.json();
        const badge = document.getElementById("gemini-status-badge");
        const desc = document.getElementById("gemini-status-desc");

        if (data.is_valid_format) {
            if (badge) {
                badge.className = "badge-success";
                badge.textContent = "Gemini AI Configured";
            }
            if (desc) desc.textContent = "API key configured. Ready for generative answers and web grounding.";
        } else {
            if (badge) {
                badge.className = "badge-status-neutral";
                badge.textContent = "Offline FAQ Fallback Active";
            }
            if (desc) desc.textContent = data.message;
        }
    } catch (e) {
        console.error("Health check error:", e);
    }
}


/* ==================================================
 * 9. Company Portals View
 * ================================================== */

async function loadCompanies() {
    if (!companiesGrid) return;
    try {
        const res = await fetch("/api/companies");
        const data = await res.json();
        if (data.companies) {
            companiesCache = data.companies;
            renderCompanies(companiesCache);
            initCompanyFilters();
        }
    } catch (e) {
        console.error("Failed to load companies:", e);
    }
}

function renderCompanies(list) {
    if (!companiesGrid) return;
    let html = "";
    list.forEach(c => {
        html += `
            <div class="company-card">
                <div class="company-card-header">
                    <span class="company-badge-icon">${c.badge || "🏢"}</span>
                    <div>
                        <h4 class="company-name">${c.name}</h4>
                        <span class="company-category">${c.category}</span>
                    </div>
                </div>
                <p class="company-desc">${c.description}</p>
                <div class="company-programs">
                    <strong>Programs:</strong>
                    <ul class="program-tags">
                        ${(c.programs || []).map(p => `<li>${p}</li>`).join("")}
                    </ul>
                </div>
                <div class="company-actions">
                    <a href="${c.url}" target="_blank" rel="noopener noreferrer" class="btn btn-primary btn-sm">Official Portal ↗</a>
                    <button type="button" class="btn btn-outline btn-sm" onclick="searchAsk('${encodeURIComponent(c.query)}')">Ask Info</button>
                </div>
            </div>
        `;
    });
    companiesGrid.innerHTML = html;
}

function initCompanyFilters() {
    if (!companiesFilterBar) return;
    const chips = companiesFilterBar.querySelectorAll(".filter-chip");
    chips.forEach(chip => {
        chip.addEventListener("click", () => {
            chips.forEach(c => c.classList.remove("active"));
            chip.classList.add("active");
            const filter = chip.getAttribute("data-filter");
            if (filter === "all") {
                renderCompanies(companiesCache);
            } else {
                const filtered = companiesCache.filter(c => c.category === filter);
                renderCompanies(filtered);
            }
        });
    });
}


/* ==================================================
 * 10. Saved Chat History View
 * ================================================== */

async function loadHistory() {
    if (!historyContainer) return;
    if (!currentUser) {
        historyContainer.innerHTML = '<div class="search-placeholder">Sign in to save and reopen previous internship chats.</div>';
        return;
    }

    try {
        const res = await fetch("/api/history");
        const data = await res.json();
        const sessions = data.sessions || [];

        if (sessions.length === 0) {
            historyContainer.innerHTML = '<div class="search-placeholder">No saved conversations yet. Start chatting and save your sessions!</div>';
            return;
        }

        let html = '<div class="history-list">';
        sessions.forEach(s => {
            html += `
                <div class="history-card" onclick="openSession('${s.id}')">
                    <div class="history-card-info">
                        <h4>${s.title}</h4>
                        <p class="text-muted">${s.last_message ? s.last_message.slice(0, 80) + '...' : 'No messages yet'}</p>
                        <span class="history-meta">📅 ${new Date(s.updated_at).toLocaleDateString()} · ${s.message_count || 0} messages</span>
                    </div>
                    <div class="history-card-actions" onclick="event.stopPropagation()">
                        <button class="btn btn-ghost btn-sm" onclick="renameSessionPrompt('${s.id}', '${encodeURIComponent(s.title)}')">✎</button>
                        <button class="btn btn-ghost btn-sm text-danger" onclick="deleteSessionAction('${s.id}')">✕</button>
                    </div>
                </div>
            `;
        });
        html += "</div>";
        historyContainer.innerHTML = html;
    } catch (e) {
        console.error("Failed to load history:", e);
    }
}

async function createSession(title = "New Conversation") {
    try {
        const res = await fetch("/api/history", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ title })
        });
        const data = await res.json();
        if (data.session) {
            currentSessionId = data.session.id;
            chatBox.innerHTML = "";
            addMessage(`Started new session: "${data.session.title}"`, "bot");
            renderSuggestions(DEFAULT_SUGGESTIONS);
        }
    } catch (e) {
        console.error("Create session error:", e);
    }
}

window.openSession = async function(sessionId) {
    try {
        const res = await fetch(`/api/history/${sessionId}`);
        const data = await res.json();
        if (data.messages) {
            currentSessionId = sessionId;
            chatBox.innerHTML = "";
            data.messages.forEach(m => {
                addMessage(m.text, m.role === "bot" ? "bot" : "user");
            });
            switchView("home");
        }
    } catch (e) {
        console.error("Open session error:", e);
    }
};

window.renameSessionPrompt = async function(sessionId, encodedCurrent) {
    const current = decodeURIComponent(encodedCurrent);
    const newTitle = prompt("Enter new title for conversation:", current);
    if (!newTitle || newTitle.trim() === "") return;

    try {
        await fetch(`/api/history/${sessionId}`, {
            method: "PATCH",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ title: newTitle.trim() })
        });
        loadHistory();
    } catch (e) {
        console.error("Rename session error:", e);
    }
};

window.deleteSessionAction = async function(sessionId) {
    if (currentSettings.delete_confirmation && !confirm("Delete this conversation?")) return;
    try {
        await fetch(`/api/history/${sessionId}`, { method: "DELETE" });
        if (currentSessionId === sessionId) currentSessionId = null;
        loadHistory();
    } catch (e) {
        console.error("Delete session error:", e);
    }
};


/* ==================================================
 * 11. Image Notice / Poster Analyzer Modal
 * ================================================== */

function initNoticeModal() {
    const modal = document.getElementById("notice-modal");
    const openBtn = document.getElementById("attach-notice-btn");
    const closeBtn = document.getElementById("notice-modal-close");
    const cancelBtn = document.getElementById("notice-cancel-btn");
    const dropzone = document.getElementById("notice-dropzone");
    const fileInput = document.getElementById("notice-file-input");
    const previewWrap = document.getElementById("preview-wrap");
    const previewImg = document.getElementById("notice-preview-img");
    const filenameEl = document.getElementById("preview-filename");
    const analyzeBtn = document.getElementById("notice-analyze-btn");
    const outputEl = document.getElementById("notice-analysis-output");

    let chosenNoticeFile = null;

    if (openBtn) openBtn.onclick = () => modal.classList.remove("hidden");
    if (closeBtn) closeBtn.onclick = () => modal.classList.add("hidden");
    if (cancelBtn) cancelBtn.onclick = () => modal.classList.add("hidden");

    if (dropzone && fileInput) {
        dropzone.onclick = () => fileInput.click();
        fileInput.onchange = () => {
            if (fileInput.files.length > 0) {
                const file = fileInput.files[0];
                chosenNoticeFile = file;
                filenameEl.textContent = file.name;
                const reader = new FileReader();
                reader.onload = (e) => {
                    previewImg.src = e.target.result;
                    previewWrap.classList.remove("hidden");
                };
                reader.readAsDataURL(file);
                analyzeBtn.disabled = false;
            }
        };
    }

    if (analyzeBtn) {
        analyzeBtn.onclick = async () => {
            if (!chosenNoticeFile) return;

            analyzeBtn.disabled = true;
            analyzeBtn.textContent = "Analyzing Notice...";
            outputEl.classList.remove("hidden");
            outputEl.innerHTML = "<em>Analyzing image text and authenticity checks...</em>";

            const fd = new FormData();
            fd.append("notice", chosenNoticeFile);

            try {
                const res = await fetch("/api/upload-notice", {
                    method: "POST",
                    body: fd
                });
                const data = await res.json();
                analyzeBtn.disabled = false;
                analyzeBtn.textContent = "Analyze Notice";

                if (data.success) {
                    outputEl.innerHTML = formatBotMessage(data.analysis);
                } else {
                    outputEl.innerHTML = `<span class="text-danger">${data.error || "Verification failed"}</span>`;
                }
            } catch (err) {
                analyzeBtn.disabled = false;
                analyzeBtn.textContent = "Analyze Notice";
                outputEl.innerHTML = '<span class="text-danger">Failed to process notice. Please try again.</span>';
            }
        };
    }
}


/* ==================================================
 * 12. Authentication & User Profile Management
 * ================================================== */

window.handleGoogleCredential = async function(response) {
    if (!response || !response.credential) return;
    try {
        const res = await fetch("/api/auth/google", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ credential: response.credential })
        });
        const data = await res.json();
        if (data.user) {
            onUserLoggedIn(data.user);
        }
    } catch (e) {
        console.error("Google auth failed:", e);
    }
};

if (demoSigninBtn) {
    demoSigninBtn.addEventListener("click", async () => {
        try {
            const res = await fetch("/api/auth/google", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ name: "Demo Student", email: "student_demo@gmail.com" })
            });
            const data = await res.json();
            if (data.user) {
                onUserLoggedIn(data.user);
            }
        } catch (e) {
            console.error("Demo login error:", e);
        }
    });
}

if (logoutBtn) {
    logoutBtn.addEventListener("click", signOutUser);
}

async function signOutUser() {
    try {
        await fetch("/api/auth/logout", { method: "POST" });
        currentUser = null;
        currentSessionId = null;
        if (authGuestBox) authGuestBox.classList.remove("hidden");
        if (authUserBox) authUserBox.classList.add("hidden");
        applySettingsToUI();
        window.location.reload();
    } catch (e) {
        console.error("Logout error:", e);
    }
}

function onUserLoggedIn(user) {
    currentUser = user;
    if (authGuestBox) authGuestBox.classList.add("hidden");
    if (authUserBox) authUserBox.classList.remove("hidden");

    if (userNameDisplay) userNameDisplay.textContent = user.name;
    if (userEmailDisplay) userEmailDisplay.textContent = user.email;
    if (userAvatarImg && user.picture) userAvatarImg.src = user.picture;

    loadSettingsView();
    loadApplications();
    loadBookmarks();
    loadReminders();
    loadHistory();
}

async function checkAuthSession() {
    try {
        const res = await fetch("/api/auth/me");
        const data = await res.json();
        if (data.logged_in && data.user) {
            onUserLoggedIn(data.user);
        } else {
            // Restore guest settings from localStorage
            const localSettings = localStorage.getItem("internbot_guest_settings");
            if (localSettings) {
                try {
                    currentSettings = Object.assign(currentSettings, JSON.parse(localSettings));
                } catch (e) {}
            }
            applySettingsToUI();
        }
    } catch (e) {
        console.error("Auth check failed:", e);
    }
}


/* ==================================================
 * 13. Application Initialization
 * ================================================== */

document.addEventListener("DOMContentLoaded", () => {
    // 1. Initialize theme controller immediately
    initThemeManager();

    // 2. Initialize views and auth
    checkAuthSession();
    initSearchControls();
    initVoiceInput();
    initNoticeModal();
    initResumeChecker();
    initSettingsSubnav();
    initSettingsActions();

    // 3. Render welcome message and default suggestions
    if (chatBox && chatBox.children.length === 0) {
        addMessage(WELCOME_MESSAGE, "bot");
        renderSuggestions(DEFAULT_SUGGESTIONS);
    }
});