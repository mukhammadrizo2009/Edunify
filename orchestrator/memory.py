"""
Xotira & Kontekst moduli.

Rasmda ko'rsatilgan:
├── Uzoq muddatli xotira
├── Loyiha konteksti
├── Qoidalar
└── Andozalar

Bu modul agentlar o'rtasida ma'lumot almashish va
kontekstni saqlash uchun ishlatiladi.
"""
import json
import time
import hashlib
import logging
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field, asdict
from pathlib import Path

logger = logging.getLogger("orchestrator.memory")


# ═══════════════════════════════════════════════
#  XOTIRA YOZUVI
# ═══════════════════════════════════════════════

@dataclass
class MemoryEntry:
    """Xotira yozuvi — har bir saqlangan ma'lumot."""
    key: str
    value: Any
    category: str              # 'context', 'rule', 'pattern', 'result', 'error'
    agent_type: str            # Qaysi agent yozgan
    timestamp: float = field(default_factory=time.time)
    ttl: Optional[int] = None  # Time-to-live (soniyalarda), None = abadiy
    tags: List[str] = field(default_factory=list)

    @property
    def is_expired(self) -> bool:
        if self.ttl is None:
            return False
        return (time.time() - self.timestamp) > self.ttl

    def to_dict(self) -> dict:
        return asdict(self)


# ═══════════════════════════════════════════════
#  XOTIRA SAQLASH TIZIMI
# ═══════════════════════════════════════════════

class MemoryStore:
    """
    Agentlar uchun markaziy xotira tizimi.

    3 qatlam:
    1. Qisqa muddatli (short-term) — joriy vazifa konteksti
    2. O'rta muddatli (session) — joriy sessiya davomida
    3. Uzoq muddatli (long-term) — diskka saqlanadi
    """

    def __init__(self, storage_dir: Optional[str] = None):
        # In-memory xotira
        self._short_term: Dict[str, MemoryEntry] = {}
        self._session: Dict[str, MemoryEntry] = {}
        self._long_term: Dict[str, MemoryEntry] = {}

        # Disk storage
        self._storage_dir = Path(storage_dir) if storage_dir else None
        if self._storage_dir:
            self._storage_dir.mkdir(parents=True, exist_ok=True)

        # Loyiha konteksti — andozalar va qoidalar
        self._load_project_context()

    def _load_project_context(self):
        """Loyiha kontekstini xotiraga yuklash."""
        from .config import PROJECT_CONTEXT, POLICY

        # Loyiha ma'lumotlari
        self.store("project_context", {
            "name": PROJECT_CONTEXT.project_name,
            "framework": PROJECT_CONTEXT.framework,
            "apps": PROJECT_CONTEXT.apps,
            "models": PROJECT_CONTEXT.models,
            "patterns": PROJECT_CONTEXT.patterns,
            "languages": PROJECT_CONTEXT.languages,
        }, category="context", agent_type="system")

        # Qoidalar
        self.store("security_policy", {
            "forbidden_operations": POLICY.forbidden_operations,
            "sensitive_fields": POLICY.sensitive_fields,
            "allowed_file_extensions": POLICY.allowed_file_extensions,
        }, category="rule", agent_type="system")

        # Andozalar
        self.store("coding_patterns", {
            "view_pattern": "Function-based views with decorators",
            "form_pattern": "Django Forms + Crispy Bootstrap5",
            "auth_pattern": "@login_required + teacher_required",
            "i18n_pattern": "session.get('lang', 'en') with if/elif/else",
            "error_pattern": "messages.error/success with language support",
        }, category="pattern", agent_type="system")

        logger.info("Loyiha konteksti xotiraga yuklandi")

    # ── CRUD operatsiyalari ────────────────────────

    def store(
        self,
        key: str,
        value: Any,
        category: str = "context",
        agent_type: str = "unknown",
        ttl: Optional[int] = None,
        tags: Optional[List[str]] = None,
        scope: str = "session",
    ) -> MemoryEntry:
        """Ma'lumotni xotiraga saqlash."""
        entry = MemoryEntry(
            key=key,
            value=value,
            category=category,
            agent_type=agent_type,
            ttl=ttl,
            tags=tags or [],
        )

        if scope == "short_term":
            self._short_term[key] = entry
        elif scope == "long_term":
            self._long_term[key] = entry
            self._persist_entry(entry)
        else:
            self._session[key] = entry

        logger.debug(f"Xotiraga saqlandi: [{scope}] {key} ({category})")
        return entry

    def retrieve(self, key: str) -> Optional[Any]:
        """Ma'lumotni xotiradan olish (barcha qatlamlardan qidiradi)."""
        # Qisqa muddatli → Session → Uzoq muddatli tartibida qidirish
        for store in [self._short_term, self._session, self._long_term]:
            if key in store:
                entry = store[key]
                if entry.is_expired:
                    del store[key]
                    continue
                return entry.value
        return None

    def search(
        self,
        category: Optional[str] = None,
        agent_type: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> List[MemoryEntry]:
        """Xotiradan qidirish — filtrlar bilan."""
        results = []
        for store in [self._short_term, self._session, self._long_term]:
            for entry in store.values():
                if entry.is_expired:
                    continue
                if category and entry.category != category:
                    continue
                if agent_type and entry.agent_type != agent_type:
                    continue
                if tags and not set(tags).issubset(set(entry.tags)):
                    continue
                results.append(entry)
        return results

    def clear_short_term(self):
        """Qisqa muddatli xotirani tozalash."""
        self._short_term.clear()
        logger.info("Qisqa muddatli xotira tozalandi")

    def clear_session(self):
        """Session xotirasini tozalash."""
        self._session.clear()
        logger.info("Session xotirasi tozalandi")

    # ── Maxsus operatsiyalar ───────────────────────

    def store_task_result(
        self,
        task_id: str,
        agent_type: str,
        result: Any,
        success: bool = True,
    ):
        """Vazifa natijasini saqlash."""
        self.store(
            key=f"task_result_{task_id}",
            value={
                "task_id": task_id,
                "agent_type": agent_type,
                "result": result,
                "success": success,
                "timestamp": time.time(),
            },
            category="result",
            agent_type=agent_type,
            tags=["task_result"],
        )

    def store_error(
        self,
        task_id: str,
        agent_type: str,
        error: str,
        traceback_info: Optional[str] = None,
    ):
        """Xatoni xotiraga saqlash — keyingi agentlar uchun kontekst."""
        self.store(
            key=f"error_{task_id}_{int(time.time())}",
            value={
                "task_id": task_id,
                "agent_type": agent_type,
                "error": error,
                "traceback": traceback_info,
                "timestamp": time.time(),
            },
            category="error",
            agent_type=agent_type,
            tags=["error", "task_error"],
        )

    def get_agent_context(self, agent_type: str) -> Dict[str, Any]:
        """Agent uchun kontekst yig'ish — loyiha ma'lumotlari + oldingi natijalar."""
        context = {
            "project": self.retrieve("project_context"),
            "patterns": self.retrieve("coding_patterns"),
            "policies": self.retrieve("security_policy"),
            "previous_results": [],
            "previous_errors": [],
        }

        # Oldingi natijalar
        results = self.search(category="result")
        context["previous_results"] = [
            entry.value for entry in results[-10:]  # Oxirgi 10 ta
        ]

        # Oldingi xatolar
        errors = self.search(category="error")
        context["previous_errors"] = [
            entry.value for entry in errors[-5:]  # Oxirgi 5 ta
        ]

        return context

    # ── Disk persistence ───────────────────────────

    def _persist_entry(self, entry: MemoryEntry):
        """Yozuvni diskka saqlash."""
        if not self._storage_dir:
            return
        try:
            safe_key = hashlib.md5(entry.key.encode()).hexdigest()
            filepath = self._storage_dir / f"{safe_key}.json"
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(entry.to_dict(), f, ensure_ascii=False, indent=2, default=str)
        except Exception as e:
            logger.error(f"Diskka saqlashda xatolik: {e}")

    def load_from_disk(self):
        """Diskdan uzoq muddatli xotirani yuklash."""
        if not self._storage_dir or not self._storage_dir.exists():
            return
        for filepath in self._storage_dir.glob("*.json"):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                entry = MemoryEntry(**data)
                if not entry.is_expired:
                    self._long_term[entry.key] = entry
            except Exception as e:
                logger.error(f"Diskdan o'qishda xatolik: {filepath} — {e}")

    # ── Statistikalar ──────────────────────────────

    def get_stats(self) -> Dict[str, Any]:
        """Xotira statistikasi."""
        return {
            "short_term_count": len(self._short_term),
            "session_count": len(self._session),
            "long_term_count": len(self._long_term),
            "total": len(self._short_term) + len(self._session) + len(self._long_term),
            "categories": self._count_by_category(),
        }

    def _count_by_category(self) -> Dict[str, int]:
        counts: Dict[str, int] = {}
        for store in [self._short_term, self._session, self._long_term]:
            for entry in store.values():
                counts[entry.category] = counts.get(entry.category, 0) + 1
        return counts
