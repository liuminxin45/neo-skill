"""ai-skill-creator

Canonical SkillSpec -> multi-target outputs (Claude/Windsurf/Cursor/GitHub Skills).

Design goals:
- Deterministic generation (same spec -> same files)
- Strict validation (especially for Claude frontmatter)
- Progressive disclosure (keep SKILL.md concise; offload details to references/)
"""

__all__ = ["__version__"]
__version__ = "0.1.0"
