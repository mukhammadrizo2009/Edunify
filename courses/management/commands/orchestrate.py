"""
Django management command — Orchestrator'ni manage.py orqali ishlatish.

Foydalanish:
    python manage.py orchestrate --review
    python manage.py orchestrate --security
    python manage.py orchestrate --deploy
    python manage.py orchestrate --request "Xavfsizlik tekshiruvi"
    python manage.py orchestrate --status
"""
from django.core.management.base import BaseCommand
import json


class Command(BaseCommand):
    help = "🤖 Edunify AI Agent Orchestrator — loyihani agentlar bilan boshqarish"

    def add_arguments(self, parser):
        parser.add_argument("--request", "-r", type=str, help="So'rov matni")
        parser.add_argument("--review", action="store_true", help="To'liq loyiha tekshiruvi")
        parser.add_argument("--security", action="store_true", help="Xavfsizlik auditi")
        parser.add_argument("--deploy", action="store_true", help="Deploy tayyorlik tekshiruvi")
        parser.add_argument("--status", action="store_true", help="Orchestrator holati")
        parser.add_argument("--json-output", action="store_true", help="JSON formatda chiqarish")

    def handle(self, *args, **options):
        from orchestrator.engine import AIAgentOrchestrator

        orchestrator = AIAgentOrchestrator()

        self.stdout.write("=" * 60)
        self.stdout.write(self.style.SUCCESS("  🤖 EDUNIFY AI AGENT ORCHESTRATOR"))
        self.stdout.write("=" * 60)

        if options["status"]:
            result = orchestrator.get_status()
            self.stdout.write(self.style.HTTP_INFO("\n📊 Orchestrator holati:"))

        elif options["review"]:
            self.stdout.write(self.style.WARNING("\n🔍 To'liq loyiha tekshiruvi..."))
            result = orchestrator.run_full_review()

        elif options["security"]:
            self.stdout.write(self.style.WARNING("\n🛡️ Xavfsizlik auditi..."))
            result = orchestrator.run_security_audit()

        elif options["deploy"]:
            self.stdout.write(self.style.WARNING("\n🚀 Deploy tayyorlik tekshiruvi..."))
            result = orchestrator.run_deploy_check()

        elif options["request"]:
            self.stdout.write(f"\n📥 So'rov: {options['request']}")
            result = orchestrator.process_request(options["request"])

        else:
            self.stdout.write(self.style.ERROR("So'rov yoki flag belgilang. --help bilan ko'ring."))
            return

        self.stdout.write("")

        if options.get("json_output"):
            self.stdout.write(json.dumps(result, indent=2, ensure_ascii=False, default=str))
        else:
            self._print_result(result)

        if "summary" in result:
            self.stdout.write(self.style.SUCCESS(f"\n📋 Xulosa: {result['summary']}"))
        if "metadata" in result:
            meta = result["metadata"]
            self.stdout.write(f"⏱️  Vaqt: {meta.get('elapsed_seconds', '?')}s")
            self.stdout.write(f"🤖 Agentlar: {meta.get('agents_used', '?')} ta")

    def _print_result(self, data, indent=0):
        prefix = "  " * indent
        if isinstance(data, dict):
            for k, v in data.items():
                if isinstance(v, (dict, list)):
                    self.stdout.write(f"{prefix}📌 {k}:")
                    self._print_result(v, indent + 1)
                else:
                    self.stdout.write(f"{prefix}  {k}: {v}")
        elif isinstance(data, list):
            for i, item in enumerate(data):
                if isinstance(item, dict):
                    self.stdout.write(f"{prefix}  [{i+1}]")
                    self._print_result(item, indent + 1)
                else:
                    self.stdout.write(f"{prefix}  - {item}")
