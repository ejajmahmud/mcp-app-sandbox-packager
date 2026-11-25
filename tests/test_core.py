"""Tests for MCP App Sandbox Packager."""
import unittest
from mcp_app_sandbox_packager.core import MCPAppPackager, SandboxPolicy


class TestMCPAppPackager(unittest.TestCase):
    def test_package_generates_csp_and_uri(self):
        pkg = MCPAppPackager("chart-ui")
        res = pkg.package("<div>Chart</div>", script="const x = 1;")
        self.assertEqual(res["uri"], "ui://mcp-app/chart-ui")
        self.assertEqual(res["sandboxAttr"], "allow-scripts")
        self.assertIn("default-src 'none'", res["cspHeader"])
        self.assertIn("sha256-", res["cspHeader"])

    def test_rejects_inline_script_in_html(self):
        pkg = MCPAppPackager("bad-ui")
        with self.assertRaises(ValueError):
            pkg.package("<script>evil()</script>")

    def test_enforces_size_budget(self):
        pkg = MCPAppPackager("tiny-ui", max_bytes=120)
        with self.assertRaises(ValueError):
            pkg.package("<div>" + ("A" * 200) + "</div>")

    def test_custom_connect_policy(self):
        pol = SandboxPolicy(allow_forms=True, connect_sources=["https://api.example.com"])
        pkg = MCPAppPackager("form-ui", policy=pol)
        res = pkg.package("<form></form>")
        self.assertIn("allow-forms", res["sandboxAttr"])
        self.assertIn("https://api.example.com", res["cspHeader"])
