"""Core MCP App bundler with strict CSP and iframe sandbox generation."""
import hashlib
import base64
from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class SandboxPolicy:
    allow_scripts: bool = True
    allow_forms: bool = False
    allow_same_origin: bool = False
    connect_sources: List[str] = field(default_factory=list)

    def sandbox_attr(self) -> str:
        flags = []
        if self.allow_scripts:
            flags.append("allow-scripts")
        if self.allow_forms:
            flags.append("allow-forms")
        if self.allow_same_origin:
            flags.append("allow-same-origin")
        return " ".join(flags)

    def build_csp(self, script_sha256_b64: str) -> str:
        connect = " ".join(self.connect_sources) if self.connect_sources else "'none'"
        return (
            f"default-src 'none'; "
            f"style-src 'unsafe-inline'; "
            f"script-src 'sha256-{script_sha256_b64}'; "
            f"connect-src {connect}; "
            f"frame-ancestors 'self';"
        )


class MCPAppPackager:
    """Packages interactive HTML/JS widgets into hardened MCP App resources."""

    def __init__(self, app_id: str, max_bytes: int = 131072, policy: SandboxPolicy = None):
        self.app_id = app_id
        self.max_bytes = max_bytes
        self.policy = policy or SandboxPolicy()

    def package(self, html_body: str, script: str = "", title: str = "MCP App") -> Dict[str, str]:
        if "<script" in html_body.lower():
            raise ValueError("Inline <script> tags in html_body are forbidden; pass JS via script parameter")

        bridge_js = (
            "window.__MCP_APP_ID__ = " + repr(self.app_id) + ";\n"
            + script
        ).strip()
        script_hash = base64.b64encode(hashlib.sha256(bridge_js.encode("utf-8")).digest()).decode("ascii")
        csp = self.policy.build_csp(script_hash)

        document = (
            "<!DOCTYPE html><html><head><meta charset='utf-8'>"
            f'<meta http-equiv="Content-Security-Policy" content="{csp}">'
            f"<title>{title}</title></head><body>{html_body}"
            f"<script>{bridge_js}</script></body></html>"
        )
        raw = document.encode("utf-8")
        if len(raw) > self.max_bytes:
            raise ValueError(f"Bundle size {len(raw)} exceeds limit {self.max_bytes}")

        digest = hashlib.sha256(raw).hexdigest()
        return {
            "uri": f"ui://mcp-app/{self.app_id}",
            "mimeType": "text/html;profile=mcp-app",
            "sandboxAttr": self.policy.sandbox_attr(),
            "cspHeader": csp,
            "sha256": digest,
            "sizeBytes": str(len(raw)),
            "html": document,
        }
