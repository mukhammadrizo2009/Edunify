"""
Orchestrator CLI — terminal orqali ishlatish.

Foydalanish:
    python orchestrator/cli.py --request "Xavfsizlik tekshiruvi"
    python orchestrator/cli.py --review
    python orchestrator/cli.py --security
    python orchestrator/cli.py --deploy
    python orchestrator/cli.py --status
"""
import os
import sys
import json
import argparse

# Loyiha root'ini PATH ga qo'shish
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from orchestrator.engine import AIAgentOrchestrator


def print_result(result: dict, indent: int = 0):
    """Natijani chiroyli formatda chiqarish."""
    prefix = "  " * indent

    if isinstance(result, dict):
        for key, value in result.items():
            if isinstance(value, (dict, list)):
                print(f"{prefix}📌 {key}:")
                print_result(value, indent + 1)
            else:
                print(f"{prefix}  {key}: {value}")
    elif isinstance(result, list):
        for i, item in enumerate(result):
            if isinstance(item, dict):
                print(f"{prefix}  [{i+1}]")
                print_result(item, indent + 1)
            else:
                print(f"{prefix}  - {item}")
    else:
        print(f"{prefix}  {result}")


def main():
    parser = argparse.ArgumentParser(
        description="🤖 Edunify AI Agent Orchestrator CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Misollar:
  python orchestrator/cli.py --request "Kurs yaratish uchun nima kerak?"
  python orchestrator/cli.py --review
  python orchestrator/cli.py --security
  python orchestrator/cli.py --deploy
  python orchestrator/cli.py --status
        """
    )

    parser.add_argument("--request", "-r", type=str, help="So'rov matni")
    parser.add_argument("--review", action="store_true", help="To'liq loyiha tekshiruvi")
    parser.add_argument("--security", action="store_true", help="Xavfsizlik auditi")
    parser.add_argument("--deploy", action="store_true", help="Deploy tayyorlik tekshiruvi")
    parser.add_argument("--status", action="store_true", help="Orchestrator holati")
    parser.add_argument("--json", action="store_true", help="JSON formatda chiqarish")

    args = parser.parse_args()

    orchestrator = AIAgentOrchestrator()

    print("=" * 60)
    print("  🤖 EDUNIFY AI AGENT ORCHESTRATOR")
    print("=" * 60)

    if args.status:
        result = orchestrator.get_status()
        print("\n📊 Orchestrator holati:")
    elif args.review:
        print("\n🔍 To'liq loyiha tekshiruvi boshlanmoqda...")
        result = orchestrator.run_full_review()
    elif args.security:
        print("\n🛡️ Xavfsizlik auditi boshlanmoqda...")
        result = orchestrator.run_security_audit()
    elif args.deploy:
        print("\n🚀 Deploy tayyorlik tekshiruvi...")
        result = orchestrator.run_deploy_check()
    elif args.request:
        print(f"\n📥 So'rov: {args.request}")
        result = orchestrator.process_request(args.request)
    else:
        parser.print_help()
        return

    print()

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False, default=str))
    else:
        print_result(result)

    print()
    print("=" * 60)

    # Summary
    if "summary" in result:
        print(f"\n📋 Xulosa: {result['summary']}")
    if "metadata" in result:
        meta = result["metadata"]
        print(f"⏱️  Vaqt: {meta.get('elapsed_seconds', '?')}s")
        print(f"🤖 Agentlar: {meta.get('agents_used', '?')} ta")
    print()


if __name__ == "__main__":
    main()
