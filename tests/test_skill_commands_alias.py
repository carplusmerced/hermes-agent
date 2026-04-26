"""Tests for skill slash-command aliases."""

from pathlib import Path


def _make_skill(skills_dir: Path, category: str, slug: str, name: str | None = None) -> Path:
    skill_dir = skills_dir / category / slug
    skill_dir.mkdir(parents=True, exist_ok=True)
    skill_name = name or slug
    (skill_dir / "SKILL.md").write_text(
        f"""---
name: {skill_name}
description: Description for {skill_name}.
---

# {skill_name}

Follow this skill.
""",
        encoding="utf-8",
    )
    return skill_dir


def test_skillify_is_registered_as_a_gateway_visible_command():
    """The short /skillify command should be visible to command registries/menus."""
    from hermes_cli.commands import GATEWAY_KNOWN_COMMANDS, COMMANDS, resolve_command

    cmd = resolve_command("skillify")

    assert cmd is not None
    assert cmd.name == "skillify"
    assert cmd.category == "Tools & Skills"
    assert "/skillify" in COMMANDS
    assert "skillify" in GATEWAY_KNOWN_COMMANDS



def test_skillify_short_alias_points_to_skillify_failures(monkeypatch, tmp_path):
    """The short /skillify command should invoke the skillify-failures skill."""
    import agent.skill_commands as skill_commands

    skill_dir = _make_skill(
        tmp_path,
        "autonomous-ai-agents",
        "skillify-failures",
        name="skillify-failures",
    )

    monkeypatch.setattr("tools.skills_tool.SKILLS_DIR", tmp_path)
    monkeypatch.setattr("agent.skill_utils.get_external_skills_dirs", lambda: [])
    skill_commands._skill_commands = {}

    commands = skill_commands.scan_skill_commands()

    assert "/skillify-failures" in commands
    assert "/skillify" in commands
    assert commands["/skillify"]["name"] == "skillify-failures"
    assert commands["/skillify"]["skill_dir"] == str(skill_dir)
    assert skill_commands.resolve_skill_command_key("skillify") == "/skillify"
    assert skill_commands.resolve_skill_command_key("skillify_failures") == "/skillify-failures"


def test_skillify_alias_builds_the_skillify_failures_invocation(monkeypatch, tmp_path):
    """Invoking /skillify should load the same skill payload as /skillify-failures."""
    import agent.skill_commands as skill_commands

    _make_skill(
        tmp_path,
        "autonomous-ai-agents",
        "skillify-failures",
        name="skillify-failures",
    )

    monkeypatch.setattr("tools.skills_tool.SKILLS_DIR", tmp_path)
    monkeypatch.setattr("agent.skill_utils.get_external_skills_dirs", lambda: [])
    skill_commands._skill_commands = {}

    msg = skill_commands.build_skill_invocation_message(
        "/skillify",
        "turn this regression into a permanent fix",
        task_id="session-123",
    )

    assert msg is not None
    assert 'invoked the "skillify-failures" skill' in msg
    assert "# skillify-failures" in msg
    assert "turn this regression into a permanent fix" in msg
