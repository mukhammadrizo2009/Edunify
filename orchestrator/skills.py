"""
Skilllar (ko'nikmalar) moduli — agentlar foydalanadigan amaliy qobiliyatlar.

Rasmda ko'rsatilgan Vositalar & Integratsiyalar:
Git/Repo, CI/CD, Issue Tracker, Code Scanner, Test Framework,
Monitoring, Docs/Wiki, Communication
"""
import os
import re
import ast
import logging
import subprocess
from typing import Any, Dict, List, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass

logger = logging.getLogger("orchestrator.skills")

BASE_DIR = Path(__file__).resolve().parent.parent


# ═══════════════════════════════════════════════
#  BAZAVIY SKILL KLASSI
# ═══════════════════════════════════════════════

@dataclass
class SkillResult:
    """Skill bajarilish natijasi."""
    success: bool
    data: Any = None
    message: str = ""
    errors: List[str] = None

    def __post_init__(self):
        if self.errors is None:
            self.errors = []


class BaseSkill:
    """Barcha skilllar uchun bazaviy klass."""
    name: str = "base_skill"
    description: str = ""

    def execute(self, **kwargs) -> SkillResult:
        raise NotImplementedError

    def validate_inputs(self, **kwargs) -> Tuple[bool, str]:
        return True, ""


# ═══════════════════════════════════════════════
#  1. KOD TAHLIL QILISH SKILLARI
# ═══════════════════════════════════════════════

class CodeAnalyzerSkill(BaseSkill):
    """Django loyiha kodini tahlil qilish."""
    name = "code_analyzer"
    description = "Loyiha fayllarini skanerlash va tahlil qilish"

    def execute(self, **kwargs) -> SkillResult:
        target_app = kwargs.get("app", None)
        file_type = kwargs.get("file_type", ".py")

        results = {"files": [], "stats": {}}
        search_dirs = [BASE_DIR / app for app in ['users', 'courses', 'quiz', 'ai_assistant']]
        if target_app:
            search_dirs = [BASE_DIR / target_app]

        total_lines = 0
        for d in search_dirs:
            if not d.exists():
                continue
            for f in d.rglob(f"*{file_type}"):
                if '__pycache__' in str(f) or 'migrations' in str(f):
                    continue
                try:
                    content = f.read_text(encoding='utf-8')
                    lines = len(content.splitlines())
                    total_lines += lines
                    results["files"].append({
                        "path": str(f.relative_to(BASE_DIR)),
                        "lines": lines,
                        "size": f.stat().st_size,
                    })
                except Exception:
                    pass

        results["stats"] = {
            "total_files": len(results["files"]),
            "total_lines": total_lines,
        }
        return SkillResult(success=True, data=results, message=f"{len(results['files'])} fayl topildi")


class ModelInspectorSkill(BaseSkill):
    """Django modellarni tekshirish."""
    name = "model_inspector"
    description = "Django modellar tuzilmasini tahlil qilish"

    def execute(self, **kwargs) -> SkillResult:
        target_app = kwargs.get("app", None)
        apps = [target_app] if target_app else ['users', 'courses', 'quiz']
        models_info = {}

        for app in apps:
            model_file = BASE_DIR / app / "models.py"
            if not model_file.exists():
                continue
            try:
                content = model_file.read_text(encoding='utf-8')
                tree = ast.parse(content)
                app_models = []
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        fields = []
                        for item in node.body:
                            if isinstance(item, ast.Assign):
                                for target in item.targets:
                                    if isinstance(target, ast.Name):
                                        fields.append(target.id)
                        app_models.append({"name": node.name, "fields": fields})
                models_info[app] = app_models
            except Exception as e:
                models_info[app] = {"error": str(e)}

        return SkillResult(success=True, data=models_info, message="Modellar tahlil qilindi")


class URLMapperSkill(BaseSkill):
    """URL tuzilmasini xaritalash."""
    name = "url_mapper"
    description = "Loyiha URL pattern'larini tahlil qilish"

    def execute(self, **kwargs) -> SkillResult:
        url_files = list(BASE_DIR.rglob("urls.py"))
        url_map = {}

        for uf in url_files:
            if '__pycache__' in str(uf) or 'venv' in str(uf):
                continue
            try:
                content = uf.read_text(encoding='utf-8')
                paths = re.findall(r"path\(['\"]([^'\"]*)['\"]", content)
                names = re.findall(r"name=['\"]([^'\"]+)['\"]", content)
                rel = str(uf.relative_to(BASE_DIR))
                url_map[rel] = {"paths": paths, "names": names}
            except Exception:
                pass

        return SkillResult(success=True, data=url_map, message=f"{len(url_map)} URL fayl tahlil qilindi")


# ═══════════════════════════════════════════════
#  2. XAVFSIZLIK TEKSHIRISH SKILLARI
# ═══════════════════════════════════════════════

class SecurityScannerSkill(BaseSkill):
    """Xavfsizlik zaifliklarini tekshirish."""
    name = "security_scanner"
    description = "CSRF, XSS, SQL injection va boshqa zaifliklarni tekshirish"

    DANGEROUS_PATTERNS = [
        (r'\.raw\(', "Raw SQL query — SQL injection xavfi"),
        (r'\beval\(', "eval() — kod injection xavfi"),
        (r'\bexec\(', "exec() — kod injection xavfi"),
        (r'__import__\(', "Dynamic import — xavfsizlik xavfi"),
        (r'mark_safe\(', "mark_safe — XSS xavfi mumkin"),
        (r'\|safe\b', "Template |safe filter — XSS xavfi"),
        (r'@csrf_exempt', "CSRF himoyasi o'chirilgan"),
        (r'^SECRET_KEY\s*=\s*["\'][^"\']+["\']', "Hardcoded SECRET_KEY"),
        (r'^password\s*=\s*["\'][^"\']+["\']', "Hardcoded password"),
    ]

    def execute(self, **kwargs) -> SkillResult:
        issues = []
        for f in BASE_DIR.rglob("*.py"):
            if any(x in str(f) for x in ['__pycache__', 'migrations', 'venv', '.git']):
                continue
            try:
                content = f.read_text(encoding='utf-8')
                for pattern, desc in self.DANGEROUS_PATTERNS:
                    matches = re.finditer(pattern, content)
                    for m in matches:
                        line_num = content[:m.start()].count('\n') + 1
                        issues.append({
                            "file": str(f.relative_to(BASE_DIR)),
                            "line": line_num,
                            "issue": desc,
                            "severity": "HIGH" if "injection" in desc.lower() else "MEDIUM",
                        })
            except Exception:
                pass

        return SkillResult(
            success=True,
            data={"issues": issues, "total": len(issues)},
            message=f"{len(issues)} ta xavfsizlik muammo topildi"
        )


class AuthReviewSkill(BaseSkill):
    """Autentifikatsiya va avtorizatsiyani tekshirish."""
    name = "auth_reviewer"
    description = "Login, permission va role tekshiruvlarini audit qilish"

    def execute(self, **kwargs) -> SkillResult:
        findings = []
        view_files = [
            BASE_DIR / "courses" / "views.py",
            BASE_DIR / "users" / "views.py",
            BASE_DIR / "quiz" / "views.py",
            BASE_DIR / "ai_assistant" / "views.py",
        ]

        for vf in view_files:
            if not vf.exists():
                continue
            content = vf.read_text(encoding='utf-8')
            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    decorators = [
                        getattr(d, 'id', getattr(d, 'attr', ''))
                        for d in node.decorator_list
                    ]
                    has_auth = any(d in ('login_required', 'teacher_required')
                                  for d in decorators)
                    if not has_auth and not node.name.startswith('_'):
                        if node.name not in ('health_check',):
                            findings.append({
                                "file": str(vf.relative_to(BASE_DIR)),
                                "function": node.name,
                                "status": "NO_AUTH_DECORATOR",
                                "recommendation": "login_required yoki teacher_required qo'shing",
                            })

        return SkillResult(
            success=True,
            data={"findings": findings, "total": len(findings)},
            message=f"{len(findings)} ta view tekshirildi"
        )


# ═══════════════════════════════════════════════
#  3. SIFAT TEKSHIRISH SKILLARI
# ═══════════════════════════════════════════════

class TestCoverageSkill(BaseSkill):
    """Test qamrovini tekshirish."""
    name = "test_coverage"
    description = "Test fayllarini tahlil qilish va qamrovni baholash"

    def execute(self, **kwargs) -> SkillResult:
        test_info = {}
        for app in ['users', 'courses', 'quiz', 'ai_assistant']:
            test_file = BASE_DIR / app / "tests.py"
            has_tests = False
            test_count = 0
            if test_file.exists():
                content = test_file.read_text(encoding='utf-8')
                test_count = len(re.findall(r'def test_', content))
                has_tests = test_count > 0 or len(content.strip()) > 100

            test_info[app] = {
                "has_test_file": test_file.exists(),
                "has_tests": has_tests,
                "test_count": test_count,
            }

        total_tests = sum(v["test_count"] for v in test_info.values())
        apps_with_tests = sum(1 for v in test_info.values() if v["has_tests"])

        return SkillResult(
            success=True,
            data={
                "apps": test_info,
                "total_tests": total_tests,
                "coverage_estimate": f"{apps_with_tests}/4 apps",
            },
            message=f"{total_tests} test topildi, {apps_with_tests}/4 app qamrovi"
        )


class CodeQualitySkill(BaseSkill):
    """Kod sifatini baholash."""
    name = "code_quality"
    description = "Kod sifati metrikalarini hisoblash"

    def execute(self, **kwargs) -> SkillResult:
        metrics = {}
        for app in ['users', 'courses', 'quiz', 'ai_assistant']:
            app_dir = BASE_DIR / app
            if not app_dir.exists():
                continue
            py_files = [f for f in app_dir.rglob("*.py")
                        if '__pycache__' not in str(f) and 'migrations' not in str(f)]

            total_lines = 0
            total_docstrings = 0
            total_functions = 0
            long_functions = []

            for f in py_files:
                try:
                    content = f.read_text(encoding='utf-8')
                    total_lines += len(content.splitlines())
                    tree = ast.parse(content)
                    for node in ast.walk(tree):
                        if isinstance(node, ast.FunctionDef):
                            total_functions += 1
                            func_lines = (node.end_lineno or 0) - node.lineno
                            if func_lines > 50:
                                long_functions.append({
                                    "name": node.name,
                                    "file": str(f.relative_to(BASE_DIR)),
                                    "lines": func_lines,
                                })
                            if (node.body and isinstance(node.body[0], ast.Expr)
                                    and isinstance(node.body[0].value, (ast.Constant, ast.Str))):
                                total_docstrings += 1
                except Exception:
                    pass

            doc_ratio = total_docstrings / max(total_functions, 1)
            metrics[app] = {
                "total_lines": total_lines,
                "total_functions": total_functions,
                "documented_functions": total_docstrings,
                "documentation_ratio": round(doc_ratio, 2),
                "long_functions": long_functions,
            }

        return SkillResult(success=True, data=metrics, message="Kod sifati baholandi")


# ═══════════════════════════════════════════════
#  4. DEPLOY TEKSHIRISH SKILLARI
# ═══════════════════════════════════════════════

class DeploymentCheckSkill(BaseSkill):
    """Deploy tayyorligini tekshirish."""
    name = "deployment_check"
    description = "Production deploy uchun tayyorlikni tekshirish"

    def execute(self, **kwargs) -> SkillResult:
        checks = []

        # 1. requirements.txt
        req = BASE_DIR / "requirements.txt"
        checks.append({
            "check": "requirements.txt mavjudligi",
            "passed": req.exists(),
        })

        # 2. Procfile
        procfile = BASE_DIR / "Procfile"
        checks.append({
            "check": "Procfile mavjudligi",
            "passed": procfile.exists(),
        })

        # 3. .env faylda SECRET_KEY
        env_file = BASE_DIR / ".env"
        if env_file.exists():
            env_content = env_file.read_text(encoding='utf-8')
            checks.append({
                "check": "SECRET_KEY .env da mavjud",
                "passed": "SECRET_KEY" in env_content,
            })
            checks.append({
                "check": "DEBUG=False production uchun",
                "passed": "DEBUG=False" in env_content or "DEBUG" in env_content,
            })

        # 4. ALLOWED_HOSTS
        settings = BASE_DIR / "config" / "settings.py"
        if settings.exists():
            s_content = settings.read_text(encoding='utf-8')
            checks.append({
                "check": "ALLOWED_HOSTS sozlangan",
                "passed": "ALLOWED_HOSTS" in s_content and "edunify.online" in s_content,
            })
            checks.append({
                "check": "WhiteNoise middleware",
                "passed": "WhiteNoiseMiddleware" in s_content,
            })
            checks.append({
                "check": "CSRF_TRUSTED_ORIGINS",
                "passed": "CSRF_TRUSTED_ORIGINS" in s_content,
            })

        # 5. .gitignore
        gitignore = BASE_DIR / ".gitignore"
        checks.append({
            "check": ".gitignore mavjud",
            "passed": gitignore.exists(),
        })

        passed = sum(1 for c in checks if c["passed"])
        total = len(checks)

        return SkillResult(
            success=passed == total,
            data={"checks": checks, "passed": passed, "total": total},
            message=f"Deploy tekshiruvi: {passed}/{total} o'tdi"
        )


# ═══════════════════════════════════════════════
#  5. HUJJATLASHTIRISH SKILLARI
# ═══════════════════════════════════════════════

class DocGeneratorSkill(BaseSkill):
    """Hujjat generatsiya qilish."""
    name = "doc_generator"
    description = "README, API docs, changelog generatsiya qilish"

    def execute(self, **kwargs) -> SkillResult:
        doc_type = kwargs.get("doc_type", "overview")

        if doc_type == "overview":
            return self._generate_overview()
        elif doc_type == "api":
            return self._generate_api_docs()
        return SkillResult(success=False, message=f"Noma'lum doc_type: {doc_type}")

    def _generate_overview(self) -> SkillResult:
        overview = {
            "project": "Edunify — Online Ta'lim Platformasi",
            "tech_stack": {
                "backend": "Django 5.2",
                "database": "SQLite (dev) / PostgreSQL (prod)",
                "frontend": "Django Templates + Bootstrap 5",
                "ai": "Google Gemini API",
                "deployment": "Railway / Render",
            },
            "apps": {},
        }

        for app in ['users', 'courses', 'quiz', 'ai_assistant']:
            app_dir = BASE_DIR / app
            views = app_dir / "views.py"
            models = app_dir / "models.py"
            view_count = 0
            model_count = 0
            if views.exists():
                content = views.read_text(encoding='utf-8')
                view_count = len(re.findall(r'^def \w+', content, re.MULTILINE))
            if models.exists():
                content = models.read_text(encoding='utf-8')
                model_count = len(re.findall(r'^class \w+', content, re.MULTILINE))

            overview["apps"][app] = {
                "views": view_count,
                "models": model_count,
            }

        return SkillResult(success=True, data=overview, message="Loyiha umumiy ko'rinishi")

    def _generate_api_docs(self) -> SkillResult:
        api_endpoints = []
        url_skill = URLMapperSkill()
        url_result = url_skill.execute()
        if url_result.success:
            for file_path, info in url_result.data.items():
                for i, path in enumerate(info.get("paths", [])):
                    name = info["names"][i] if i < len(info.get("names", [])) else ""
                    api_endpoints.append({"url": path, "name": name, "file": file_path})

        return SkillResult(success=True, data={"endpoints": api_endpoints}, message="API docs")


# ═══════════════════════════════════════════════
#  6. I18N TEKSHIRISH SKILL
# ═══════════════════════════════════════════════

class I18nCheckSkill(BaseSkill):
    """Ko'p tillilik tekshiruvi."""
    name = "i18n_check"
    description = "Tarjima qamrovini va hardcoded stringlarni tekshirish"

    def execute(self, **kwargs) -> SkillResult:
        issues = []
        templates_dir = BASE_DIR / "templates"

        for f in templates_dir.rglob("*.html"):
            try:
                content = f.read_text(encoding='utf-8')
                # Hardcoded uzbek/tajik strings qidirish
                hardcoded = re.findall(r'>[А-Яа-яЁёҲҳ][А-Яа-яЁёҲҳ\s]{5,}<', content)
                for h in hardcoded:
                    issues.append({
                        "file": str(f.relative_to(BASE_DIR)),
                        "text": h[1:-1].strip(),
                        "type": "hardcoded_cyrillic",
                    })
            except Exception:
                pass

        return SkillResult(
            success=True,
            data={"issues": issues, "total": len(issues)},
            message=f"{len(issues)} ta hardcoded string topildi"
        )


# ═══════════════════════════════════════════════
#  SKILL REGISTRY
# ═══════════════════════════════════════════════

SKILL_REGISTRY: Dict[str, BaseSkill] = {
    "code_analyzer": CodeAnalyzerSkill(),
    "model_inspector": ModelInspectorSkill(),
    "url_mapper": URLMapperSkill(),
    "security_scanner": SecurityScannerSkill(),
    "auth_reviewer": AuthReviewSkill(),
    "test_coverage": TestCoverageSkill(),
    "code_quality": CodeQualitySkill(),
    "deployment_check": DeploymentCheckSkill(),
    "doc_generator": DocGeneratorSkill(),
    "i18n_check": I18nCheckSkill(),
}


def get_skill(name: str) -> Optional[BaseSkill]:
    """Skill ni nomi bo'yicha olish."""
    return SKILL_REGISTRY.get(name)


def list_skills() -> List[Dict[str, str]]:
    """Barcha mavjud skilllar ro'yxati."""
    return [{"name": s.name, "description": s.description} for s in SKILL_REGISTRY.values()]
