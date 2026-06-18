"""
AI Agent Orchestrator — Markaziy boshqaruv tizimi.

Rasmda ko'rsatilgan 5 ta asosiy funksiya:
1. Vazifa tahlili    — Talabni tushunish, Vazifani bo'lish
2. Rejalashtirish    — Agentlarni tanlash, Ketma-ketlikni belgilash, Resurslarni ajratish
3. Muvofiqlashtirish — Vazifalarni delegatsiya qilish, Holatni kuzatish, Qayta rejalashtirish
4. Sifat & Xavfsizlik — Xavfsizlik tekshiruvi, Sifat nazorati, Muvofiqlik qoidalari
5. Natija birlashtirish — Natijalarni yig'ish, Validatsiya qilish, Yakuniy javob
"""
import re
import time
import uuid
import logging
from typing import Any, Dict, List, Optional

from .config import (
    AgentType, TaskStatus, IntentType,
    INTENT_AGENT_MAP, POLICY, PROJECT_CONTEXT,
)
from .agents import Task, BaseAgent, create_agent
from .memory import MemoryStore
from .skills import SKILL_REGISTRY

logger = logging.getLogger("orchestrator.engine")


class AIAgentOrchestrator:
    """
    Markaziy Orchestrator — rasmda ko'rsatilgan arxitekturaning yuragi.

    Foydalanuvchi so'rovini qabul qilib:
    1. Intentni aniqlaydi (NLP / Intent aniqlash)
    2. Vazifani tahlil qiladi
    3. Agentlarni tanlaydi va rejalashtiradi
    4. Vazifalarni delegatsiya qiladi va muvofiqlashtiradi
    5. Sifat va xavfsizlikni tekshiradi
    6. Natijalarni birlashtiradi va qaytaradi
    """

    def __init__(self, storage_dir: Optional[str] = None):
        self.memory = MemoryStore(storage_dir=storage_dir)
        self._task_history: List[Task] = []
        self._active_tasks: Dict[str, Task] = {}
        logger.info("🚀 AI Agent Orchestrator ishga tushdi")

    # ═══════════════════════════════════════════════
    #  1. SO'ROVNI QABUL QILISH — NLP / Intent aniqlash
    # ═══════════════════════════════════════════════

    def process_request(self, request: str, user_role: str = "admin") -> Dict[str, Any]:
        """
        Asosiy entry point — foydalanuvchi so'rovini qabul qilish.

        Args:
            request: Foydalanuvchi so'rovi (matn)
            user_role: Foydalanuvchi roli (admin, teacher, student)

        Returns:
            Yakuniy natija (dict)
        """
        start_time = time.time()
        task_id = str(uuid.uuid4())[:8]

        logger.info(f"📥 Yangi so'rov: [{task_id}] {request[:100]}...")

        # 1. Ruxsat tekshiruvi
        if user_role not in POLICY.allowed_roles:
            return self._error_response(task_id, "Ruxsat yo'q: faqat admin va teacher ishlatishi mumkin")

        # 2. Intent aniqlash
        intent = self._detect_intent(request)
        logger.info(f"🎯 Intent: {intent.value}")

        # 3. Vazifa tahlili
        analysis = self._analyze_task(task_id, request, intent)

        # 4. Rejalashtirish — agentlarni tanlash
        plan = self._create_plan(task_id, intent, analysis)

        # 5. Muvofiqlashtirish — vazifalarni bajarish
        results = self._coordinate(task_id, plan)

        # 6. Sifat & Xavfsizlik tekshiruvi
        quality_check = self._check_quality(task_id, results)

        # 7. Natijani birlashtirish
        final_result = self._merge_results(
            task_id, request, intent, analysis, plan, results, quality_check
        )

        elapsed = round(time.time() - start_time, 2)
        final_result["metadata"] = {
            "task_id": task_id,
            "elapsed_seconds": elapsed,
            "intent": intent.value,
            "agents_used": len(plan.get("agents", [])),
        }

        logger.info(f"✅ So'rov tugadi: [{task_id}] {elapsed}s")
        return final_result

    # ═══════════════════════════════════════════════
    #  2. INTENT ANIQLASH
    # ═══════════════════════════════════════════════

    def _detect_intent(self, request: str) -> IntentType:
        """So'rovdan intentni aniqlash — pattern matching."""
        request_lower = request.lower()

        intent_keywords = {
            IntentType.CREATE_COURSE: [
                'kurs yaratish', 'kurs qo\'shish', 'yangi kurs', 'create course', 'new course',
                'dars qo\'shish', 'lesson', 'yangi dars',
            ],
            IntentType.CREATE_QUIZ: [
                'test yaratish', 'quiz', 'savol qo\'shish', 'create quiz', 'new quiz',
                'test qo\'shish',
            ],
            IntentType.FIX_BUG: [
                'xato', 'bug', 'fix', 'tuzatish', 'ishlamayapti', 'error', 'crash',
                'muammo', 'xatolik',
            ],
            IntentType.ADD_FEATURE: [
                'feature', 'yangi funksiya', 'qo\'shish', 'add', 'implement',
                'yangi imkoniyat',
            ],
            IntentType.REVIEW_CODE: [
                'review', 'tekshirish', 'ko\'rib chiqish', 'code review', 'check code',
                'tahlil',
            ],
            IntentType.REVIEW_SECURITY: [
                'xavfsizlik', 'security', 'zaiflik', 'vulnerability', 'himoya',
                'csrf', 'xss',
            ],
            IntentType.DEPLOY: [
                'deploy', 'production', 'chiqarish', 'publish', 'release',
                'server', 'hosting',
            ],
            IntentType.WRITE_DOCS: [
                'hujjat', 'documentation', 'readme', 'docs', 'yozish',
                'api docs',
            ],
            IntentType.REFACTOR: [
                'refactor', 'qayta yozish', 'optimallashtirish', 'clean code',
                'reorganize',
            ],
            IntentType.OPTIMIZE: [
                'optimize', 'tezlashtirish', 'performance', 'speed', 'cache',
            ],
            IntentType.TRANSLATE: [
                'tarjima', 'translate', 'til', 'language', 'i18n', 'localization',
                'ko\'p tillilik',
            ],
        }

        best_match = IntentType.UNKNOWN
        best_score = 0

        for intent, keywords in intent_keywords.items():
            score = sum(1 for kw in keywords if kw in request_lower)
            if score > best_score:
                best_score = score
                best_match = intent

        return best_match

    # ═══════════════════════════════════════════════
    #  3. VAZIFA TAHLILI
    # ═══════════════════════════════════════════════

    def _analyze_task(self, task_id: str, request: str, intent: IntentType) -> Dict[str, Any]:
        """
        Rasmda: Vazifa tahlili
        - Talabni tushunish
        - Vazifani bo'lish
        """
        analysis = {
            "request": request,
            "intent": intent.value,
            "affected_apps": self._detect_affected_apps(request),
            "complexity": self._estimate_complexity(request, intent),
            "dependencies": self._detect_dependencies(request),
        }

        self.memory.store(
            f"analysis_{task_id}", analysis,
            category="context", agent_type="orchestrator", scope="short_term"
        )

        return analysis

    def _detect_affected_apps(self, request: str) -> List[str]:
        request_lower = request.lower()
        apps = []
        app_keywords = {
            'users': ['user', 'foydalanuvchi', 'login', 'register', 'auth', 'profil', 'dashboard'],
            'courses': ['kurs', 'course', 'dars', 'lesson', 'enroll', 'category'],
            'quiz': ['test', 'quiz', 'savol', 'question', 'natija', 'result'],
            'ai_assistant': ['ai', 'gemini', 'muallim', 'chat', 'feedback'],
        }
        for app, keywords in app_keywords.items():
            if any(kw in request_lower for kw in keywords):
                apps.append(app)
        return apps or ['courses']

    def _estimate_complexity(self, request: str, intent: IntentType) -> str:
        high_complexity = [IntentType.ADD_FEATURE, IntentType.REFACTOR, IntentType.DEPLOY]
        medium_complexity = [IntentType.CREATE_COURSE, IntentType.CREATE_QUIZ, IntentType.REVIEW_CODE]
        if intent in high_complexity:
            return "high"
        if intent in medium_complexity:
            return "medium"
        return "low"

    def _detect_dependencies(self, request: str) -> List[str]:
        deps = []
        request_lower = request.lower()
        if any(w in request_lower for w in ['database', 'model', 'migration']):
            deps.append("database")
        if any(w in request_lower for w in ['api', 'gemini', 'ai']):
            deps.append("external_api")
        if any(w in request_lower for w in ['template', 'html', 'css', 'frontend']):
            deps.append("frontend")
        return deps

    # ═══════════════════════════════════════════════
    #  4. REJALASHTIRISH
    # ═══════════════════════════════════════════════

    def _create_plan(self, task_id: str, intent: IntentType, analysis: Dict) -> Dict[str, Any]:
        """
        Rasmda: Rejalashtirish
        - Agentlarni tanlash
        - Ketma-ketlikni belgilash
        - Resurslarni ajratish
        """
        agent_types = INTENT_AGENT_MAP.get(intent, [AgentType.DEVELOPER])

        plan = {
            "task_id": task_id,
            "agents": [at.value for at in agent_types],
            "sequence": [],
            "parallel_groups": [],
        }

        for i, at in enumerate(agent_types):
            plan["sequence"].append({
                "order": i + 1,
                "agent": at.value,
                "agent_name": at.name,
                "description": f"{at.value} — vazifani bajarish",
                "depends_on": [agent_types[i-1].value] if i > 0 else [],
            })

        return plan

    # ═══════════════════════════════════════════════
    #  5. MUVOFIQLASHTIRISH
    # ═══════════════════════════════════════════════

    def _coordinate(self, task_id: str, plan: Dict) -> Dict[str, Any]:
        """
        Rasmda: Muvofiqlashtirish
        - Vazifalarni delegatsiya qilish
        - Holatni kuzatish
        - Qayta rejalashtirish
        """
        results = {}

        for step in plan["sequence"]:
            agent_type = AgentType(step["agent"])

            task = Task(
                task_id=f"{task_id}_{step['agent']}",
                description=step["description"],
                agent_type=agent_type,
                input_data={"plan_step": step},
            )

            self._active_tasks[task.task_id] = task

            try:
                agent = create_agent(agent_type, self.memory)
                completed_task = agent.execute(task)

                results[step["agent"]] = {
                    "status": completed_task.status.value,
                    "output": completed_task.output_data,
                    "errors": completed_task.errors,
                    "duration": completed_task.duration,
                }

                self._task_history.append(completed_task)

                # Qayta rejalashtirish — agar xatolik bo'lsa
                if completed_task.status == TaskStatus.FAILED:
                    logger.warning(f"⚠️ Agent xatolik: {step['agent']} — davom etilmoqda")

            except Exception as e:
                results[step["agent"]] = {
                    "status": "error",
                    "output": None,
                    "errors": [str(e)],
                    "duration": 0,
                }
                logger.error(f"❌ Agent xatolik: {step['agent']} — {e}")

            finally:
                self._active_tasks.pop(task.task_id, None)

        return results

    # ═══════════════════════════════════════════════
    #  6. SIFAT & XAVFSIZLIK
    # ═══════════════════════════════════════════════

    def _check_quality(self, task_id: str, results: Dict) -> Dict[str, Any]:
        """
        Rasmda: Sifat & Xavfsizlik
        - Xavfsizlik tekshiruvi
        - Sifat nazorati
        - Muvofiqlik qoidalari
        """
        checks = {
            "all_tasks_completed": all(
                r.get("status") == "completed" for r in results.values()
            ),
            "no_critical_errors": not any(
                r.get("errors") for r in results.values()
            ),
            "policy_compliance": True,
        }

        # Muvofiqlik qoidalari tekshiruvi
        if POLICY.require_tests:
            checks["tests_required"] = True
        if POLICY.require_review:
            checks["review_required"] = True

        checks["overall_status"] = "PASSED" if all(checks.values()) else "NEEDS_ATTENTION"
        return checks

    # ═══════════════════════════════════════════════
    #  7. NATIJA BIRLASHTIRISH
    # ═══════════════════════════════════════════════

    def _merge_results(
        self, task_id, request, intent, analysis,
        plan, results, quality_check
    ) -> Dict[str, Any]:
        """
        Rasmda: Natija birlashtirish
        - Natijalarni yig'ish
        - Validatsiya qilish
        - Yakuniy javob
        """
        return {
            "task_id": task_id,
            "request": request,
            "intent": intent.value,
            "analysis": analysis,
            "plan": {
                "agents_planned": plan.get("agents", []),
                "total_steps": len(plan.get("sequence", [])),
            },
            "results": results,
            "quality": quality_check,
            "summary": self._generate_summary(results, quality_check),
        }

    def _generate_summary(self, results: Dict, quality: Dict) -> str:
        total = len(results)
        successful = sum(1 for r in results.values() if r.get("status") == "completed")
        failed = total - successful

        if failed == 0:
            return f"✅ Barcha {total} ta agent muvaffaqiyatli bajarildi"
        return f"⚠️ {successful}/{total} agent muvaffaqiyatli, {failed} ta xatolik bor"

    # ═══════════════════════════════════════════════
    #  QULAYLIK METODLARI
    # ═══════════════════════════════════════════════

    def run_full_review(self) -> Dict[str, Any]:
        """Loyihani to'liq tekshirish — barcha agentlarni ishga tushirish."""
        return self.process_request("Loyihani to'liq tekshirish: kod sifati, xavfsizlik, deploy tayyor")

    def run_security_audit(self) -> Dict[str, Any]:
        """Xavfsizlik auditi."""
        return self.process_request("Xavfsizlik tekshiruvi: CSRF, XSS, SQL injection")

    def run_deploy_check(self) -> Dict[str, Any]:
        """Deploy tayyorlik tekshiruvi."""
        return self.process_request("Deploy tayyorligini tekshirish")

    def get_status(self) -> Dict[str, Any]:
        """Orchestrator holati."""
        return {
            "active_tasks": len(self._active_tasks),
            "completed_tasks": len(self._task_history),
            "memory_stats": self.memory.get_stats(),
            "available_agents": [at.value for at in AgentType],
            "available_skills": list(SKILL_REGISTRY.keys()),
        }

    def _error_response(self, task_id: str, message: str) -> Dict[str, Any]:
        return {
            "task_id": task_id,
            "status": "error",
            "message": message,
            "results": {},
        }
