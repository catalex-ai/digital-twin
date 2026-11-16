import json

import pytest

from brainkit import mcp_manage as M, persona_tone, profiles, store


@pytest.fixture
def home(tmp_path, monkeypatch):
    monkeypatch.setenv("TWIN_HOME", str(tmp_path / "brain"))
    monkeypatch.delenv("TWIN_PROFILE", raising=False)
    monkeypatch.delenv("TWIN_DEFAULT_PRESET", raising=False)
    return tmp_path / "brain"


def test_fresh_home_gets_a_parody_default_profile(home):
    M.init()
    assert profiles.current_slug() == "default"
    assert store.home() == home / "profiles" / "default"
    assert persona_tone.preset_of(persona_tone.load(store.home() / "personas" / "_")) == "parody"


def test_default_preset_can_be_changed(home, monkeypatch):
    monkeypatch.setenv("TWIN_DEFAULT_PRESET", "natural")
    M.init()
    assert persona_tone.preset_of(persona_tone.load(store.home() / "personas" / "_")) == "natural"


def test_legacy_home_becomes_the_default_profile_in_place(home):
    store.init(home)
    M.init()
    assert not (home / "profiles.json").exists() and store.home() == home
    before = sorted(p.name for p in home.iterdir())
    M.create_profile("parody-x", "X", "parody")
    assert store.home() == home / "profiles" / "parody-x"
    M.use_profile("default")
    assert store.home() == home  # the old brain, where it always was
    assert set(before) <= {p.name for p in home.iterdir()}
    listed = {p["slug"]: p for p in M.list_profiles()["profiles"]}
    assert listed["default"]["preset"] == "natural" and listed["parody-x"]["preset"] == "parody"


def test_import_profile_copies_a_shared_brain(home, tmp_path):
    M.init()
    M.create_profile("src", "Src", "parody")
    M.define_category("background", "where I come from")
    M.add_items([{"text": "I was born in Alphaville.", "category": "background"}])
    out = M.import_profile(str(home / "profiles" / "src"), "copy", "Copy")
    assert out["preset"] == "parody" and not out["active"]
    M.use_profile("copy")
    assert "Alphaville" in json.dumps(M.list_items())
    assert "error" in M.import_profile(str(tmp_path), "bad")


def test_profiles_are_isolated(home):
    M.init()
    M.create_profile("alpha", "Alpha", "parody")
    M.create_persona("public", "strangers", "everything public", "nothing private")
    M.define_category("background", "where I come from")
    M.add_items([{"text": "I was born in Alphaville.", "category": "background"}])
    a_items = M.list_items()
    M.create_profile("beta", "Beta", "serious")
    assert store.home() == home / "profiles" / "beta"
    assert "Alphaville" not in json.dumps(M.list_items())
    assert M.status()["personas"] == []
    M.use_profile("alpha")
    assert "Alphaville" in json.dumps(M.list_items()) and a_items
    listed = {p["slug"]: p for p in M.list_profiles()["profiles"]}
    assert listed["alpha"]["preset"] == "parody" and listed["beta"]["preset"] == "serious"
    assert listed["alpha"]["in_use"] and not listed["beta"]["in_use"]


def test_pinned_profile_wins_over_active(home, monkeypatch):
    M.init()
    M.create_profile("alpha", "Alpha", "parody")
    M.create_profile("beta", "Beta", "serious")
    monkeypatch.setenv("TWIN_PROFILE", "alpha")
    assert store.home() == home / "profiles" / "alpha"


def test_set_tone_changes_the_current_profile(home):
    M.init()
    M.create_profile("alpha", "Alpha", "natural")
    out = M.set_tone("leader", intensity="light")
    assert out["profile"] == "alpha" and out["preset"] == "leader"
    assert M.list_profiles()["profiles"][0]["preset"] == "leader"
    assert M.status()["tone"]["preset"] == "leader"


def test_bad_slug(home):
    M.init()
    assert "error" in M.create_profile("Jensen Huang", "J", "parody")
