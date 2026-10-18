"""
Comprehensive Domain Data for Internship FAQ Assistant.
Covers:
- 4 Primary Categories: Java Development, Python Development, JavaScript Development, Full-Stack Development
- Learning Roadmaps (Milestones, Skills, Concepts)
- Project Recommendations with transparent 'Why this project' rationale
- External LinkedIn Internship Discovery Links (clearly labeled as external job search)
- Topic-wise MCQs with answers and explanations
- Mock Interview Questions & Model Answers
"""

CATEGORIES = [
    {
        "id": "java",
        "title": "Java Development",
        "icon": "☕",
        "badge": "Backend & Enterprise",
        "skills": ["Core Java", "OOP", "Collections Framework", "Exception Handling", "JDBC", "SQL", "Spring Boot", "REST APIs", "Git", "JUnit / Mockito Testing"],
        "experience_levels": ["Beginner", "Intermediate", "Advanced"],
        "external_link": {
            "title": "Java Internships on LinkedIn",
            "url": "https://www.linkedin.com/jobs/java-intern-jobs/",
            "disclaimer": "External job-search link. Vacancies and criteria are managed by respective employers on LinkedIn, not guaranteed by InternBot."
        },
        "description": "Enterprise backend systems, high-throughput microservices, robust multithreading, and Spring Boot web services.",
        "roadmap": [
            {
                "step": 1,
                "title": "Java Fundamentals & OOP Mastery",
                "duration": "Weeks 1-3",
                "topics": ["Primitive types, control flow, loops", "Classes, Objects, Constructors", "Inheritance, Polymorphism, Abstraction, Encapsulation", "Interfaces and Abstract Classes"],
                "skills": ["Core Java", "OOP"]
            },
            {
                "step": 2,
                "title": "Collections & Exception Handling",
                "duration": "Weeks 4-5",
                "topics": ["List, ArrayList, LinkedList", "Set, HashSet, TreeSet", "Map, HashMap, ConcurrentHashMap", "Generics, Comparable & Comparator", "Try-catch-finally, Custom Exceptions"],
                "skills": ["Collections Framework", "Exception Handling"]
            },
            {
                "step": 3,
                "title": "Database Integration with JDBC & SQL",
                "duration": "Weeks 6-7",
                "topics": ["Relational Schema Design & Normalization", "SQL queries: Joins, Indexing, Transactions", "JDBC Connection, PreparedStatement, ResultSet", "DAO Pattern"],
                "skills": ["JDBC", "SQL"]
            },
            {
                "step": 4,
                "title": "Spring Boot & REST API Development",
                "duration": "Weeks 8-10",
                "topics": ["Spring Core, Dependency Injection, Inversion of Control", "Spring Boot Starter, Actuator", "Building REST Controllers, JSON Serialization", "Spring Data JPA & Hibernate ORM"],
                "skills": ["Spring Boot", "REST APIs"]
            },
            {
                "step": 5,
                "title": "Testing, Git & Deployment",
                "duration": "Weeks 11-12",
                "topics": ["Unit testing with JUnit 5 & Mockito", "Git branching, pull requests, semantic versioning", "Docker basics & deploying Spring Boot JAR to AWS/Render"],
                "skills": ["Git", "JUnit / Mockito Testing"]
            }
        ],
        "projects": [
            {
                "id": "java-proj-1",
                "title": "Student Management System",
                "difficulty": "Beginner",
                "tech_stack": ["Java", "JDBC", "MySQL", "Console/Swing"],
                "description": "CRUD management for student records, enrollment, grade calculations, and course assignment.",
                "why": "Demonstrates mastery of Object-Oriented Principles, SQL normalization, DAO architectural patterns, and defensive exception handling."
            },
            {
                "id": "java-proj-2",
                "title": "Hotel Reservation System",
                "difficulty": "Intermediate",
                "tech_stack": ["Java", "Spring Boot", "Spring Data JPA", "PostgreSQL", "REST APIs"],
                "description": "Room booking engine featuring date-range conflict detection, guest invoicing, and payment status tracking.",
                "why": "Shows enterprise Spring Boot capabilities: transactional boundaries (`@Transactional`), relational entity mappings (`@OneToMany`), and production REST design."
            },
            {
                "id": "java-proj-3",
                "title": "Library Management System",
                "difficulty": "Intermediate",
                "tech_stack": ["Java", "Spring Boot", "Hibernate", "MySQL", "JWT Security"],
                "description": "Digital library catalog with book checkout, fine calculation on overdue returns, and role-based access for librarians and students.",
                "why": "Proves proficiency in authentication workflows, date arithmetic, business rule validation, and automated unit testing."
            }
        ],
        "mcqs": [
            {
                "id": "java-q1",
                "topic": "OOP & Collections",
                "question": "What is the primary difference between HashMap and HashTable in Java?",
                "options": [
                    "HashMap is synchronized whereas HashTable is not synchronized",
                    "HashMap allows one null key and multiple null values, whereas HashTable does not allow any null key or value",
                    "HashTable is faster than HashMap in single-threaded environments",
                    "HashMap guarantees the order of elements based on insertion"
                ],
                "answer_index": 1,
                "explanation": "HashMap is non-synchronized and allows one null key and multiple null values. HashTable is legacy, synchronized (thread-safe with lock contention), and does not permit null keys or values."
            },
            {
                "id": "java-q2",
                "topic": "Exception Handling",
                "question": "Which of the following is an Unchecked Exception in Java?",
                "options": [
                    "IOException",
                    "SQLException",
                    "NullPointerException",
                    "ClassNotFoundException"
                ],
                "answer_index": 2,
                "explanation": "NullPointerException extends RuntimeException, making it an unchecked exception. The compiler does not enforce try-catch or throws clauses for unchecked exceptions."
            },
            {
                "id": "java-q3",
                "topic": "Spring Boot",
                "question": "What does the `@SpringBootApplication` annotation combine?",
                "options": [
                    "@Configuration, @EnableAutoConfiguration, and @ComponentScan",
                    "@Controller, @Service, and @Repository",
                    "@Entity, @Table, and @Id",
                    "@Component, @Autowired, and @Qualifier"
                ],
                "answer_index": 0,
                "explanation": "`@SpringBootApplication` is a convenience meta-annotation combining `@Configuration`, `@EnableAutoConfiguration`, and `@ComponentScan`."
            }
        ],
        "interview_questions": [
            {
                "question": "Explain the difference between `==` and `.equals()` in Java.",
                "key_points": [
                    "`==` compares memory addresses (reference equality) for objects, and actual bit values for primitives.",
                    "`.equals()` is a method in `java.lang.Object` intended to compare logical or state equivalence.",
                    "String and wrapper classes override `.equals()` to compare contents, but custom classes must override both `.equals()` and `.hashCode()` together."
                ]
            },
            {
                "question": "What is Inversion of Control (IoC) and Dependency Injection (DI) in Spring Boot?",
                "key_points": [
                    "IoC shifts object lifecycle control from individual classes to the Spring container.",
                    "Dependency Injection is the design pattern implementing IoC by supplying collaborators via constructors, setters, or fields.",
                    "Benefits: Loose coupling, straightforward test mocking (e.g. Mockito), and centralized lifecycle management."
                ]
            }
        ]
    },
    {
        "id": "python",
        "title": "Python Development",
        "icon": "🐍",
        "badge": "Backend, Scripting & AI",
        "skills": ["Python Fundamentals", "OOP", "Data Structures", "File Handling", "Flask", "Django", "APIs", "SQL", "Unit Testing (pytest)"],
        "experience_levels": ["Beginner", "Intermediate", "Advanced"],
        "external_link": {
            "title": "Python Internships on LinkedIn",
            "url": "https://www.linkedin.com/jobs/python-intern-jobs/",
            "disclaimer": "External job-search link. Vacancies and criteria are managed by respective employers on LinkedIn, not guaranteed by InternBot."
        },
        "description": "Rapid backend development, web services, automation scripts, and foundational engineering for data science & AI pipelines.",
        "roadmap": [
            {
                "step": 1,
                "title": "Python Fundamentals & Idiomatic Syntax",
                "duration": "Weeks 1-2",
                "topics": ["Variables, dynamic typing, mutability", "List comprehensions, dict comprehensions, slicing", "Functions, *args, **kwargs, lambda functions", "Generators and yield"],
                "skills": ["Python Fundamentals"]
            },
            {
                "step": 2,
                "title": "OOP & Pythonic Architecture",
                "duration": "Weeks 3-4",
                "topics": ["Classes, `__init__`, `__repr__`, magic/dunder methods", "Inheritance, mixins, method resolution order (MRO)", "Decorators (`@staticmethod`, `@classmethod`, custom decorators)", "Context managers with `with` statement"],
                "skills": ["OOP", "Data Structures"]
            },
            {
                "step": 3,
                "title": "File Handling, OS & Automation",
                "duration": "Weeks 5-6",
                "topics": ["Pathlib, reading/writing JSON, CSV, binary files", "Regex pattern matching (`re` module)", "Web scraping basics (BeautifulSoup/requests)", "Subprocess & system task scheduling"],
                "skills": ["File Handling", "Automation"]
            },
            {
                "step": 4,
                "title": "Flask & REST API Engineering",
                "duration": "Weeks 7-9",
                "topics": ["Flask application factory, blueprints", "Request parsing, JSON serialization, HTTP status codes", "SQLite/PostgreSQL with SQLAlchemy ORM", "JWT authentication & CORS handling"],
                "skills": ["Flask", "APIs", "SQL"]
            },
            {
                "step": 5,
                "title": "Django & Production Testing",
                "duration": "Weeks 10-12",
                "topics": ["Django MTV architecture, ORM migrations, Admin portal", "REST framework (DRF) serializers & viewsets", "Writing test suites with `pytest` and `unittest`", "Deploying with Gunicorn and Docker"],
                "skills": ["Django", "Unit Testing (pytest)"]
            }
        ],
        "projects": [
            {
                "id": "py-proj-1",
                "title": "FAQ Chatbot & Knowledge Assistant",
                "difficulty": "Beginner",
                "tech_stack": ["Python", "Flask", "JSON/SQLite", "Regex"],
                "description": "Intelligent domain chatbot matching student queries against normalized knowledge vectors with offline fallback.",
                "why": "Demonstrates clean Flask routing, tokenization, text normalization, and resilient fallback engineering."
            },
            {
                "id": "py-proj-2",
                "title": "Automated Web Scraping & Alert Tool",
                "difficulty": "Intermediate",
                "tech_stack": ["Python", "BeautifulSoup4", "Requests", "SQLite", "SMTP"],
                "description": "Monitors target career portals for new internship openings and dispatches structured email/webhook notifications.",
                "why": "Proves understanding of HTTP networking, HTML parsing, scheduling, rate limiting, and robust error recovery."
            },
            {
                "id": "py-proj-3",
                "title": "REST API with Authentication & Role Controls",
                "difficulty": "Intermediate",
                "tech_stack": ["Python", "Flask/FastAPI", "SQLAlchemy", "JWT", "Pytest"],
                "description": "Secure API service with password hashing (bcrypt), token expiration, pagination, and automated test coverage.",
                "why": "Shows industry-standard backend security practices, relational modeling, and strict input validation."
            },
            {
                "id": "py-proj-4",
                "title": "Smart File Organizer & Deduplicator",
                "difficulty": "Beginner",
                "tech_stack": ["Python", "Pathlib", "OS", "Hashlib (SHA-256)"],
                "description": "Desktop utility scanning directories, sorting files by MIME types and creation date, and detecting exact duplicate files via cryptographic hashing.",
                "why": "Demonstrates practical file system operations, algorithmic hashing, and defensive I/O handling."
            }
        ],
        "mcqs": [
            {
                "id": "py-q1",
                "topic": "Python Core",
                "question": "What is the output of `bool([])` and `bool({})` in Python?",
                "options": [
                    "True, True",
                    "False, False",
                    "False, True",
                    "Raises a TypeError"
                ],
                "answer_index": 1,
                "explanation": "Empty containers (empty list `[]`, empty dict `{}`, empty tuple `()`, empty string `\"\"`) evaluate to `False` in boolean context due to Python's truth-value testing protocol."
            },
            {
                "id": "py-q2",
                "topic": "Decorators",
                "question": "What is a Python decorator at its core?",
                "options": [
                    "A class that inherits from `abc.ABC`",
                    "A function that accepts another function as an argument and extends its behavior without modifying its source",
                    "A compiler directive that compiles Python bytecode to C",
                    "A package manager tool like pip"
                ],
                "answer_index": 1,
                "explanation": "A decorator is a callable that takes another function/class as input and returns an augmented wrapper function, enabled by first-class functions in Python."
            },
            {
                "id": "py-q3",
                "topic": "Flask Framework",
                "question": "How do you correctly access incoming JSON payloads in a Flask POST request?",
                "options": [
                    "`request.args.get('json')`",
                    "`request.form['json']`",
                    "`request.get_json()`",
                    "`request.json_data()`"
                ],
                "answer_index": 2,
                "explanation": "`request.get_json()` parses the incoming request data as JSON. Passing `silent=True` safely prevents 400 bad request crashes on malformed data."
            }
        ],
        "interview_questions": [
            {
                "question": "What is the Global Interpreter Lock (GIL) in CPython?",
                "key_points": [
                    "The GIL is a mutex that prevents multiple native threads from executing Python bytecodes at once.",
                    "Why it exists: CPython's memory management is not thread-safe and relies on reference counting.",
                    "Impact: CPU-bound tasks do not achieve parallelism via `threading`; developers use `multiprocessing` or asynchronous I/O (`asyncio`) for concurrency."
                ]
            },
            {
                "question": "How do list comprehensions differ from generator expressions in memory efficiency?",
                "key_points": [
                    "List comprehensions `[x for x in data]` build the entire collection in memory at once.",
                    "Generator expressions `(x for x in data)` produce items lazily on demand using the iterator protocol.",
                    "For large or streaming datasets, generator expressions consume $O(1)$ memory compared to $O(N)$ for lists."
                ]
            }
        ]
    },
    {
        "id": "javascript",
        "title": "JavaScript Development",
        "icon": "⚡",
        "badge": "Frontend & Node.js",
        "skills": ["ES6+ Modern JavaScript", "DOM Manipulation", "Event Handling", "Promises & Async/Await", "React Fundamentals", "Node.js & Express", "RESTful API Integration", "Git & NPM"],
        "experience_levels": ["Beginner", "Intermediate", "Advanced"],
        "external_link": {
            "title": "JavaScript Internships on LinkedIn",
            "url": "https://www.linkedin.com/jobs/javascript-intern-jobs/",
            "disclaimer": "External job-search link. Vacancies and criteria are managed by respective employers on LinkedIn, not guaranteed by InternBot."
        },
        "description": "Dynamic web applications, responsive user interfaces, reactive state management, and asynchronous event-driven server runtime.",
        "roadmap": [
            {
                "step": 1,
                "title": "Modern JavaScript (ES6+) Foundations",
                "duration": "Weeks 1-2",
                "topics": ["let/const vs var, scope, hoisting, closures", "Arrow functions, template literals, destructuring", "Spread/rest operators, modules (import/export)", "Array methods: map, filter, reduce, find, some"],
                "skills": ["ES6+ Modern JavaScript"]
            },
            {
                "step": 2,
                "title": "DOM, Events & Browser APIs",
                "duration": "Weeks 3-4",
                "topics": ["DOM traversal & manipulation methods", "Event bubbling, capturing, and delegation", "Web Storage (`localStorage`, `sessionStorage`)", "Web Speech API, Notifications API, MediaDevices"],
                "skills": ["DOM Manipulation", "Event Handling"]
            },
            {
                "step": 3,
                "title": "Asynchronous Programming & Fetch",
                "duration": "Weeks 5-6",
                "topics": ["Event loop, call stack, microtask queue, macrotask queue", "Promises: `.then()`, `.catch()`, `.all()`, `.allSettled()`", "`async/await` syntax and defensive try/catch error boundaries", "Fetch API: headers, JSON payloads, abort controllers"],
                "skills": ["Promises & Async/Await", "RESTful API Integration"]
            },
            {
                "step": 4,
                "title": "React Component Architecture",
                "duration": "Weeks 7-9",
                "topics": ["JSX, component props, conditional rendering", "Hooks: `useState`, `useEffect`, `useRef`, `useCallback`", "State lifting, context API for global state", "Client-side routing with React Router"],
                "skills": ["React Fundamentals"]
            },
            {
                "step": 5,
                "title": "Node.js & Express Backend Basics",
                "duration": "Weeks 10-12",
                "topics": ["Node.js runtime, event loop, CommonJS vs ES Modules", "Express routing, middleware architecture, error handlers", "Connecting MongoDB/SQLite, CORS, environment variables", "Building and deploying to Vercel/Render"],
                "skills": ["Node.js & Express", "Git & NPM"]
            }
        ],
        "projects": [
            {
                "id": "js-proj-1",
                "title": "Interactive Weather & Climate App",
                "difficulty": "Beginner",
                "tech_stack": ["HTML5", "CSS3", "JavaScript (Vanilla)", "OpenWeather API"],
                "description": "Location-based real-time forecast with 5-day projections, dynamic animated weather graphics, and city search history.",
                "why": "Proves mastery of Fetch API, JSON parsing, asynchronous error handling, and dynamic DOM updating."
            },
            {
                "id": "js-proj-2",
                "title": "Productivity Task & Kanban Manager",
                "difficulty": "Intermediate",
                "tech_stack": ["JavaScript", "HTML5 Drag & Drop API", "LocalStorage", "CSS Grid"],
                "description": "Multi-column task board featuring drag-and-drop status changes, priority tagging, due dates, and offline storage persistence.",
                "why": "Demonstrates native browser Drag and Drop events, local state management, and accessible UI interaction patterns."
            },
            {
                "id": "js-proj-3",
                "title": "Interactive Analytics & Internship Dashboard",
                "difficulty": "Intermediate",
                "tech_stack": ["JavaScript/React", "Chart.js / Canvas", "REST API", "CSS Flexbox"],
                "description": "Real-time metric visualization showing application conversion rates, salary benchmarks, and category distributions.",
                "why": "Shows data visualization skills, component modularity, responsive CSS design, and structured state updates."
            }
        ],
        "mcqs": [
            {
                "id": "js-q1",
                "topic": "Event Loop",
                "question": "What is the execution order of `console.log('A')`, `setTimeout(() => console.log('B'), 0)`, and `Promise.resolve().then(() => console.log('C'))`?",
                "options": [
                    "A, B, C",
                    "A, C, B",
                    "C, A, B",
                    "B, A, C"
                ],
                "answer_index": 1,
                "explanation": "Synchronous code ('A') executes first. Microtasks (Promise callbacks -> 'C') run before macrotasks (timers like `setTimeout` -> 'B'). Thus the order is A, C, B."
            },
            {
                "id": "js-q2",
                "topic": "Closures",
                "question": "What is a closure in JavaScript?",
                "options": [
                    "A function bundled together with references to its surrounding lexical environment",
                    "A method that closes a database connection",
                    "A statement that terminates a loop early",
                    "A variable declared with `const`"
                ],
                "answer_index": 0,
                "explanation": "A closure gives an inner function access to its outer function's scope even after the outer function has returned."
            },
            {
                "id": "js-q3",
                "topic": "Equality Operators",
                "question": "What does `'5' == 5` and `'5' === 5` evaluate to?",
                "options": [
                    "true and true",
                    "false and false",
                    "true and false",
                    "false and true"
                ],
                "answer_index": 2,
                "explanation": "`==` performs type coercion before comparison ('5' becomes number 5 -> true). `===` requires strict equality with identical types (string vs number -> false)."
            }
        ],
        "interview_questions": [
            {
                "question": "Explain Event Delegation and why it is useful for performance.",
                "key_points": [
                    "Event delegation attaches a single event listener to a parent element instead of multiple listeners to child elements.",
                    "Relies on event bubbling: events trigger on target and propagate upward through ancestor nodes.",
                    "Benefits: Significant memory reduction, especially for dynamically generated elements (e.g. list items added via JavaScript)."
                ]
            },
            {
                "question": "What are the key rules of React Hooks?",
                "key_points": [
                    "Only call Hooks at the top level of React function components; never inside loops, conditions, or nested functions.",
                    "Only call Hooks from React function components or custom Hooks.",
                    "This guarantees Hooks are called in the exact same order on every render, preserving internal state indices."
                ]
            }
        ]
    },
    {
        "id": "fullstack",
        "title": "Full-Stack Development",
        "icon": "🌐",
        "badge": "Frontend + Backend + Cloud",
        "skills": ["HTML5/CSS3", "JavaScript (ES6+)", "React Frontend", "Node.js / Python Flask / Java Spring", "MySQL / MongoDB", "Authentication & JWT", "Git / GitHub", "Docker & Cloud Deployment"],
        "experience_levels": ["Beginner", "Intermediate", "Advanced"],
        "external_link": {
            "title": "Full-Stack Internships on LinkedIn",
            "url": "https://www.linkedin.com/jobs/full-stack-developer-intern-jobs/",
            "disclaimer": "External job-search link. Vacancies and criteria are managed by respective employers on LinkedIn, not guaranteed by InternBot."
        },
        "description": "End-to-end web engineering: responsive user experiences, scalable REST APIs, secure authentication, relational/NoSQL databases, and cloud deployments.",
        "roadmap": [
            {
                "step": 1,
                "title": "Responsive Web Foundations & UI Architecture",
                "duration": "Weeks 1-3",
                "topics": ["Semantic HTML5, CSS Grid, Flexbox, Custom Properties", "Modern mobile-first responsive design principles", "Interactive DOM manipulation with modern JavaScript", "Client-side form validation and accessible UX"],
                "skills": ["HTML5/CSS3", "JavaScript (ES6+)"]
            },
            {
                "step": 2,
                "title": "Dynamic Frontend Framework (React)",
                "duration": "Weeks 4-6",
                "topics": ["Component lifecycle, state management, custom hooks", "API consumption with Axios/Fetch and caching patterns", "Authentication contexts, protected routes, token storage", "Modern styling (CSS modules / TailwindCSS / Vanilla CSS tokens)"],
                "skills": ["React Frontend"]
            },
            {
                "step": 3,
                "title": "Backend Engineering & API Design",
                "duration": "Weeks 7-9",
                "topics": ["RESTful architectural constraints and HTTP verb semantics", "Server frameworks: Express.js, Flask, or Spring Boot", "Middleware chains: logging, CORS, rate limiting, error handling", "Secure password hashing (bcrypt) and JWT session tokens"],
                "skills": ["Node.js / Python Flask / Java Spring", "Authentication & JWT"]
            },
            {
                "step": 4,
                "title": "Database Modeling & Transactions",
                "duration": "Weeks 10-11",
                "topics": ["Relational schemas in PostgreSQL / MySQL", "Document schemas in MongoDB", "Indexes, ACID transactions, join optimization", "Safe database migrations without downtime or data loss"],
                "skills": ["MySQL / MongoDB"]
            },
            {
                "step": 5,
                "title": "CI/CD, Containerization & Production Cloud",
                "duration": "Weeks 12-14",
                "topics": ["Multi-stage Dockerfiles and container orchestration", "Environment configuration management and secret vaults", "Automated integration testing and GitHub Actions CI", "Deploying to Render, AWS EC2, or Vercel"],
                "skills": ["Git / GitHub", "Docker & Cloud Deployment"]
            }
        ],
        "projects": [
            {
                "id": "fs-proj-1",
                "title": "Campus Job & Internship Portal",
                "difficulty": "Advanced",
                "tech_stack": ["React / HTML5", "Node.js / Express or Flask", "PostgreSQL / SQLite", "JWT Auth", "Multer"],
                "description": "Comprehensive student portal with company vacancy listings, student resume submissions, application tracking, and recruiter dashboards.",
                "why": "Covers end-to-end full-stack workflows: multi-role authentication, file uploads, relational schema modeling, and status transition workflows."
            },
            {
                "id": "fs-proj-2",
                "title": "Internship Application & Opportunity Platform",
                "difficulty": "Advanced",
                "tech_stack": ["React", "Python Flask / Spring Boot", "MySQL", "REST API", "Docker"],
                "description": "Student platform aggregating verified internship opportunities, deadline reminders, resume review scores, and skill benchmark checklists.",
                "why": "Demonstrates complex data joins, scheduled notification logic, secure REST contracts, and Docker deployment."
            },
            {
                "id": "fs-proj-3",
                "title": "Hotel & Workspace Booking System",
                "difficulty": "Intermediate",
                "tech_stack": ["JavaScript", "Node.js / Express or Java", "MongoDB / MySQL", "Stripe API Mock", "CSS"],
                "description": "End-to-end reservation platform with inventory scheduling, real-time availability calendar, and automated booking confirmation emails.",
                "why": "Proves ability to manage concurrent reservations, calendar date-range collisions, transactional workflows, and external third-party integrations."
            }
        ],
        "mcqs": [
            {
                "id": "fs-q1",
                "topic": "Security & Auth",
                "question": "What is the primary vulnerability prevented by setting `HttpOnly` and `SameSite=Strict` on session cookies?",
                "options": [
                    "SQL Injection (SQLi)",
                    "Cross-Site Scripting (XSS) cookie theft and Cross-Site Request Forgery (CSRF)",
                    "Distributed Denial of Service (DDoS)",
                    "Man-in-the-Middle (MitM) attacks over plaintext HTTP"
                ],
                "answer_index": 1,
                "explanation": "`HttpOnly` prevents client-side JavaScript from reading cookies (mitigating XSS session hijacking). `SameSite=Strict` prevents the browser from sending cookies on cross-origin requests (mitigating CSRF)."
            },
            {
                "id": "fs-q2",
                "topic": "REST Architecture",
                "question": "Which HTTP method is idempotent according to REST specifications?",
                "options": [
                    "POST",
                    "PUT",
                    "PATCH (in general non-idempotent updates)",
                    "CONNECT"
                ],
                "answer_index": 1,
                "explanation": "PUT is idempotent: performing multiple identical PUT requests will leave the resource in the exact same state as a single request. POST is not idempotent."
            },
            {
                "id": "fs-q3",
                "topic": "Database Architecture",
                "question": "What does the 'I' in ACID database transactions stand for?",
                "options": [
                    "Integrity",
                    "Isolation",
                    "Indexing",
                    "Idempotency"
                ],
                "answer_index": 1,
                "explanation": "ACID stands for Atomicity, Consistency, Isolation, and Durability. Isolation ensures concurrent transactions execute without interfering with one another."
            }
        ],
        "interview_questions": [
            {
                "question": "What are CORS (Cross-Origin Resource Sharing) headers and why does the browser enforce them?",
                "key_points": [
                    "CORS is a browser security mechanism based on the Same-Origin Policy (protocol, domain, port).",
                    "It prevents malicious scripts on one origin from accessing sensitive data on another origin without explicit permission.",
                    "The server responds with headers like `Access-Control-Allow-Origin`, `Access-Control-Allow-Methods`, and `Access-Control-Allow-Headers`."
                ]
            },
            {
                "question": "Explain the difference between SQL (relational) and NoSQL (document) databases, and when to use each.",
                "key_points": [
                    "SQL (PostgreSQL, MySQL): Structured schema, ACID compliance, complex relational JOINs, ideal for financial, transactional, and linked entity models.",
                    "NoSQL (MongoDB): Flexible JSON schema, horizontal sharding, rapid prototyping, ideal for unstructured data, logs, or high-velocity document storage.",
                    "Choice depends on consistency requirements, schema stability, and relational query complexity."
                ]
            }
        ]
    }
]

def get_all_categories():
    """Return the structured 4 categories."""
    return CATEGORIES

def get_category_by_id(cat_id):
    """Find category by ID."""
    for c in CATEGORIES:
        if c["id"].lower() == cat_id.lower():
            return c
    return None

def get_recommendations_for_user(skills_list, career_goal):
    """
    Generate personalized project and roadmap recommendations based on user skills and goal.
    Provides transparent reasons for each recommendation.
    """
    skills_set = set(s.strip().lower() for s in skills_list if s.strip())
    goal_lower = (career_goal or "").lower()

    # Determine recommended category
    matched_cat = None
    if "java" in goal_lower:
        matched_cat = "java"
    elif "python" in goal_lower:
        matched_cat = "python"
    elif "javascript" in goal_lower or "frontend" in goal_lower or "react" in goal_lower:
        matched_cat = "javascript"
    elif "full" in goal_lower or "web" in goal_lower:
        matched_cat = "fullstack"
    else:
        # Check skill overlap
        java_overlap = len(skills_set.intersection({"java", "spring", "sql", "jdbc"}))
        py_overlap = len(skills_set.intersection({"python", "flask", "django", "pandas"}))
        js_overlap = len(skills_set.intersection({"javascript", "react", "html", "css", "node"}))
        if java_overlap >= max(py_overlap, js_overlap) and java_overlap > 0:
            matched_cat = "java"
        elif py_overlap >= max(java_overlap, js_overlap) and py_overlap > 0:
            matched_cat = "python"
        elif js_overlap > 0:
            matched_cat = "javascript"
        else:
            matched_cat = "fullstack"

    cat_data = get_category_by_id(matched_cat) or CATEGORIES[0]

    recs = []
    for proj in cat_data["projects"]:
        recs.append({
            "project_id": proj["id"],
            "title": proj["title"],
            "difficulty": proj["difficulty"],
            "tech_stack": proj["tech_stack"],
            "description": proj["description"],
            "category": cat_data["title"],
            "category_id": cat_data["id"],
            "transparent_reason": (
                f"Recommended for your interest in {cat_data['title']} and career path '{career_goal or 'Software Engineering'}'. "
                f"Building this project provides tangible evidence of {', '.join(proj['tech_stack'][:3])} on your resume."
            ),
            "why": proj["why"]
        })

    return {
        "category": cat_data["title"],
        "category_id": cat_data["id"],
        "external_link": cat_data["external_link"],
        "projects": recs
    }
