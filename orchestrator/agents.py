"""
Agentlar moduli — rasmda ko'rsatilgan 9 ta agent implementatsiyasi.

Har bir agent o'z vazifasini bajaradi va natijani orchestratorga qaytaradi.
"""
import time
import logging
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field

from .config import AgentType, TaskStatus, AGENT_CONFIGS
from .skills import (
    SKILL_REGISTRY, SkillResult,
    CodeAnalyzerSkill, ModelInspectorSkill, URLMapperSkill,
    SecurityScannerSkill, AuthReviewSkill,
    TestCoverageSkill, CodeQualitySkill,
    DeploymentCheckSkill, DocGeneratorSkill, I18nCheckSkill,
)
from .memory import MemoryStore

logger = logging.getLogger("orchestrator.agents")


# ═══════════════════════════════════════════════
#  VAZIFA (TASK) MODELI
# ═══════════════════════════════════════════════

@dataclass
class Task:
    """Agent uchun vazifa."""
    task_id: str
    description: str
    agent_type: AgentType
    status: TaskStatus = TaskStatus.PENDING
    priority: int = 3
    input_data: Dict[str, Any] = field(default_factory=dict)
    output_data: Optional[Dict[str, Any]] = None
    errors: List[str] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    completed_at: Optional[float] = None
    parent_task_id: Optional[str] = None
    depends_on: List[str] = field(default_factory=list)

    @property
    def duration(self) -> Optional[float]:
        if self.completed_at:
            return round(self.completed_at - self.created_at, 2)
        return None


# ═══════════════════════════════════════════════
#  BAZAVIY AGENT KLASSI
# ═══════════════════════════════════════════════

class BaseAgent:
    """Barcha agentlar uchun bazaviy klass."""

    agent_type: AgentType = None

    def __init__(self, memory: MemoryStore):
        self.memory = memory
        self.config = AGENT_CONFIGS.get(self.agent_type)
        self.name = self.config.name if self.config else "Unknown"
        self._skills: Dict[str, Any] = {}
        self._register_skills()

    def _register_skills(self):
        """Agent o'z skilllarini ro'yxatga oladi."""
        pass

    def execute(self, task: Task) -> Task:
        """Vazifani bajarish — asosiy metod."""
        logger.info(f"[{self.name}] Vazifa boshlandi: {task.task_id}")
        task.status = TaskStatus.IN_PROGRESS

        try:
            context = self.memory.get_agent_context(self.agent_type.value)
            result = self._process(task, context)

            task.output_data = result
            task.status = TaskStatus.COMPLETED
            task.completed_at = time.time()

            self.memory.store_task_result(
                task.task_id, self.agent_type.value, result, success=True
            )
            logger.info(f"[{self.name}] Vazifa tugadi: {task.task_id} ({task.duration}s)")

        except Exception as e:
            task.status = TaskStatus.FAILED
            task.errors.append(str(e))
            task.completed_at = time.time()
            self.memory.store_error(task.task_id, self.agent_type.value, str(e))
            logger.error(f"[{self.name}] Xatolik: {task.task_id} — {e}")

        return task

    def _process(self, task: Task, context: Dict) -> Dict[str, Any]:
        """Asosiy ish mantiqi — subklasslarda override qilinadi."""
        raise NotImplementedError

    def _run_skill(self, skill_name: str, **kwargs) -> SkillResult:
        """Skill ni ishga tushirish."""
        skill = SKILL_REGISTRY.get(skill_name)
        if not skill:
            return SkillResult(success=False, message=f"Skill topilmadi: {skill_name}")
        return skill.execute(**kwargs)


# ═══════════════════════════════════════════════
#  1. ORCHESTRATOR AGENT — Jarayonni boshqaradi
# ═══════════════════════════════════════════════

class OrchestratorAgent(BaseAgent):
    agent_type = AgentType.ORCHESTRATOR

    def _process(self, task: Task, context: Dict) -> Dict[str, Any]:
        """Boshqa agentlarni boshqarish va natijalarni birlashtirish."""
        sub_tasks = task.input_data.get("sub_tasks", [])
        results = {}

        for st in sub_tasks:
            agent_type = AgentType(st["agent_type"])
            agent = create_agent(agent_type, self.memory)
            sub_task = Task(
                task_id=f"{task.task_id}_sub_{st['agent_type']}",
                description=st.get("description", ""),
                agent_type=agent_type,
                input_data=st.get("input_data", {}),
                parent_task_id=task.task_id,
            )
            completed = agent.execute(sub_task)
            results[st["agent_type"]] = {
                "status": completed.status.value,
                "output": completed.output_data,
                "errors": completed.errors,
                "duration": completed.duration,
            }

        return {
            "sub_results": results,
            "total_tasks": len(sub_tasks),
            "successful": sum(1 for r in results.values() if r["status"] == "completed"),
            "failed": sum(1 for r in results.values() if r["status"] == "failed"),
        }


# ═══════════════════════════════════════════════
#  2. ARCHITECT AGENT — Arxitektura qarorlarini yozadi
# ═══════════════════════════════════════════════

class ArchitectAgent(BaseAgent):
    agent_type = AgentType.ARCHITECT

    def _process(self, task: Task, context: Dict) -> Dict[str, Any]:
        models = self._run_skill("model_inspector")
        urls = self._run_skill("url_mapper")

        return {
            "models_analysis": models.data,
            "url_structure": urls.data,
            "recommendations": self._generate_recommendations(models.data, urls.data),
        }

    def _generate_recommendations(self, models_data, url_data) -> List[str]:
        recs = []
        if models_data:
            for app, models in models_data.items():
                if isinstance(models, list):
                    for m in models:
                        if len(m.get("fields", [])) > 15:
                            recs.append(f"{app}.{m['name']} modelida juda ko'p field — bo'lishni o'ylab ko'ring")
        if url_data:
            all_names = []
            for info in url_data.values():
                all_names.extend(info.get("names", []))
            if len(all_names) != len(set(all_names)):
                recs.append("Duplikat URL nomlari bor — nomlarni unikal qiling")
        return recs


# ═══════════════════════════════════════════════
#  3. PLANNER AGENT — Reja tuzadi
# ═══════════════════════════════════════════════

class PlannerAgent(BaseAgent):
    agent_type = AgentType.PLANNER

    def _process(self, task: Task, context: Dict) -> Dict[str, Any]:
        description = task.description
        code_analysis = self._run_skill("code_analyzer")

        steps = self._create_plan(description, code_analysis.data)
        return {
            "plan": steps,
            "estimated_tasks": len(steps),
            "project_stats": code_analysis.data.get("stats", {}),
        }

    def _create_plan(self, description: str, code_data: Dict) -> List[Dict]:
        steps = [
            {"step": 1, "action": "Vazifani tahlil qilish", "agent": "architect", "status": "pending"},
            {"step": 2, "action": "Kodni yozish", "agent": "developer", "status": "pending"},
            {"step": 3, "action": "Xavfsizlik tekshiruvi", "agent": "security", "status": "pending"},
            {"step": 4, "action": "Sifat tekshiruvi", "agent": "qa", "status": "pending"},
            {"step": 5, "action": "Hujjatlashtirish", "agent": "tech_writer", "status": "pending"},
        ]
        return steps


# ═══════════════════════════════════════════════
#  4. DEVELOPER AGENT — Kodni yozadi
# ═══════════════════════════════════════════════

class DeveloperAgent(BaseAgent):
    agent_type = AgentType.DEVELOPER

    def _process(self, task: Task, context: Dict) -> Dict[str, Any]:
        code_analysis = self._run_skill("code_analyzer", app=task.input_data.get("app"))
        quality = self._run_skill("code_quality")

        return {
            "code_analysis": code_analysis.data,
            "quality_metrics": quality.data,
            "suggestions": self._suggest_improvements(quality.data),
        }

    def _suggest_improvements(self, quality_data: Dict) -> List[str]:
        suggestions = []
        for app, metrics in quality_data.items():
            if isinstance(metrics, dict):
                ratio = metrics.get("documentation_ratio", 0)
                if ratio < 0.5:
                    suggestions.append(f"{app}: Docstring qo'shing (hozir {int(ratio*100)}%)")
                for func in metrics.get("long_functions", []):
                    suggestions.append(f"{app}: {func['name']} funksiyasi juda uzun ({func['lines']} qator)")
        return suggestions


# ═══════════════════════════════════════════════
#  5. SECURITY REVIEWER AGENT — Xavfsizlikni tekshiradi
# ═══════════════════════════════════════════════

class SecurityReviewerAgent(BaseAgent):
    agent_type = AgentType.SECURITY_REVIEWER

    def _process(self, task: Task, context: Dict) -> Dict[str, Any]:
        security = self._run_skill("security_scanner")
        auth = self._run_skill("auth_reviewer")

        return {
            "security_scan": security.data,
            "auth_review": auth.data,
            "overall_score": self._calculate_score(security.data, auth.data),
        }

    def _calculate_score(self, security_data, auth_data) -> str:
        issues = security_data.get("total", 0)
        auth_issues = auth_data.get("total", 0)
        total = issues + auth_issues
        if total == 0:
            return "A+ (mukammal)"
        elif total <= 3:
            return "B (yaxshi)"
        elif total <= 7:
            return "C (o'rtacha)"
        return "D (yaxshilash kerak)"


# ═══════════════════════════════════════════════
#  6. QA REVIEWER AGENT — Testlarni tekshiradi
# ═══════════════════════════════════════════════

class QAReviewerAgent(BaseAgent):
    agent_type = AgentType.QA_REVIEWER

    def _process(self, task: Task, context: Dict) -> Dict[str, Any]:
        coverage = self._run_skill("test_coverage")
        quality = self._run_skill("code_quality")

        return {
            "test_coverage": coverage.data,
            "code_quality": quality.data,
            "recommendations": self._qa_recommendations(coverage.data),
        }

    def _qa_recommendations(self, coverage_data: Dict) -> List[str]:
        recs = []
        for app, info in coverage_data.get("apps", {}).items():
            if not info.get("has_tests"):
                recs.append(f"{app}: Test yozing! Hozir hech qanday test yo'q.")
            elif info.get("test_count", 0) < 5:
                recs.append(f"{app}: Test soni kam ({info['test_count']}) — ko'proq test qo'shing")
        return recs


# ═══════════════════════════════════════════════
#  7. SRE REVIEWER AGENT — Deploy tayyorligini tekshiradi
# ═══════════════════════════════════════════════

class SREReviewerAgent(BaseAgent):
    agent_type = AgentType.SRE_REVIEWER

    def _process(self, task: Task, context: Dict) -> Dict[str, Any]:
        deploy = self._run_skill("deployment_check")
        return {
            "deployment_readiness": deploy.data,
            "deploy_ready": deploy.success,
            "message": deploy.message,
        }


# ═══════════════════════════════════════════════
#  8. FIX DEVELOPER AGENT — Muammolarni tuzatadi
# ═══════════════════════════════════════════════

class FixDeveloperAgent(BaseAgent):
    agent_type = AgentType.FIX_DEVELOPER

    def _process(self, task: Task, context: Dict) -> Dict[str, Any]:
        previous_errors = context.get("previous_errors", [])
        security_scan = self._run_skill("security_scanner")

        return {
            "known_errors": previous_errors,
            "security_issues": security_scan.data,
            "fix_suggestions": self._suggest_fixes(security_scan.data),
        }

    def _suggest_fixes(self, security_data: Dict) -> List[Dict]:
        fixes = []
        for issue in security_data.get("issues", []):
            fixes.append({
                "file": issue["file"],
                "line": issue["line"],
                "issue": issue["issue"],
                "fix": self._get_fix_for(issue["issue"]),
            })
        return fixes

    def _get_fix_for(self, issue: str) -> str:
        fix_map = {
            "CSRF": "@csrf_protect decorator qo'shing",
            "XSS": "|escape filter ishlatish yoki mark_safe ni olib tashlang",
            "injection": "ORM query ishlatish, raw SQL dan saqlaning",
            "eval": "eval() o'rniga xavfsiz alternativa ishlatish",
            "Hardcoded": ".env faylga ko'chiring va os.getenv() ishlatish",
        }
        for key, fix in fix_map.items():
            if key.lower() in issue.lower():
                return fix
        return "Kodni ko'rib chiqing va best practice'ga moslashtiring"


# ═══════════════════════════════════════════════
#  9. TECH WRITER AGENT — Hujjatlarni yozadi
# ═══════════════════════════════════════════════

class TechWriterAgent(BaseAgent):
    agent_type = AgentType.TECH_WRITER

    def _process(self, task: Task, context: Dict) -> Dict[str, Any]:
        doc_type = task.input_data.get("doc_type", "overview")
        docs = self._run_skill("doc_generator", doc_type=doc_type)
        i18n = self._run_skill("i18n_check")

        return {
            "documentation": docs.data,
            "i18n_status": i18n.data,
        }


# ═══════════════════════════════════════════════
#  AGENT FACTORY
# ═══════════════════════════════════════════════

AGENT_CLASSES = {
    AgentType.ORCHESTRATOR: OrchestratorAgent,
    AgentType.ARCHITECT: ArchitectAgent,
    AgentType.PLANNER: PlannerAgent,
    AgentType.DEVELOPER: DeveloperAgent,
    AgentType.SECURITY_REVIEWER: SecurityReviewerAgent,
    AgentType.QA_REVIEWER: QAReviewerAgent,
    AgentType.SRE_REVIEWER: SREReviewerAgent,
    AgentType.FIX_DEVELOPER: FixDeveloperAgent,
    AgentType.TECH_WRITER: TechWriterAgent,
}


def create_agent(agent_type: AgentType, memory: MemoryStore) -> BaseAgent:
    """Agent yaratish — factory pattern."""
    cls = AGENT_CLASSES.get(agent_type)
    if not cls:
        raise ValueError(f"Noma'lum agent turi: {agent_type}")
    return cls(memory)
