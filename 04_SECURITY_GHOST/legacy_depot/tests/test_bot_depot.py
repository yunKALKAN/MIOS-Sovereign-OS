#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
================================================================================
  MIOS BOT DEPOT TEST SUITE
  Module : 01_MIOS_CORE/bot_depot/tests/test_bot_depot.py
  Version: v2.5.0-EnterpriseTest
================================================================================
"""

import os
import unittest
import tempfile
from bot_depot.treasury import SecretTreasury, mask_secret, SCOPE_LIVE_COMMAND, SCOPE_GUARDIAN
from bot_depot.cfel_auditor import CFELBotAuditor
from bot_depot.event_bus import MIOSEventBus, EVENT_SECURITY_ALERT
from bot_depot.registry import BotRegistry, BotDescriptor
from bot_depot.security_engine import SecurityTamperEngine
from bot_depot.health_monitor import BotHealthMonitor
from bot_depot.depot_dispatcher import BotDepotDispatcher
from bot_depot.live_command_bot import MIOSLiveCommandBot
from bot_depot.mioxid99_bot import MIOXid99Bot
from bot_depot.upsell_engine import UpsellEngine, PLANS


class TestSecretTreasury(unittest.TestCase):
    def test_secret_masking(self):
        self.assertEqual(mask_secret(""), "<EMPTY>")
        self.assertEqual(mask_secret("1234567890abcdef"), "1234...cdef")

    def test_scoped_access(self):
        treasury = SecretTreasury()
        sol_key = treasury.request_secret("mios-live-command", "SOLANA_PRIVATE_KEY", SCOPE_GUARDIAN)
        self.assertIsNone(sol_key)

        master_key = treasury.request_secret("mios-core-master", "SOLANA_RPC_URL", "ALL")
        self.assertIsNotNone(master_key)


class TestCFELAuditor(unittest.TestCase):
    def test_hash_chaining_and_sanitization(self):
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tf:
            temp_path = tf.name

        auditor = CFELBotAuditor(ledger_file=temp_path)
        h1 = auditor.seal_event(
            event_type="TEST_START",
            bot_id="test-bot",
            action="INIT",
            result="OK",
            payload={"secret_token": "super_secret_123", "status": "active"}
        )
        self.assertNotEqual(h1, "0" * 64)

        records = auditor.get_recent_records(1)
        self.assertEqual(len(records), 1)
        self.assertIn("REDACTED_HASH", records[0]["payload"]["secret_token"])

        valid, msg = auditor.verify_chain()
        self.assertTrue(valid)
        if os.path.exists(temp_path):
            os.remove(temp_path)


class TestEventBus(unittest.TestCase):
    def test_publish_subscribe(self):
        bus = MIOSEventBus()
        received = []

        def handler(ev):
            received.append(ev)

        bus.subscribe("CUSTOM_TEST_EVENT", handler)
        bus.publish("CUSTOM_TEST_EVENT", "test-bot", {"value": 42}, seal_cfel=False)
        self.assertEqual(len(received), 1)
        self.assertEqual(received[0].data["value"], 42)


class TestBotRegistry(unittest.TestCase):
    def test_initial_fleet_and_versions(self):
        registry = BotRegistry()
        bots = registry.list_bots()
        self.assertGreaterEqual(len(bots), 6)
        bot_ids = [b.bot_id for b in bots]
        self.assertIn("mios-live-command", bot_ids)
        self.assertIn("mioxid-99", bot_ids)
        self.assertIn("mios-guardian", bot_ids)
        self.assertIn("mios-signal", bot_ids)
        self.assertIn("mios-telemetry", bot_ids)
        self.assertIn("mios-cfel", bot_ids)

        live_cmd = registry.get_bot("mios-live-command")
        self.assertIn("v2.5.0", live_cmd.version)
        self.assertEqual(live_cmd.tier, "PRO")

    def test_maintenance_mode(self):
        registry = BotRegistry()
        self.assertFalse(registry.is_maintenance_mode())

        registry.set_maintenance_mode(enabled=True, reason="Unit Test Maintenance")
        self.assertTrue(registry.is_maintenance_mode())
        view = registry.generate_agents_view()
        self.assertIn("BAKIM", view)

        registry.set_maintenance_mode(enabled=False)
        self.assertFalse(registry.is_maintenance_mode())


class TestUpsellEngine(unittest.TestCase):
    def test_plans_structure(self):
        engine = UpsellEngine()
        tiers = engine.list_tiers()
        self.assertEqual(len(tiers), 4)
        tier_keys = [t.tier_id for t in tiers]
        self.assertListEqual(tier_keys, ["LITE", "STANDARD", "PRO", "ENTERPRISE"])

        pro_tier = engine.get_tier("PRO")
        self.assertEqual(pro_tier.price_usd_monthly, 149.0)
        self.assertTrue(pro_tier.solana_sniper_access)

    def test_roi_calculation(self):
        engine = UpsellEngine()
        roi = engine.calculate_roi_projection(60000.0)
        self.assertEqual(roi["vault_try"], 60000.0)
        self.assertEqual(len(roi["projections"]), 4)

        pro_proj = next(p for p in roi["projections"] if p["tier_id"] == "PRO")
        self.assertGreater(pro_proj["estimated_net_try"], 0)

    def test_upsell_trigger(self):
        engine = UpsellEngine()
        trig = engine.evaluate_upsell_trigger("Solana DEX sniper ve çoklu bot kullanmak istiyorum", current_tier="STANDARD")
        self.assertIsNotNone(trig)
        self.assertEqual(trig["target_tier"]["tier_id"], "PRO")


class TestSecurityEngine(unittest.TestCase):
    def test_malicious_command_filter(self):
        engine = SecurityTamperEngine()
        safe, err = engine.validate_command_safety("user-1", "rm -rf /")
        self.assertFalse(safe)
        self.assertIsNotNone(err)

        safe2, _ = engine.validate_command_safety("user-1", "/status")
        self.assertTrue(safe2)


class TestHealthMonitor(unittest.TestCase):
    def test_health_view_format(self):
        monitor = BotHealthMonitor()
        view = monitor.format_health_view()
        self.assertIn("MIOS BOT HEALTH", view)
        self.assertIn("Core .", view)
        self.assertIn("Telegram .", view)
        self.assertIn("OVERALL:", view)


class TestLiveCommandPipeline(unittest.TestCase):
    def test_all_commands(self):
        bot = MIOSLiveCommandBot()
        commands = [
            "/start", "/help", "/status", "/balance", "/wallet",
            "/position", "/pnl", "/signal", "/guardian", "/cfel",
            "/system", "/agents", "/telemetry", "/health",
            "/plans", "/upgrade PRO", "/calc 50000", "/maintenance"
        ]
        for cmd in commands:
            resp = bot.execute_command("user-1", "operator", cmd)
            self.assertIn("text", resp)
            self.assertTrue(len(resp["text"]) > 10)


if __name__ == "__main__":
    unittest.main()
