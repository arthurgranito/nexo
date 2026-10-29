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
    "nexo-dev-implementer",
    "nexo-dev-isolation-reviewer",
    "nexo-dev-quality",
    "nexo-dev-ux",
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

MCP_DOC = REPO_ROOT / "docs" / "mcp-desenvolvimento.md"
MCP_EXAMPLE = REPO_ROOT / ".cursor" / "mcp.json.example"

MCP_REQUIRED_SECTIONS = (
    "## Veredito",
    "## Escopo mínimo por bloco",
    "Documentação oficial",
    "GitHub do repositório",
    "Banco local de teste",
    "Browser de staging",
    "## Servidor MCP customizado Nexo",
    "execute_sql",
    "Testes de abuso",
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


def test_mcp_desenvolvimento_doc_contract() -> None:
    assert MCP_DOC.is_file(), f"Documento MCP ausente: {MCP_DOC}"
    text = MCP_DOC.read_text(encoding="utf-8").lower()
    for section in MCP_REQUIRED_SECTIONS:
        assert section.lower() in text, f"mcp-desenvolvimento.md: seção faltando: {section}"
    assert "inf-002" in text, "deve apontar próximo ticket INF-002"


def test_mcp_json_example_no_real_secrets() -> None:
    assert MCP_EXAMPLE.is_file(), f"Exemplo MCP ausente: {MCP_EXAMPLE}"
    raw = MCP_EXAMPLE.read_text(encoding="utf-8")
    assert "ghp_" not in raw and "sk-" not in raw
    assert "${GITHUB_TOKEN}" in raw or "GITHUB_TOKEN" in raw
    assert "127.0.0.1" in raw, "DSN de exemplo deve ser apenas localhost"
