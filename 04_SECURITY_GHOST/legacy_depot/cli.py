#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
================================================================================
  MIOS CORE - BOT DEPOT CLI MANAGEMENT UTILITY
  Module       : 01_MIOS_CORE/bot_depot/cli.py
  Version      : v2.5.0-EnterpriseCLI
  Usage        : python3 -m bot_depot.cli [status|agents|health|scan|report|cfel|plans|calc|service-on|service-off|upgrade|exec]
================================================================================
"""

import sys
import json
from registry import bot_registry
from health_monitor import health_monitor
from security_engine import security_engine
from depot_dispatcher import depot_dispatcher
from cfel_auditor import cfel_auditor
from treasury import treasury
from live_command_bot import live_command_bot
from mioxid99_bot import mioxid99_bot
from upsell_engine import upsell_engine


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 -m bot_depot.cli <command> [args...]")
        print("Commands:")
        print("  status         - View central registry status and metrics")
        print("  agents         - View bot team list, versions, and tiers")
        print("  health         - View 7-point health check matrix")
        print("  scan           - Run security and integrity audit scan")
        print("  report-daily   - Dispatch daily shift reports to depot")
        print("  report-closing - Dispatch closing shift report to depot")
        print("  plans          - View all subscription and upsell tiers")
        print("  calc [amount]  - Calculate ROI projection for vault")
        print("  service-on     - Put bot fleet into service / maintenance mode")
        print("  service-off    - Resume bot fleet from maintenance mode")
        print("  upgrade <tier> - Execute tier upgrade (LITE/STANDARD/PRO/ENTERPRISE)")
        print("  cfel           - View CFEL audit ledger state")
        print("  exec <cmd>     - Execute a command through live command pipeline")
        sys.exit(1)

    cmd = sys.argv[1].lower()

    if cmd == "status":
        print("=== MIOS BOT REGISTRY STATUS (v2.5.0) ===")
        print(json.dumps(bot_registry.to_dict(), indent=2, ensure_ascii=False))

    elif cmd == "agents":
        print(bot_registry.generate_agents_view())

    elif cmd == "health":
        print(health_monitor.format_health_view())

    elif cmd == "scan":
        print("=== SECURITY & INTEGRITY SCAN RESULTS ===")
        print(json.dumps(security_engine.run_system_audit_scan(), indent=2, ensure_ascii=False))

    elif cmd == "plans":
        print(upsell_engine.generate_plans_comparison_markdown())

    elif cmd == "calc":
        vault = float(sys.argv[2]) if len(sys.argv) > 2 else 64131.62
        print(upsell_engine.generate_roi_table_markdown(vault))

    elif cmd in ("service-on", "maintenance-on"):
        reason = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else "Planlı Servis & Sürüm Yükseltme"
        bot_registry.set_maintenance_mode(enabled=True, reason=reason)
        cfel_auditor.seal_event(
            event_type="BOTS_MAINTENANCE_ENABLED",
            bot_id="cli-admin",
            action="SERVICE_ON",
            result="MAINTENANCE_ACTIVE",
            payload={"reason": reason}
        )
        depot_dispatcher.broadcast_maintenance_notice(enabled=True, reason=reason)
        print(f"🛠️ All bots placed in MAINTENANCE / SERVICE MODE. Reason: {reason}")

    elif cmd in ("service-off", "maintenance-off"):
        bot_registry.set_maintenance_mode(enabled=False)
        cfel_auditor.seal_event(
            event_type="BOTS_MAINTENANCE_DISABLED",
            bot_id="cli-admin",
            action="SERVICE_OFF",
            result="ONLINE",
            payload={"system_status": "NORMAL"}
        )
        depot_dispatcher.broadcast_maintenance_notice(enabled=False)
        print("🟢 All bots restored to ONLINE status.")

    elif cmd == "upgrade":
        tier = sys.argv[2].upper() if len(sys.argv) > 2 else "PRO"
        plan = upsell_engine.get_tier(tier)
        cfel_auditor.seal_event(
            event_type="SYSTEM_TIER_UPGRADED",
            bot_id="cli-admin",
            action=f"UPGRADE_TO_{tier}",
            result="SUCCESS",
            payload={"tier": tier, "price_usd": plan.price_usd_monthly}
        )
        print(f"🚀 System upgraded to {plan.badge} ({plan.name})")
        print(f"   • Monthly: ${plan.price_usd_monthly:,.0f} ({plan.price_try_monthly:,.0f} ₺)")
        print(f"   • Max Bots: {plan.max_bots} | Sniper: {'ACTIVE' if plan.solana_sniper_access else 'OFF'}")

    elif cmd == "report-daily":
        print("Broadcasting Daily Shift Reports to MİOXid Depot...")
        count = depot_dispatcher.broadcast_all_daily_reports()
        print(f"Sent {count} reports.")

    elif cmd == "report-closing":
        print("Broadcasting Daily Closing Shift Report to MİOXid Depot...")
        ok = depot_dispatcher.broadcast_closing_shift_report()
        print(f"Result: {ok}")

    elif cmd == "cfel":
        print("=== CFEL LEDGER STATE ===")
        state = cfel_auditor.get_state()
        valid, msg = cfel_auditor.verify_chain()
        print(json.dumps(state, indent=2, ensure_ascii=False))
        print(f"Chain Verification: {valid} ({msg})")

    elif cmd == "exec":
        sub_cmd = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else "/status"
        res = live_command_bot.execute_command(user_id="cli-admin", username="master", command_text=sub_cmd)
        print("--- RESPONSE ---")
        print(res.get("text"))

    else:
        print(f"Unknown command: {cmd}")


if __name__ == "__main__":
    main()
