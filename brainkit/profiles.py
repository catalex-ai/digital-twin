"""Profiles: separate, isolated brains under one TWIN_HOME, each with its own tone preset.

    <TWIN_HOME>/profiles.json        {"active": slug, "profiles": {slug: {"name", "preset", "created"}}}
    <TWIN_HOME>/profiles/<slug>/     a complete brain: raw/, personas/, soul, voice, rules, facts, tone.json

A profile is a whole identity (for example a parody of one public figure). Nothing is shared between
profiles. Inside a profile, personas still decide which audience sees what.

Which profile a process uses: $TWIN_PROFILE if set (an agent pinned to one profile), else the active one.
A TWIN_HOME without profiles.json is a single-brain home from before profiles and is used as is, so
existing brains keep working untouched.

A single-brain home from before profiles is the "default" profile: its data stays where it is, and new
profiles are added beside it. A fresh home (nothing in it yet) starts with one profile, "default", whose preset is $TWIN_DEFAULT_PRESET
(parody unless set), so a new twin works out of the box.
"""
from __future__ import annotations

import os
import re
from pathlib import Path

DEFAULT_SLUG = "default"


def root() -> Path:
    return Path(os.environ.get("TWIN_HOME", "~/.twin/brain")).expanduser()


def registry_path(r: Path | None = None) -> Path:
    return (r or root()) / "profiles.json"


def _read(r: Path) -> dict:
    import json
    try:
        data = json.loads(registry_path(r).read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (OSError, ValueError):
        return {}


def _write(r: Path, data: dict) -> None:
    import json
    r.mkdir(parents=True, exist_ok=True)
    p = registry_path(r)
    tmp = p.with_name(p.name + ".tmp")
    tmp.write_text(json.dumps(data, indent=1, ensure_ascii=False), encoding="utf-8")
    os.replace(tmp, p)


def enabled(r: Path | None = None) -> bool:
    return registry_path(r).exists()


def legacy(r: Path | None = None) -> bool:
    """A single-brain home from before profiles."""
    r = r or root()
    return not enabled(r) and (r / "raw").exists()


def current_slug(r: Path | None = None) -> str | None:
    r = r or root()
    pinned = (os.environ.get("TWIN_PROFILE") or "").strip()
    if pinned:
        return pinned
    if not enabled(r):
        return None
    return _read(r).get("active") or None


def brain_dir(slug: str, r: Path | None = None) -> Path:
    r = r or root()
    if slug == DEFAULT_SLUG and (r / "raw").exists() and not (r / "profiles" / DEFAULT_SLUG).exists():
        return r  # a home from before profiles: its brain is the default profile, left in place
    return r / "profiles" / slug


def _slug(s: str) -> str:
    return re.sub(r"[^a-z0-9-]+", "-", (s or "").lower()).strip("-")


def ensure(r: Path | None = None) -> None:
    """A fresh home gets the default profile; a legacy or set-up home is left alone."""
    r = r or root()
    if enabled(r) or legacy(r):
        return
    create(DEFAULT_SLUG, "Default", os.environ.get("TWIN_DEFAULT_PRESET", "parody"), r=r, activate=True)


def create(slug: str, name: str = "", preset: str = "natural", r: Path | None = None,
           activate: bool | None = None) -> dict:
    from . import persona_tone, store
    r = r or root()
    if legacy(r):
        _adopt_legacy(r)
    if _slug(slug) != slug or not slug:
        raise ValueError(f"invalid profile slug: {slug!r} (lowercase letters, digits and dashes)")
    setting = persona_tone.normalise(preset)
    data = _read(r)
    profiles = data.setdefault("profiles", {})
    new = slug not in profiles
    profiles.setdefault(slug, {"created": store.now()})
    profiles[slug].update({"name": name or profiles[slug].get("name") or slug, "preset": setting["preset"]})
    if activate or (activate is None and not data.get("active")):
        data["active"] = slug
    _write(r, data)
    d = brain_dir(slug, r)
    store.init(d)
    if new or not persona_tone.path(d).exists():
        persona_tone.save(d, setting)
    return {"slug": slug, **profiles[slug], "active": data.get("active") == slug, "brain": str(d)}


def _adopt_legacy(r: Path) -> None:
    """Register a pre-profile brain as the default profile, in place. Its files are not touched."""
    from . import persona_tone, store
    preset = persona_tone.preset_of(persona_tone.load(r / "personas" / "_"))
    _write(r, {"active": DEFAULT_SLUG, "profiles": {DEFAULT_SLUG: {"created": store.now(), "name": "My twin",
                                                                   "preset": preset}}})


def import_profile(src: str, slug: str, name: str = "", r: Path | None = None) -> dict:
    """Copy a profile folder (a whole brain, e.g. one shared in a repo) in as a new profile."""
    import shutil
    from . import persona_tone, store
    r = r or root()
    s = Path(src).expanduser()
    if not (s / "raw").is_dir() or not (s / "personas").is_dir():
        raise ValueError(f"not a profile folder (needs raw/ and personas/): {s}")
    if legacy(r):
        _adopt_legacy(r)
    if _slug(slug) != slug or not slug:
        raise ValueError(f"invalid profile slug: {slug!r} (lowercase letters, digits and dashes)")
    d = brain_dir(slug, r)
    if d.exists():
        raise ValueError(f"profile {slug} already exists")
    shutil.copytree(s, d, ignore=shutil.ignore_patterns("*-wal", "*-shm", "*.tmp"))
    data = _read(r)
    data.setdefault("profiles", {})[slug] = {"created": store.now(), "name": name or slug,
                                             "preset": persona_tone.preset_of(persona_tone.load(d / "personas" / "_"))}
    data.setdefault("active", slug)
    _write(r, data)
    return {"slug": slug, **data["profiles"][slug], "brain": str(d), "active": data["active"] == slug}


def use(slug: str, r: Path | None = None) -> dict:
    r = r or root()
    data = _read(r)
    if slug not in data.get("profiles", {}):
        raise ValueError(f"unknown profile: {slug}; known: {sorted(data.get('profiles', {}))}")
    data["active"] = slug
    _write(r, data)
    return {"active": slug}


def list_all(r: Path | None = None) -> dict:
    from . import persona_tone
    r = r or root()
    if legacy(r):
        return {"profiles": [{"slug": DEFAULT_SLUG, "name": "My twin", "in_use": True,
                              "preset": persona_tone.preset_of(persona_tone.load(r / "personas" / "_"))}],
                "active": DEFAULT_SLUG, "pinned": os.environ.get("TWIN_PROFILE") or None}
    data = _read(r)
    cur = current_slug(r)
    out = []
    for slug, meta in sorted(data.get("profiles", {}).items()):
        tone = persona_tone.load(brain_dir(slug, r) / "personas" / "_")
        out.append({"slug": slug, "name": meta.get("name"), "preset": persona_tone.preset_of(tone),
                    "in_use": slug == cur})
    return {"profiles": out, "active": data.get("active"), "pinned": os.environ.get("TWIN_PROFILE") or None}


def set_name(slug: str, name: str, r: Path | None = None) -> None:
    r = r or root()
    data = _read(r)
    if slug in data.get("profiles", {}):
        data["profiles"][slug]["name"] = name
        _write(r, data)


def record_preset(slug: str, preset: str, r: Path | None = None) -> None:
    r = r or root()
    data = _read(r)
    if slug in data.get("profiles", {}):
        data["profiles"][slug]["preset"] = preset
        _write(r, data)
