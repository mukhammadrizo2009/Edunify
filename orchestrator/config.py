"""
Orchestrator konfiguratsiyasi — barcha sozlamalar va konstantalar.

Rasmda ko'rsatilgan:
├── Qoidalar & Siyosatlar (Ruxsatlar, Maxfiylik, Xavfsizlik, Compliance)
└── Kuzatuv & Kuzatiluvchanlik (Loglar, Metrikalar, Tracing, Ogohlantirishlar)
"""
import os
import logging
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional


# ═══════════════════════════════════════════════
#  AGENT TURLARI
# ═══════════════════════════════════════════════

class AgentType(Enum):
    """Rasmda ko'rsatilgan 9 ta agent turi."""
    ORCHESTRATOR = "orchestrator"        # Jarayonni boshqaradi
    ARCHITECT = "architect"              # Arxitektura qarorlarini yozadi
    PLANNER = "planner"                  # Reja tuzadi
    DEVELOPER = "developer"              # Kodni yozadi
    SECURITY_REVIEWER = "security"       # Xavfsizlikni tekshiradi
    QA_REVIEWER = "qa"                   # Testlarni tekshiradi
    SRE_REVIEWER = "sre"                 # Deploy tayyorligini tekshiradi
    FIX_DEVELOPER = "fix_developer"      # Muammolarni tuzatadi
    TECH_WRITER = "tech_writer"          # Hujjatlarni yozadi


class TaskStatus(Enum):
    """Vazifa holatlari."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"


class TaskPriority(Enum):
    """Vazifa ustuvorligi."""
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4


class IntentType(Enum):
    """Rasmda ko'rsatilgan So'rovni qabul qilish — NLP / Intent aniqlash."""
    CREATE_COURSE = "create_course"
    CREATE_QUIZ = "create_quiz"
    FIX_BUG = "fix_bug"
    ADD_FEATURE = "add_feature"
    REVIEW_CODE = "review_code"
    REVIEW_SECURITY = "review_security"
    DEPLOY = "deploy"
    WRITE_DOCS = "write_docs"
    REFACTOR = "refactor"
    OPTIMIZE = "optimize"
    TRANSLATE = "translate"
    UNKNOWN = "unknown"


# ═══════════════════════════════════════════════
#  QOIDALAR & SIYOSATLAR
# ═══════════════════════════════════════════════

@dataclass
class PolicyConfig:
    """
    Rasmda ko'rsatilgan: Qoidalar & Siyosatlar
    - Ruxsatlar
    - Maxfiylik
    - Xavfsizlik
    - Compliance
    """
    # Ruxsatlar
    allowed_roles: List[str] = field(default_factory=lambda: ['admin', 'teacher'])
    max_concurrent_tasks: int = 5
    rate_limit_per_minute: int = 30

    # Maxfiylik
    sensitive_fields: List[str] = field(default_factory=lambda: [
        'password', 'secret_key', 'api_key', 'token',
        'GEMINI_API_KEY', 'GOOGLE_OAUTH2_SECRET',
        'CLOUDINARY_API_SECRET', 'DATABASE_URL',
    ])
    mask_sensitive_data: bool = True

    # Xavfsizlik
    max_file_size_mb: int = 10
    allowed_file_extensions: List[str] = field(default_factory=lambda: [
        '.py', '.html', '.css', '.js', '.json', '.md', '.txt', '.yml', '.yaml'
    ])
    forbidden_operations: List[str] = field(default_factory=lambda: [
        'DROP DATABASE', 'DELETE FROM', 'rm -rf', 'os.system',
        'eval(', 'exec(', '__import__',
    ])

    # Compliance
    require_tests: bool = True
    require_review: bool = True
    require_documentation: bool = True
    min_code_coverage: float = 0.7  # 70%


# ═══════════════════════════════════════════════
#  AGENT KONFIGURATSIYASI
# ═══════════════════════════════════════════════

@dataclass
class AgentConfig:
    """Har bir agent uchun sozlamalar."""
    agent_type: AgentType
    name: str
    description: str
    skills: List[str]
    max_retries: int = 3
    timeout_seconds: int = 300
    requires_approval: bool = False
    allowed_tools: List[str] = field(default_factory=list)


# Barcha agentlar konfiguratsiyasi
AGENT_CONFIGS: Dict[AgentType, AgentConfig] = {

    AgentType.ORCHESTRATOR: AgentConfig(
        agent_type=AgentType.ORCHESTRATOR,
        name="Orchestrator Agent",
        description="Jarayonni boshqaradi — vazifalarni taqsimlaydi va natijalarni birlashtiradi",
        skills=[
            "task_analysis", "agent_selection", "coordination",
            "result_merging", "error_handling", "replanning",
        ],
        allowed_tools=["task_manager", "agent_registry", "memory_store"],
    ),

    AgentType.ARCHITECT: AgentConfig(
        agent_type=AgentType.ARCHITECT,
        name="Architect Agent",
        description="Arxitektura qarorlarini qabul qiladi — modellar, view'lar, URL tuzilmasi",
        skills=[
            "model_design", "url_design", "view_design",
            "database_schema", "api_design", "template_structure",
        ],
        allowed_tools=["code_analyzer", "model_inspector", "url_mapper"],
    ),

    AgentType.PLANNER: AgentConfig(
        agent_type=AgentType.PLANNER,
        name="Planner Agent",
        description="Reja tuzadi — vazifalarni bosqichlarga bo'ladi va ketma-ketlikni belgilaydi",
        skills=[
            "task_decomposition", "dependency_analysis", "estimation",
            "resource_allocation", "risk_assessment", "milestone_planning",
        ],
        allowed_tools=["task_manager", "dependency_graph"],
    ),

    AgentType.DEVELOPER: AgentConfig(
        agent_type=AgentType.DEVELOPER,
        name="Developer Agent",
        description="Kodni yozadi — Django modellar, view'lar, templatelar, CSS/JS",
        skills=[
            "django_models", "django_views", "django_templates",
            "django_forms", "django_urls", "css_styling",
            "javascript", "api_integration", "database_queries",
        ],
        allowed_tools=["code_writer", "file_manager", "code_formatter"],
    ),

    AgentType.SECURITY_REVIEWER: AgentConfig(
        agent_type=AgentType.SECURITY_REVIEWER,
        name="Security Reviewer Agent",
        description="Xavfsizlikni tekshiradi — CSRF, XSS, SQL injection, autentifikatsiya",
        skills=[
            "csrf_check", "xss_check", "sql_injection_check",
            "auth_review", "permission_check", "input_validation",
            "secret_detection", "dependency_audit",
        ],
        allowed_tools=["code_scanner", "vulnerability_db"],
    ),

    AgentType.QA_REVIEWER: AgentConfig(
        agent_type=AgentType.QA_REVIEWER,
        name="QA Reviewer Agent",
        description="Testlarni tekshiradi — unit test, integration test, edge case",
        skills=[
            "unit_test_review", "integration_test_review",
            "edge_case_detection", "test_coverage_analysis",
            "regression_check", "ui_test_review",
        ],
        allowed_tools=["test_runner", "coverage_tool"],
    ),

    AgentType.SRE_REVIEWER: AgentConfig(
        agent_type=AgentType.SRE_REVIEWER,
        name="SRE Reviewer Agent",
        description="Deploy tayyorligini tekshiradi — performance, scaling, monitoring",
        skills=[
            "deployment_check", "performance_review",
            "scaling_analysis", "monitoring_check",
            "configuration_validation", "health_check",
        ],
        allowed_tools=["deployment_validator", "performance_profiler"],
    ),

    AgentType.FIX_DEVELOPER: AgentConfig(
        agent_type=AgentType.FIX_DEVELOPER,
        name="Fix Developer Agent",
        description="Muammolarni tuzatadi — bugfix, error handling, regression fix",
        skills=[
            "bug_diagnosis", "error_tracing", "fix_implementation",
            "regression_prevention", "hot_fix", "rollback_plan",
        ],
        allowed_tools=["debugger", "log_analyzer", "code_writer"],
    ),

    AgentType.TECH_WRITER: AgentConfig(
        agent_type=AgentType.TECH_WRITER,
        name="Tech Writer Agent",
        description="Hujjatlarni yozadi — README, API docs, user guide, changelog",
        skills=[
            "readme_writing", "api_documentation", "user_guide",
            "changelog", "inline_comments", "architecture_docs",
        ],
        allowed_tools=["doc_generator", "markdown_formatter"],
    ),
}


# ═══════════════════════════════════════════════
#  INTENT → AGENT MAPPING
# ═══════════════════════════════════════════════

INTENT_AGENT_MAP: Dict[IntentType, List[AgentType]] = {
    IntentType.CREATE_COURSE: [
        AgentType.PLANNER, AgentType.ARCHITECT, AgentType.DEVELOPER,
        AgentType.QA_REVIEWER, AgentType.TECH_WRITER,
    ],
    IntentType.CREATE_QUIZ: [
        AgentType.PLANNER, AgentType.DEVELOPER, AgentType.QA_REVIEWER,
    ],
    IntentType.FIX_BUG: [
        AgentType.FIX_DEVELOPER, AgentType.QA_REVIEWER,
        AgentType.SECURITY_REVIEWER,
    ],
    IntentType.ADD_FEATURE: [
        AgentType.PLANNER, AgentType.ARCHITECT, AgentType.DEVELOPER,
        AgentType.SECURITY_REVIEWER, AgentType.QA_REVIEWER, AgentType.TECH_WRITER,
    ],
    IntentType.REVIEW_CODE: [
        AgentType.QA_REVIEWER, AgentType.SECURITY_REVIEWER,
    ],
    IntentType.REVIEW_SECURITY: [
        AgentType.SECURITY_REVIEWER, AgentType.SRE_REVIEWER,
    ],
    IntentType.DEPLOY: [
        AgentType.SRE_REVIEWER, AgentType.SECURITY_REVIEWER,
        AgentType.QA_REVIEWER,
    ],
    IntentType.WRITE_DOCS: [
        AgentType.TECH_WRITER,
    ],
    IntentType.REFACTOR: [
        AgentType.ARCHITECT, AgentType.DEVELOPER,
        AgentType.QA_REVIEWER, AgentType.SECURITY_REVIEWER,
    ],
    IntentType.OPTIMIZE: [
        AgentType.SRE_REVIEWER, AgentType.DEVELOPER,
    ],
    IntentType.TRANSLATE: [
        AgentType.DEVELOPER, AgentType.QA_REVIEWER,
    ],
}


# ═══════════════════════════════════════════════
#  KUZATUV KONFIGURATSIYASI
# ═══════════════════════════════════════════════

@dataclass
class ObservabilityConfig:
    """
    Rasmda ko'rsatilgan: Kuzatuv & Kuzatiluvchanlik
    - Loglar
    - Metrikalar
    - Tracing
    - Ogohlantirishlar
    """
    log_level: str = "INFO"
    log_format: str = "[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s"
    enable_tracing: bool = True
    enable_metrics: bool = True
    alert_on_failure: bool = True
    max_log_retention_days: int = 30
    metrics_export_interval: int = 60  # soniyada


# ═══════════════════════════════════════════════
#  EDUNIFY LOYIHA KONTEKSTI
# ═══════════════════════════════════════════════

@dataclass
class ProjectContext:
    """
    Rasmda ko'rsatilgan: Xotira & Kontekst
    - Loyiha konteksti
    - Qoidalar
    - Andozalar
    """
    project_name: str = "Edunify"
    framework: str = "Django 5.2"
    python_version: str = "3.12"
    database: str = "SQLite (dev) / PostgreSQL (prod)"
    frontend: str = "Django Templates + Bootstrap 5 + JavaScript"
    ai_provider: str = "Google Gemini API"
    languages: List[str] = field(default_factory=lambda: ['en', 'ru', 'tj', 'uz'])
    apps: List[str] = field(default_factory=lambda: [
        'users', 'courses', 'quiz', 'ai_assistant',
    ])
    deployment: str = "Railway (PostgreSQL) / Render (backup)"
    domain: str = "edunify.online"

    # Django modellar
    models: Dict[str, List[str]] = field(default_factory=lambda: {
        'users': ['CustomUser'],
        'courses': ['Category', 'Course', 'Lesson', 'Enrollment'],
        'quiz': ['Quiz', 'Question', 'Result'],
    })

    # URL patterns
    url_namespaces: Dict[str, str] = field(default_factory=lambda: {
        '': 'courses.urls',
        'users/': 'users.urls',
        'quiz/': 'quiz.urls',
        'ai/': 'ai_assistant.urls',
        'auth/': 'social_django.urls',
    })

    # Andozalar (patterns)
    patterns: Dict[str, str] = field(default_factory=lambda: {
        'auth': 'Session-based + Google OAuth2',
        'roles': 'student, teacher, admin',
        'i18n': 'Session-based language switching (en, ru, tj)',
        'forms': 'Django Forms + Crispy Bootstrap5',
        'media': 'Cloudinary (prod) / Local (dev)',
        'static': 'WhiteNoise + collectstatic',
        'admin': 'Django Unfold',
        'ai': 'Google Gemini via google-genai client',
    })


# Global instances
POLICY = PolicyConfig()
OBSERVABILITY = ObservabilityConfig()
PROJECT_CONTEXT = ProjectContext()
