from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import sqlite3
from pathlib import Path
import re
import os
import json
import time
import hashlib
import urllib.request
import urllib.error
from collections import OrderedDict, defaultdict, deque
from flask import send_from_directory, abort
def notify(*args, **kwargs):
    return None

# Load a local .env file (if present) without needing python-dotenv.
_env_file = Path(__file__).resolve().parent / ".env"
if _env_file.exists():
    for _line in _env_file.read_text(encoding="utf-8").splitlines():
        _line = _line.strip()
        if _line and not _line.startswith("#") and "=" in _line:
            _k, _v = _line.split("=", 1)
            os.environ.setdefault(_k.strip(), _v.strip().strip('"').strip("'"))
os.environ["GOOGLE_SCRIPT_URL"] = "https://script.google.com/macros/s/AKfycbxJZk-1oSM_yNzBaGAZFtwBbL43_7Drpm7JAr1chFecG0cazOrttNgp-U5cDUDUC0ngvg/exec"
os.environ["GOOGLE_SCRIPT_SECRET"] = "CHANGE_ME_TO_A_LONG_RANDOM_STRING"
app = Flask(__name__, static_folder=None)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "replace-this-with-a-long-random-secret-key")
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "instance" / "karka_ai.db"
DB_PATH.parent.mkdir(exist_ok=True)

# ---------------------------------------------------------------------------
# KARKA AI LOCATION
# MAPS_URL is the official Google Maps link for Karka AI (opens the exact pin).
# MAPS_EMBED_URL powers the inline map. Google does not allow short
# maps.app.goo.gl links inside an <iframe>, so the embed uses a place search.
# To pin the embed to the exact spot: open the location in Google Maps ->
# Share -> Embed a map -> copy the src="..." URL and put it in KARKA_MAPS_EMBED_URL.
# ---------------------------------------------------------------------------
MAPS_URL = os.getenv("KARKA_MAPS_URL", "https://maps.app.goo.gl/4P1jj6hAVpHMSwpWA?g_st=aw")
MAPS_EMBED_URL = os.getenv(
    "KARKA_MAPS_EMBED_URL",
    "https://maps.google.com/maps?q=Karka%20AI%2C%20Nagercoil%2C%20Tamil%20Nadu&z=15&output=embed",
)
PHONE_DISPLAY = "+91 9487530243"
PHONE_TEL = "+919487530243"

@app.context_processor
def inject_site_globals():
    return {
        "maps_url": MAPS_URL,
        "maps_embed_url": MAPS_EMBED_URL,
        "phone_display": PHONE_DISPLAY,
        "phone_tel": PHONE_TEL,
        "career_tracks": CAREER_TRACKS,
    }

COURSES = [
    {
        "slug": "mern-full-stack",
        "title": "MERN Fullstack Development",
        "track": "Full Stack Development",
        "video": "course-mern.mp4",
        "enrollments": "650+",
        "rating": "4.8",
        "ratings": "200",
        "duration": "6 Months",
        "level": "Beginner to Advanced",
        "lessons": "48 Lessons",
        "mode": ["Offline", "Online"],
        "tagline": "Build scalable full-stack web apps with MongoDB, Express, React and Node.js.",
        "overview": "Master MongoDB, Express.js, React, and Node.js. Build high-performance, dynamic web applications from scratch and launch a high-earning software engineering career with our 100% placement-supported bootcamp in Nagercoil.",
        "why_title": "High Market Demand",
        "why_lead": "The MERN stack is widely used across modern startups and product teams building fast, scalable web applications.",
        "why": [
            ("High Market Demand", "Build skills around a widely used modern JavaScript stack for startups and product teams."),
            ("Unified Language Power", "Use JavaScript across frontend and backend development so you can build complete applications efficiently."),
            ("Premium Tech Salaries", "End-to-end engineering skills can open doors to software roles and remote opportunities."),
            ("Rapid Career Growth", "A complete stack creates a foundation for advanced architecture, product engineering and technical leadership.")
        ],
        "curriculum": [
            ("Frontend Mastery", ["React Hooks & Context API", "State Management with Redux", "Responsive UI with Tailwind CSS"]),
            ("Backend Architecture", ["Node.js Runtime", "Express.js REST APIs", "Middleware & Routing", "Authentication with JWT"]),
            ("Database Design", ["MongoDB Schema Design", "Aggregation Framework", "Mongoose Modeling"]),
            ("Deployment & Scaling", ["Docker Basics", "CI/CD Pipelines", "AWS/Heroku Deployment"])
        ],
        "instructor": ("John Doe", "Sr. Fullstack Developer", "TechCorp", "8 Years Experience"),
        "testimonial": "Building a complete e-commerce platform from scratch and deploying it live gave me the confidence to face technical rounds. Karka's focus on actual projects rather than theory makes all the difference.",
        "admission": [("Application", "Submit your interest via our online form."), ("Counseling", "A brief session with our career advisors."), ("Enrollment", "Finalize your admission and start learning.")],
        "faqs": [
            ("What is the course duration and mode?", "The program is designed as a 6-month track with Offline and Online learning options."),
            ("What modules are covered in this curriculum?", "Frontend React development, backend APIs, MongoDB, authentication, deployment, Docker and CI/CD are covered."),
            ("Is prior coding experience required to join?", "The track starts from fundamentals and progresses to advanced topics, so motivated beginners can begin the journey."),
            ("What placement support do you provide after graduation?", "Career mentoring, resume and portfolio support, mock interviews and dedicated placement guidance are part of the program.")
        ]
    },
    {
        "slug": "ai-data-science",
        "title": "AI & Data Science",
        "track": "Data Science & Machine Learning",
        "video": "course-ai-data-science.mp4",
        "enrollments": "650+",
        "rating": "4.8",
        "ratings": "200",
        "duration": "6 Months",
        "level": "Intermediate",
        "lessons": "50 Lessons",
        "mode": ["Offline", "Online"],
        "tagline": "Turn data into predictive intelligence with statistics, ML and practical AI.",
        "overview": "Master Statistical Modeling, Machine Learning Algorithms, and Predictive AI Systems. Transform raw, unorganized corporate information into predictive intelligence engines with our 100% placement-supported bootcamp in Nagercoil.",
        "why_title": "The Blueprint of Enterprise",
        "why_lead": "Modern organizations use data to forecast outcomes, understand customers and make better decisions.",
        "why": [
            ("The Blueprint of Enterprise", "Learn how data supports forecasting, decision-making and competitive strategy."),
            ("Incredible Salary Growth", "Build specialized skills around data, machine learning and AI systems."),
            ("Versatile Industry Scope", "Apply data science concepts across banking, healthcare, retail, technology and more."),
            ("High Structural Security", "Develop durable technical skills as organizations become increasingly data-driven.")
        ],
        "curriculum": [
            ("Statistical Foundations", ["Probability Theory", "Inferential Statistics", "Hypothesis Testing"]),
            ("Machine Learning", ["Supervised Learning", "Unsupervised Learning", "Deep Learning Foundations"]),
            ("AI Engineering", ["Natural Language Processing", "Computer Vision", "LLM Fine-tuning"])
        ],
        "instructor": ("Dr. Sarah Lee", "AI Research Scientist", "DataMind", "15 Years Experience"),
        "testimonial": "Karka's focus on messy, real-world data prepares you for actual office environments. Building real predictive analytics models got me through tough corporate interviews with ease.",
        "admission": [("Application", "Apply online with your CV."), ("Tech Interview", "Assessment of math and coding basics."), ("Enrollment", "Secure your seat for the next batch.")],
        "faqs": [
            ("What tools are covered in this curriculum?", "The program focuses on statistical analysis, machine learning, deep learning, NLP, computer vision and modern AI workflows."),
            ("I don't have a strong math degree, can I join?", "The course is structured around practical learning, while gradually building the mathematical foundations needed for the models."),
            ("What is the course duration and learning options?", "The program runs for 6 months with Offline and Online options."),
            ("What placement support do you provide?", "Students receive career mentoring, resume and portfolio support, interview preparation and placement guidance.")
        ]
    },
    {
        "slug": "ui-ux-design",
        "title": "UI/UX Design",
        "track": "Design Courses",
        "video": "course-ui-ux.mp4",
        "enrollments": "450+",
        "rating": "4.8",
        "ratings": "200",
        "duration": "4 Months",
        "level": "Beginner",
        "lessons": "32 Lessons",
        "mode": ["Offline", "Online"],
        "tagline": "Design intuitive, beautiful digital experiences with industry-standard tools.",
        "overview": "Master User Research, Wireframing, and High-Fidelity Interface Prototyping. Learn user psychology and digital design to build beautiful, intuitive mobile applications and website layouts with our 100% placement-backed Nagercoil bootcamp.",
        "why_title": "The Core of Product Success",
        "why_lead": "A digital product succeeds when people can understand it, navigate it and enjoy using it.",
        "why": [
            ("The Core of Product Success", "Learn how usability and thoughtful interaction design influence digital product success."),
            ("No-Code Creative Tech Career", "Build a creative technology career without needing complex backend programming."),
            ("Exceptional Career Freedom", "Explore product design, startup consulting and freelance design opportunities."),
            ("High Financial Upside", "Strong product design skills can directly influence customer experience and business conversion.")
        ],
        "curriculum": [
            ("Design Thinking", ["Empathize & Define", "Ideation Techniques", "User Persona Mapping"]),
            ("UI Components", ["Visual Hierarchy", "Typography & Color Theory", "Auto-layout in Figma"]),
            ("UX Research", ["Usability Testing", "Information Architecture", "Wireframing Basics"])
        ],
        "instructor": ("Elena Rossi", "Sr. Product Designer", "Designflow", "7 Years Experience"),
        "testimonial": "Learning user research alongside interface design at Karka reshaped how I think. Creating a real product design case study helped me build an agency portfolio that got me hired immediately.",
        "admission": [("Application", "Submit your details and design interest."), ("Portfolio Review", "Meet with mentors to discuss your goals."), ("Enrollment", "Confirm your enrollment.")],
        "faqs": [
            ("What software tools will I master?", "You will work with industry-standard interface and prototyping workflows, including Figma-based design practices."),
            ("Do I need an art background?", "No. Curiosity, visual thinking and a willingness to practice are more important than a formal art background."),
            ("What is the course duration and mode of learning?", "The program runs for 4 months and offers Offline and Online learning."),
            ("Do you support freelance portfolio building?", "Yes. The program emphasizes case studies, portfolio-ready projects and practical presentation skills.")
        ]
    },
    {
        "slug": "python-for-kids",
        "title": "Python for Kids",
        "track": "Python for Kids",
        "video": "course-python-kids.mp4",
        "enrollments": "200+",
        "rating": "4.8",
        "ratings": "200",
        "duration": "3 Months",
        "level": "Beginner (Ages 10–15)",
        "lessons": "24 Lessons",
        "mode": ["Offline", "Online"],
        "tagline": "Make coding fun through Python games, animations and creative projects.",
        "overview": "Interactive introduction to programming logic using Python. Build games and animations while learning core coding concepts in a friendly, project-led environment.",
        "why_title": "Creative Coding Starts Early",
        "why_lead": "Young learners can build confidence in logic and problem-solving when programming is taught through things they can see, play and create.",
        "why": [
            ("Creative Coding", "Turn programming concepts into visual, hands-on experiences with games and animations."),
            ("Strong Logic Foundation", "Build a clear understanding of variables, conditions, loops and algorithms."),
            ("Project-Based Learning", "Learn by making small creations instead of memorizing syntax."),
            ("Confidence Through Making", "Give learners a supportive environment to experiment, debug and improve.")
        ],
        "curriculum": [
            ("Foundations of Logic", ["Algorithms & Flowcharts", "Variables & Data Types", "Input/Output Operations"]),
            ("Creative Coding", ["Turtle Graphics", "Coordinate Systems", "Loops & Patterns", "Event Handling"]),
            ("Game Development", ["Conditional Logic", "Nested Loops", "Basic Lists", "Project: Retro Snake Game"])
        ],
        "instructor": ("Michael Park", "STEM Instructor", "Kodable", "4 Years Experience"),
        "testimonial": "The support I received from Karka was phenomenal. They guided me at every step from learning to landing my first coding projects.",
        "admission": [("Registration", "Parents can register their children through the online portal."), ("Orientation", "A quick session for parents and students to understand the curriculum."), ("Enrollment", "Secure the spot and start the coding journey.")],
        "faqs": [
            ("What is the mode of training?", "The program offers Offline and Online learning options."),
            ("Do you offer placement support?", "This is a youth coding foundation program focused on skills, projects and confidence rather than placement."),
            ("Can I pay in installments?", "Enrollment and payment options can be discussed with the admissions team during counseling.")
        ]
    },
    {
        "slug": "advanced-mern",
        "title": "Full Stack Developer Internship",
        "track": "Advanced MERN & Production",
        "video": "course-full-stack.mp4",
        "enrollments": "800+",
        "rating": "4.8",
        "ratings": "200",
        "duration": "6 Months",
        "level": "Beginner to Advanced",
        "lessons": "60 Lessons",
        "mode": ["Offline", "Online"],
        "tagline": "Go beyond MERN with DevOps, system design and production engineering.",
        "overview": "Rigorous MERN stack training for students. Master DevOps, System Design, and Production best practices on large-scale apps through practical architecture and deployment work.",
        "why_title": "From Developer to Production Engineer",
        "why_lead": "Production software requires more than coding: architecture, deployment, reliability and scalable engineering practices matter.",
        "why": [
            ("Architecture Depth", "Understand MVC, microservices, scalability and system design principles."),
            ("Production Engineering", "Learn deployment, monitoring, logging, rate limiting and resilient application practices."),
            ("Industry Exposure", "Build experience around workflows that mirror professional engineering teams."),
            ("Career Acceleration", "Strengthen your portfolio with advanced full-stack and cloud-focused projects.")
        ],
        "curriculum": [
            ("Architecture & System Design", ["MVC vs Microservices", "Scalability Principles", "Load Balancing", "Database Indexing"]),
            ("Full-Stack Mastery", ["Advanced React Patterns", "Server-Side Rendering (Next.js)", "API Rate Limiting", "Websockets"]),
            ("Cloud & DevOps", ["Dockerization", "CI/CD Pipelines (GitHub Actions)", "AWS Deployment (S3/EC2)", "Monitoring & Logging"])
        ],
        "instructor": ("Alex Rivera", "Software Architect", "Amazon", "8 Years Experience"),
        "testimonial": "The support I received from Karka was phenomenal. They guided me at every step from learning to landing my first job.",
        "admission": [("Registration", "Open for current college students and recent graduates."), ("Aptitude Test", "Assessment of basic logical reasoning and problem-solving skills."), ("Enrollment", "Secure your internship and start your career path.")],
        "faqs": [
            ("What is the mode of training?", "The internship track offers Offline and Online learning options."),
            ("Do you offer placement support?", "Yes. Career mentoring, mock interviews, portfolio building and placement guidance are integrated into the journey."),
            ("Can I pay in installments?", "Payment and enrollment options can be discussed with the admissions team.")
        ]
    },
    {
        "slug": "generative-ai",
        "title": "Generative AI Foundations",
        "track": "Generative AI",
        "video": "course-generative-ai.mp4",
        "enrollments": "900+",
        "rating": "4.8",
        "ratings": "200",
        "duration": "3 Months",
        "level": "Beginner",
        "lessons": "24 Lessons",
        "mode": ["Offline", "Online"],
        "tagline": "Master GenAI basics, prompt engineering and practical AI workflows.",
        "overview": "Unlock the Absolute Basics of Prompt Engineering & AI Automation. Learn how to use, configure, and integrate cutting-edge generative AI models into everyday business, marketing, and design tasks at our Nagercoil academy.",
        "why_title": "Essential Modern Skill Set",
        "why_lead": "Generative AI is becoming a practical productivity layer across technical, business, marketing and creative work.",
        "why": [
            ("Essential Modern Skill Set", "Build practical knowledge of generative AI tools and workflows for modern work."),
            ("Exponential Productivity", "Learn structured prompting and AI-assisted workflows to speed up research, content and creative tasks."),
            ("Future-Ready Thinking", "Understand how AI changes workflows so you can adapt as tools evolve."),
            ("Accessible Technical Transition", "Explore advanced AI concepts without requiring a traditional software engineering background.")
        ],
        "curriculum": [
            ("Introduction to Gen AI", ["History of AI", "Transformers & LLMs", "Ethical AI Practices"]),
            ("Prompt Engineering", ["Zero-shot & Few-shot Prompting", "Chain of Thought", "Effective Context Setting"]),
            ("AI Tooling", ["ChatGPT Mastery", "Midjourney & Stable Diffusion", "Productivity AI Tools"])
        ],
        "instructor": ("Dr. Alan Turing Jr.", "AI Ethicist", "FutureLogic", "5 Years Experience"),
        "testimonial": "Learning prompt engineering systematically at Karka made my work incredibly fast. I can manage content and design projects at a pace that blew my current employers away.",
        "admission": [("Sign Up", "Quick registration on our platform."), ("Orientation", "Welcome session to understand AI tools."), ("Enrollment", "Confirm your seat and start learning.")],
        "faqs": [
            ("Who is this course designed for?", "It is designed for students, creators, professionals and curious learners who want a practical introduction to generative AI."),
            ("Is coding required for this program?", "No. Coding is not required for the foundation track, although technical learners can explore additional workflows."),
            ("How long is this program and what is the learning mode?", "The program runs for 3 months with Offline and Online options."),
            ("Will I get a certificate after completion?", "A certificate is included upon successful completion of the program.")
        ]
    },
]
TRACKS = [course["track"] for course in COURSES]
# Extra career categories shown on the homepage (they have no detail page yet but are valid enrollment choices).
EXTRA_TRACKS = ["Digital Media", "Content & Marketing", "Other Tech", "Non Tech"]
CAREER_TRACKS = list(dict.fromkeys(TRACKS + EXTRA_TRACKS))

# ---------------------------------------------------------------------------
# KARKA AI DOUBT ASSISTANT
# OpenRouter is called server-side so the API key never reaches the browser.
# The assistant also has a local knowledge/fallback layer and a small TTL cache
# so common questions do not consume an API request every time.
# ---------------------------------------------------------------------------
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "").strip()
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "openrouter/free").strip() or "openrouter/free"
OPENROUTER_FALLBACK_MODELS = [x.strip() for x in os.getenv("OPENROUTER_FALLBACK_MODELS", "").split(",") if x.strip()]
OPENROUTER_SITE_URL = os.getenv("OPENROUTER_SITE_URL", "https://karka.ai")
OPENROUTER_SITE_NAME = os.getenv("OPENROUTER_SITE_NAME", "Karka AI")
CHAT_CACHE_TTL = int(os.getenv("KARKA_CHAT_CACHE_TTL", "900"))
CHAT_MIN_INTERVAL = float(os.getenv("KARKA_CHAT_MIN_INTERVAL", "2.0"))
CHAT_RATE_WINDOW = 60
CHAT_RATE_MAX = int(os.getenv("KARKA_CHAT_RATE_MAX", "10"))
_CHAT_CACHE = OrderedDict()
_CHAT_RATE = defaultdict(deque)

KARKA_AI_KNOWLEDGE = {
    "identity": "Karka AI is a career-focused learning academy in Nagercoil, Tamil Nadu, India. It focuses on GenAI-infused education, practical projects, industry-oriented mentorship, internships and placement-focused career preparation.",
    "contact": "Karka AI HQ: Nagercoil, Tamil Nadu, India. Phone: +91 9487530243. Google Maps location: https://maps.app.goo.gl/4P1jj6hAVpHMSwpWA?g_st=aw",
    "pay_after_placement": "Karka AI presents a Pay After Placement model for applicable programs. Learners should review the exact eligibility, qualifying-job, salary and payment terms during counseling. Do not promise a job or guaranteed placement.",
    "placement": "Karka AI does not claim that every learner is guaranteed a job. Karka AI focuses on job readiness through projects, mentorship, portfolio building, interview preparation and placement support.",
    "internship": "Internship learning includes real-world style/client projects, project portfolio building, collaboration practice and an internship certificate where the program provides one.",
    "pillars": "The four job-ready pillars are Technical Mastery, Real-World Projects, Professional Skills, and Interview & Career Readiness.",
    "career_call": "Learners can book a free career call with mentors for course guidance and doubts. The website has a career-call form with name, email, preferred program, phone and message.",
    "faq": "Learners do not need a CSE/coding background for beginner-friendly pathways. Course duration varies by program. Practical project and internship-oriented experience is a core part of the learning journey.",
    "courses": [

    ]
}
KARKA_AI_KNOWLEDGE["courses"] = [
    {
        "title": c["title"], "track": c["track"], "duration": c["duration"],
        "level": c["level"], "mode": c["mode"], "tagline": c["tagline"],
        "overview": c["overview"],
        "curriculum": [" ".join([section, ", ".join(items)]) for section, items in c.get("curriculum", [])]
    }
    for c in COURSES
]

_WS_RE = re.compile(r"\s+")

def _chat_cache_key(message, language):
    normalized = _WS_RE.sub(" ", message.strip().lower())
    raw = f"{language.lower()}|{normalized}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()

def _cache_get(key):
    item = _CHAT_CACHE.get(key)
    if not item:
        return None
    if time.time() - item[0] > CHAT_CACHE_TTL:
        _CHAT_CACHE.pop(key, None)
        return None
    _CHAT_CACHE.move_to_end(key)
    return item[1]

def _cache_put(key, value):
    _CHAT_CACHE[key] = (time.time(), value)
    _CHAT_CACHE.move_to_end(key)
    while len(_CHAT_CACHE) > 300:
        _CHAT_CACHE.popitem(last=False)

def _rate_allowed(ip):
    now = time.time()
    q = _CHAT_RATE[ip]
    while q and now - q[0] > CHAT_RATE_WINDOW:
        q.popleft()
    if q and now - q[-1] < CHAT_MIN_INTERVAL:
        return False, max(1, int(CHAT_MIN_INTERVAL - (now - q[-1]) + 1))
    if len(q) >= CHAT_RATE_MAX:
        return False, max(5, int(CHAT_RATE_WINDOW - (now - q[0]) + 1))
    q.append(now)
    return True, 0

def _local_karka_answer(message, language):
    q = message.lower()
    key = ""
    if any(k in q for k in ["pay after", "pap", "placement fee", "பிளேஸ்மென்ட்"]): key = "pay"
    elif any(k in q for k in ["internship", "project", "certificate"]): key = "internship"
    elif any(k in q for k in ["coding", "cse", "background", "beginner", "arts", "science"]): key = "beginner"
    elif any(k in q for k in ["contact", "phone", "nagercoil", "address", "location"]): key = "contact"
    elif any(k in q for k in ["placement", "job guarantee", "guarantee job"]): key = "placement"
    elif any(k in q for k in ["course", "courses", "which should", "best course", "track", "கோர்ஸ்"]): key = "courses"
    if not key: return None

    names = ", ".join(c["title"] for c in COURSES[:8])
    answers = {
      "en-IN": {
        "pay": "Karka AI’s Pay After Placement model is available for applicable programs. You learn first and share the applicable fees only after a qualifying job, subject to the program’s eligibility, salary and payment terms. It is not a promise of a job; exact terms should be confirmed during counseling.",
        "internship": "Internship learning at Karka AI is practical: learners work on real-world style projects, build a portfolio, practice collaboration and can receive an internship certificate where included by the program.",
        "beginner": "You do not need a CSE background for beginner-friendly Karka AI pathways. The learning journey starts with foundations and moves step by step toward projects, practical skills and career readiness.",
        "contact": "Karka AI HQ is in Nagercoil, Tamil Nadu, India. The listed phone number is +91 9487530243. You can also book a free career call through the website. Find us on Google Maps: https://maps.app.goo.gl/4P1jj6hAVpHMSwpWA?g_st=aw",
        "placement": "Karka AI focuses strongly on job readiness, but it should not promise that every learner will get a job. Support includes practical projects, portfolio building, mentoring, interview preparation and placement guidance.",
        "courses": f"Karka AI has career pathways including {names}. Tell me your education level, interests and career goal, and I can recommend a suitable track. You can also use the Explore Courses page to search and compare programs."
      },
      "ta-IN": {
        "pay": "Karka AI-யின் Pay After Placement முறை சில திட்டங்களுக்கு பொருந்தும். தகுதியான வேலை கிடைத்த பிறகு, திட்டத்தின் தகுதி, சம்பளம் மற்றும் கட்டண விதிமுறைகளுக்கு உட்பட்டு பொருந்தும் கட்டணத்தை செலுத்தலாம். இது வேலை உத்தரவாதம் அல்ல; சரியான விதிமுறைகளை mentor-களிடம் உறுதி செய்யுங்கள்.",
        "internship": "Karka AI internship-ல் நடைமுறை project work, portfolio உருவாக்கம், team collaboration மற்றும் திட்டத்தில் இருந்தால் internship certificate போன்ற அனுபவங்கள் கிடைக்கும்.",
        "beginner": "Beginner-friendly Karka AI courses-க்கு CSE பின்னணி அவசியமில்லை. அடிப்படையிலிருந்து தொடங்கி project, practical skills மற்றும் career readiness வரை படிப்படியாக கற்றுக்கொள்ளலாம்.",
        "contact": "Karka AI தலைமையகம் Nagercoil, Tamil Nadu, India-வில் உள்ளது. தொலைபேசி: +91 9487530243. Website மூலம் free career call-ஐயும் book செய்யலாம். Google Maps: https://maps.app.goo.gl/4P1jj6hAVpHMSwpWA?g_st=aw",
        "placement": "Karka AI job readiness-க்கு முக்கியத்துவம் அளிக்கிறது; ஆனால் ஒவ்வொரு learner-க்கும் வேலை கிடைக்கும் என்று உத்தரவாதம் அளிக்காது. Projects, portfolio, mentoring, interview preparation மற்றும் placement guidance வழங்கப்படுகிறது.",
        "courses": f"Karka AI-ல் {names} போன்ற career pathways உள்ளன. உங்கள் கல்வி, ஆர்வம் மற்றும் career goal-ஐ சொல்லுங்கள்; உங்களுக்கு ஏற்ற track-ஐ பரிந்துரைக்கிறேன். Explore Courses பக்கத்தில் courses-ஐ தேடி ஒப்பிடலாம்."
      },
      "hi-IN": {
        "pay": "Karka AI का Pay After Placement मॉडल कुछ प्रोग्राम्स पर लागू होता है। योग्य नौकरी मिलने के बाद, प्रोग्राम की eligibility, salary और payment terms के अनुसार लागू फीस साझा की जाती है। यह नौकरी की गारंटी नहीं है; सही शर्तें mentor से confirm करें।",
        "internship": "Karka AI internship में practical projects, portfolio building, collaboration और जहाँ program में शामिल हो वहाँ internship certificate का अनुभव मिलता है।",
        "beginner": "Beginner-friendly Karka AI pathways के लिए CSE background जरूरी नहीं है। आप fundamentals से शुरू करके projects, practical skills और career readiness तक step-by-step सीख सकते हैं।",
        "contact": "Karka AI का मुख्यालय Nagercoil, Tamil Nadu, India में है। फोन: +91 9487530243. Website से free career call भी book कर सकते हैं। Google Maps: https://maps.app.goo.gl/4P1jj6hAVpHMSwpWA?g_st=aw",
        "placement": "Karka AI job readiness पर ध्यान देता है, लेकिन हर learner को job मिलने की guarantee नहीं देता। Projects, portfolio, mentoring, interview preparation और placement guidance दी जाती है।",
        "courses": f"Karka AI में {names} जैसे career pathways हैं। अपनी education, interests और career goal बताइए; मैं आपके लिए सही track सुझा सकता हूँ। Explore Courses page पर courses search और compare कर सकते हैं।"
      },
      "ml-IN": {
        "pay": "Karka AI-യുടെ Pay After Placement മോഡൽ ചില പ്രോഗ്രാമുകൾക്ക് ബാധകമാണ്. യോഗ്യതയുള്ള ജോലി ലഭിച്ചതിന് ശേഷം, പ്രോഗ്രാമിന്റെ eligibility, salary, payment terms എന്നിവയ്ക്ക് വിധേയമായി ബാധകമായ ഫീസ് നൽകാം. ഇത് job guarantee അല്ല; കൃത്യമായ നിബന്ധനകൾ mentor-നോട് സ്ഥിരീകരിക്കുക.",
        "internship": "Karka AI internship-ൽ practical projects, portfolio building, collaboration, കൂടാതെ program-ൽ ഉൾപ്പെടുത്തിയിട്ടുണ്ടെങ്കിൽ internship certificate എന്നിവ ലഭിക്കും.",
        "beginner": "Beginner-friendly Karka AI pathways-ക്ക് CSE background ആവശ്യമില്ല. Fundamentals മുതൽ projects, practical skills, career readiness വരെ ഘട്ടംഘട്ടമായി പഠിക്കാം.",
        "contact": "Karka AI-യുടെ ആസ്ഥാനം Nagercoil, Tamil Nadu, India-യിലാണ്. ഫോൺ: +91 9487530243. Website വഴി free career call book ചെയ്യാം. Google Maps: https://maps.app.goo.gl/4P1jj6hAVpHMSwpWA?g_st=aw",
        "placement": "Karka AI job readiness-ന് പ്രാധാന്യം നൽകുന്നു; എന്നാൽ എല്ലാവർക്കും ജോലി ലഭിക്കും എന്ന് guarantee ചെയ്യില്ല. Projects, portfolio, mentoring, interview preparation, placement guidance എന്നിവ ലഭിക്കും.",
        "courses": f"Karka AI-ൽ {names} പോലുള്ള career pathways ഉണ്ട്. നിങ്ങളുടെ education, interests, career goal പറയൂ; അനുയോജ്യമായ track ഞാൻ നിർദ്ദേശിക്കാം. Explore Courses page-ൽ courses search ചെയ്ത് compare ചെയ്യാം."
      },
      "te-IN": {
        "pay": "Karka AI యొక్క Pay After Placement మోడల్ కొన్ని ప్రోగ్రామ్‌లకు వర్తిస్తుంది. అర్హత కలిగిన ఉద్యోగం వచ్చిన తర్వాత, ప్రోగ్రామ్ eligibility, salary మరియు payment terms ప్రకారం వర్తించే ఫీజును చెల్లించవచ్చు. ఇది job guarantee కాదు; ఖచ్చితమైన నిబంధనలను mentor‌తో నిర్ధారించండి.",
        "internship": "Karka AI internship‌లో practical projects, portfolio building, collaboration మరియు program‌లో ఉంటే internship certificate వంటి అనుభవాలు లభిస్తాయి.",
        "beginner": "Beginner-friendly Karka AI pathways‌కు CSE background అవసరం లేదు. Fundamentals నుంచి projects, practical skills మరియు career readiness వరకు step-by-step నేర్చుకోవచ్చు.",
        "contact": "Karka AI HQ Nagercoil, Tamil Nadu, Indiaలో ఉంది. ఫోన్: +91 9487530243. Website ద్వారా free career call కూడా book చేయవచ్చు. Google Maps: https://maps.app.goo.gl/4P1jj6hAVpHMSwpWA?g_st=aw",
        "placement": "Karka AI job readiness‌పై దృష్టి పెడుతుంది, కానీ ప్రతి learner‌కు job వస్తుందని guarantee చేయదు. Projects, portfolio, mentoring, interview preparation మరియు placement guidance ఉంటాయి.",
        "courses": f"Karka AIలో {names} వంటి career pathways ఉన్నాయి. మీ education, interests మరియు career goal చెప్పండి; సరైన track‌ను సూచిస్తాను. Explore Courses pageలో courses‌ను search మరియు compare చేయవచ్చు."
      }
    }
    return answers.get(language, answers["en-IN"]).get(key)

def _build_system_prompt(language):
    course_lines = "\n".join([f"- {c['title']} | track: {c['track']} | duration: {c['duration']} | level: {c['level']} | mode: {', '.join(c['mode'])} | {c['tagline']} | overview: {c['overview']} | curriculum: {'; '.join(c['curriculum'])}" for c in KARKA_AI_KNOWLEDGE["courses"]])
    return f"""You are Karka AI, the official website doubt assistant for Karka AI in Nagercoil, Tamil Nadu.
Answer naturally, warmly and accurately. You are not a sales bot. Help learners choose courses, understand learning paths, projects, internships, placement support, Pay After Placement, career calls, registration and website navigation.
LANGUAGE: Reply in the user's selected language: {language}. If the user mixes languages, use the selected language unless they clearly request another language. Keep technical names such as React, Python, MERN and AI in their standard spelling.
IMPORTANT: Never invent fees, salary guarantees, mentor names, placement percentages, company partnerships, certificates, schedules or policies. If a detail is not in the knowledge below, say that the exact current detail should be confirmed with Karka mentors. Never claim that placement is guaranteed.
VOICE: Keep answers concise and useful for a spoken conversation: normally 2-6 short paragraphs or bullets.
KNOWLEDGE:
{KARKA_AI_KNOWLEDGE["identity"]}
{KARKA_AI_KNOWLEDGE["contact"]}
{KARKA_AI_KNOWLEDGE["pay_after_placement"]}
{KARKA_AI_KNOWLEDGE["placement"]}
{KARKA_AI_KNOWLEDGE["internship"]}
{KARKA_AI_KNOWLEDGE["pillars"]}
{KARKA_AI_KNOWLEDGE["career_call"]}
{KARKA_AI_KNOWLEDGE["faq"]}
COURSES:
{course_lines}
If the user asks for a course recommendation, ask at most one useful follow-up if needed; otherwise give a best-fit recommendation and explain why. For enrollment, direct the learner to the website's registration page rather than collecting sensitive details in chat."""

def _openrouter_answer(messages):
    if not OPENROUTER_API_KEY:
        return None, "OpenRouter API key is not configured on the server."
    models = [OPENROUTER_MODEL] + [m for m in OPENROUTER_FALLBACK_MODELS if m != OPENROUTER_MODEL]
    payload = {
        "models": models,
        "messages": messages,
        "temperature": 0.35,
        "max_tokens": 650,
        "stream": False,
    }
    req = urllib.request.Request(
        "https://openrouter.ai/api/v1/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": OPENROUTER_SITE_URL,
            "X-Title": OPENROUTER_SITE_NAME,
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=35) as response:
            data=json.loads(response.read().decode("utf-8"))
        answer=((data.get("choices") or [{}])[0].get("message") or {}).get("content", "").strip()
        return (answer or None), None
    except urllib.error.HTTPError as exc:
        try: detail=exc.read().decode("utf-8")[:500]
        except Exception: detail=""
        return None, f"OpenRouter HTTP {exc.code}: {detail}"
    except Exception as exc:
        return None, str(exc)
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS enrollments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                whatsapp TEXT NOT NULL,
                email TEXT NOT NULL,
                career_track TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS callback_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                whatsapp TEXT NOT NULL,
                course TEXT NOT NULL,
                preferred_time TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS career_call_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                email TEXT NOT NULL,
                program TEXT NOT NULL,
                phone TEXT NOT NULL,
                message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)


@app.route("/static/<path:filename>")
def static(filename):
    allowed = ("images/", "videos/", "style/", "js/", "audios/")
    if not filename.startswith(allowed):
        abort(404)
    # Cache media for a week and CSS/JS for an hour so repeat visits feel instant.
    max_age = 3600 if filename.startswith(("style/", "js/")) else 604800
    return send_from_directory(BASE_DIR, filename, max_age=max_age)

@app.route("/")
def home():
    return render_template(
        "index.html",
        courses=COURSES,
        career_call_success=request.args.get("career_call") == "success"
    )

@app.route("/career-call", methods=["POST"])
def career_call():
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    program = request.form.get("program", "").strip()
    phone = request.form.get("phone", "").strip()
    message = request.form.get("message", "").strip()

    if not name or len(name) > 100:
        flash("Please enter your name.", "error")
    elif not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
        flash("Please enter a valid email address.", "error")
    elif program not in CAREER_TRACKS:
        flash("Please choose a valid program.", "error")
    elif not re.fullmatch(r"[+0-9()\-\s]{7,20}", phone):
        flash("Please enter a valid phone number.", "error")
    elif len(message) > 1000:
        flash("Please keep your message under 1000 characters.", "error")
    else:
        with get_db() as conn:
            conn.execute(
                "INSERT INTO career_call_requests (full_name, email, program, phone, message) VALUES (?, ?, ?, ?, ?)",
                (name, email, program, phone, message)
            )
        notify("career_call", name=name, email=email, program=program, phone=phone, message=message)
        return redirect(url_for("home", career_call="success") + "#career-call")

    return redirect(url_for("home") + "#career-call")

@app.route("/courses")
def courses_page():
    return render_template("courses.html", courses=COURSES)

@app.route("/course/<slug>")
def course_detail(slug):
    course = next((item for item in COURSES if item["slug"] == slug), None)
    if course is None:
        abort(404)
    return render_template("course.html", course=course)

@app.route("/enroll", methods=["GET", "POST"])
def enroll():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        whatsapp = request.form.get("whatsapp", "").strip()
        email = request.form.get("email", "").strip()
        track = request.form.get("track", "").strip()

        if not name or len(name) > 100:
            flash("Please enter your name (up to 100 characters).", "error")
        elif not re.fullmatch(r"[+0-9()\-\s]{7,20}", whatsapp):
            flash("Please enter a valid WhatsApp number.", "error")
        elif not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
            flash("Please enter a valid email address.", "error")
        elif track not in CAREER_TRACKS:
            flash("Please select a career track.", "error")
        else:
            with get_db() as conn:
                conn.execute(
                    "INSERT INTO enrollments (full_name, whatsapp, email, career_track) VALUES (?, ?, ?, ?)",
                    (name, whatsapp, email, track)
                )
            notify("enrollment", name=name, whatsapp=whatsapp, email=email, track=track)
            # Post/Redirect/Get: refreshing the thank-you page can no longer submit the form twice.
            return redirect(url_for("enroll_success", name=name))
        # Validation failed: keep what the person typed so they do not have to start over.
        return render_template(
            "enroll.html", tracks=CAREER_TRACKS, selected_track=track,
            form={"name": name, "whatsapp": whatsapp, "email": email},
        ), 400
    selected_track = request.args.get("track", "").strip()
    return render_template("enroll.html", tracks=CAREER_TRACKS, selected_track=selected_track, form={})

@app.route("/enroll/success")
def enroll_success():
    name = request.args.get("name", "").strip()[:100] or "there"
    return render_template("success.html", name=name)

@app.route("/request-callback", methods=["POST"])
def request_callback():
    name = request.form.get("name", "").strip()
    whatsapp = request.form.get("whatsapp", "").strip()
    course_slug = request.form.get("course", "").strip()
    preferred_time = request.form.get("preferred_time", "").strip()
    course = next((item for item in COURSES if item["slug"] == course_slug), None)

    if not name or len(name) > 100:
        flash("Please enter your name.", "error")
    elif not re.fullmatch(r"[+0-9()\-\s]{7,20}", whatsapp):
        flash("Please enter a valid WhatsApp number.", "error")
    elif course is None:
        flash("Please choose a valid course.", "error")
    else:
        with get_db() as conn:
            conn.execute(
                "INSERT INTO callback_requests (full_name, whatsapp, course, preferred_time) VALUES (?, ?, ?, ?)",
                (name, whatsapp, course["title"], preferred_time)
            )
        notify("callback", name=name, whatsapp=whatsapp, course=course["title"], preferred_time=preferred_time)
        return redirect(url_for("course_detail", slug=course_slug, callback="success"))

    if course:
        return redirect(url_for("course_detail", slug=course_slug))
    return redirect(url_for("home"))

@app.route("/api/karka-chat", methods=["POST"])
def karka_chat():
    body=request.get_json(silent=True) or {}
    message=str(body.get("message", "")).strip()
    language=str(body.get("language", "en-IN")).strip() or "en-IN"
    if not message:
        return jsonify({"error":"Please enter a doubt first."}), 400
    if len(message) > 1200:
        return jsonify({"error":"Please keep your question under 1200 characters."}), 400
    allowed_languages={"en-IN","ta-IN","hi-IN","ml-IN","te-IN","kn-IN","mr-IN","bn-IN"}
    if language not in allowed_languages:
        language="en-IN"

    key=_chat_cache_key(message, language)
    cached=_cache_get(key)
    if cached:
        return jsonify({"answer":cached,"cached":True})

    allowed, wait=_rate_allowed(request.headers.get("X-Forwarded-For", request.remote_addr or "anonymous").split(",")[0].strip())
    if not allowed:
        return jsonify({"error":f"Please give Karka AI a moment. Try again in about {wait} seconds."}), 429

    local=_local_karka_answer(message, language)
    if local:
        _cache_put(key, local)
        return jsonify({"answer":local,"cached":True,"source":"karka-knowledge"})

    system=_build_system_prompt(language)
    messages=[{"role":"system","content":system},{"role":"user","content":message}]
    answer, error=_openrouter_answer(messages)
    if answer:
        _cache_put(key, answer)
        return jsonify({"answer":answer,"cached":False,"source":"openrouter"})

    fallback=(
        "I’m still here to help, but the live AI service is temporarily unavailable. "
        "You can ask me about Karka courses, internships, projects, placement support, Pay After Placement or enrollment, "
        "and I’ll use the Karka knowledge layer whenever possible. For a personalized recommendation, book a free career call with a mentor."
    )
    return jsonify({"answer":fallback,"cached":False,"source":"fallback","error_detail":error}), 200

@app.route("/health")
def health():
    return {"status": "ok"}

@app.route("/school_students")
def school_students():
    return render_template("student.html")

@app.route("/professionals")
def professionals():
    return render_template("professionals.html")

@app.route("/college_students")
def college_students():
    return render_template("college.html")
init_db()

if __name__ == "__main__":
    # Set FLASK_DEBUG=1 for local development. Leave it off in production.
    app.run(debug=os.getenv("FLASK_DEBUG", "0") == "1")
