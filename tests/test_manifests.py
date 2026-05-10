"""Manifest coverage for plugins imported by Prax."""
from __future__ import annotations

import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
KNOWN_ROUTES = {"artifact", "media", "research", "sysadmin", "utility", "vision", "workspace"}
KNOWN_RISKS = {"low", "medium", "high"}
KNOWN_EXPOSURE = {"none", "requested"}


def test_every_plugin_has_manifest():
    plugin_dirs = sorted(p.parent for p in REPO_ROOT.glob("*/plugin.py"))
    assert plugin_dirs

    missing = [str(p.relative_to(REPO_ROOT)) for p in plugin_dirs if not (p / "plugin.json").is_file()]
    assert missing == []


def test_manifests_are_valid_and_match_plugin_names():
    for manifest_path in sorted(REPO_ROOT.glob("*/plugin.json")):
        plugin_dir = manifest_path.parent
        data = json.loads(manifest_path.read_text(encoding="utf-8"))

        assert data["name"] == plugin_dir.name
        assert isinstance(data["version"], str) and data["version"]
        assert isinstance(data["description"], str) and data["description"]
        assert isinstance(data["tools"], list) and data["tools"]

        seen = set()
        for tool in data["tools"]:
            assert isinstance(tool["name"], str) and tool["name"]
            assert tool["name"] not in seen
            seen.add(tool["name"])
            assert isinstance(tool["description"], str) and tool["description"]
            assert tool["route"] in KNOWN_ROUTES
            assert tool["risk"] in KNOWN_RISKS
            assert tool.get("orchestrator_exposure", "none") in KNOWN_EXPOSURE

        source = (plugin_dir / "plugin.py").read_text(encoding="utf-8")
        for tool_name in seen:
            assert f"def {tool_name}(" in source


def test_presentation_tools_request_orchestrator_exposure():
    data = json.loads((REPO_ROOT / "txt2presentation" / "plugin.json").read_text(encoding="utf-8"))
    tools = {tool["name"]: tool for tool in data["tools"]}

    assert tools["text_to_presentation"]["route"] == "artifact"
    assert tools["text_to_presentation"]["orchestrator_exposure"] == "requested"
    assert tools["text_to_slides"]["route"] == "artifact"
