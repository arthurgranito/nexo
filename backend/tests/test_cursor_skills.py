"""Contrato das skills de desenvolvimento versionadas em .cursor/skills/."""
from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SKILLS_ROOT = REPO_ROOT / ".cursor" / "skills"

EXPECTED_SKILLS = (
    "nexo-tenant-review",
    "nexo-connector",
    "nexo-eval",
    "nexo-release",
)

REQUIRED_SECTIONS = (
    "## Entradas",
    "## Passos",
    "## Critérios de saída",
    "## Limites",
    "## Exemplo",
)

FRONTMATTER_NAME = re.compile(r"^name:\s*(nexo-[a-z-]+)\s*$", re.MULTILINE)
PROHIBITED_PERMISSIONS = (
    "compras",
    "mensagens externas",
    "deploy",
)


@pytest.mark.parametrize("skill_dir", EXPECTED_SKILLS)
def test_skill_directory_and_frontmatter(skill_dir: str) -> None:
    skill_path = SKILLS_ROOT / skill_dir / "SKILL.md"
    assert skill_path.is_file(), f"SKILL.md ausente: {skill_path}"

    text = skill_path.read_text(encoding="utf-8")
    assert text.startswith("---"), f"Frontmatter YAML obrigatório em {skill_dir}"
    assert "description:" in text.split("---", 2)[1], f"description ausente em {skill_dir}"

    match = FRONTMATTER_NAME.search(text)
    assert match is not None, f"name: no frontmatter de {skill_dir}"
    assert match.group(1) == skill_dir, f"name deve ser {skill_dir}"


@pytest.mark.parametrize("skill_dir", EXPECTED_SKILLS)
def test_skill_required_sections(skill_dir: str) -> None:
    text = (SKILLS_ROOT / skill_dir / "SKILL.md").read_text(encoding="utf-8")
    for section in REQUIRED_SECTIONS:
        assert section in text, f"{skill_dir}: seção faltando: {section}"


@pytest.mark.parametrize("skill_dir", EXPECTED_SKILLS)
def test_skill_limits_forbid_external_side_effects(skill_dir: str) -> None:
    text = (SKILLS_ROOT / skill_dir / "SKILL.md").read_text(encoding="utf-8")
    limits_block = text.split("## Limites", 1)[-1].split("##", 1)[0].lower()
    for phrase in PROHIBITED_PERMISSIONS:
        assert phrase in limits_block, (
            f"{skill_dir}: Limites deve mencionar restrição a '{phrase}'"
        )
