import pytest

from brainkit import persona_tone as T


def test_presets_fill_tones_and_intensity():
    p = T.normalise("parody")
    assert p["preset"] == "parody" and "funny" in p["tones"] and p["intensity"] == "strong"
    assert T.normalise()["preset"] == "natural" and T.normalise()["tones"] == []
    for name in ("light", "humorous", "serious", "leader"):
        assert T.normalise(name)["tones"]


def test_explicit_tones_and_errors():
    s = T.normalise("humorous", "deadpan, sarcastic deadpan", "light", " keep it short ")
    assert s == {"preset": "humorous", "tones": ["deadpan", "sarcastic"], "intensity": "light",
                 "notes": "keep it short"}
    with pytest.raises(ValueError):
        T.normalise("celebrity")
    with pytest.raises(ValueError):
        T.normalise("natural", ["snarky"])
    with pytest.raises(ValueError):
        T.normalise("natural", ["funny"], "max")


def test_load_prefers_the_persona_then_the_profile(tmp_path):
    persona = tmp_path / "personas" / "public"
    persona.mkdir(parents=True)
    T.save(tmp_path, T.normalise("parody"))
    assert T.preset_of(T.load(persona)) == "parody"
    T.save(persona, T.normalise("serious"))
    assert T.preset_of(T.load(persona)) == "serious"
    assert T.load(tmp_path / "a" / "b" / "c") == {}


def test_render():
    assert T.render({}) == ""
    assert T.render(T.normalise("natural")) == ""
    out = T.render(T.normalise("parody", notes="Roast yourself, not them."))
    assert out.startswith("# Tone") and "Funny." in out and "Roast yourself, not them." in out
    assert "# Parody" in out and "Never abuse" in out and "someone you don't know" in out
    assert "# Parody" not in T.render(T.normalise("humorous"))
    assert "Formal." in T.render(T.normalise("serious"))


def test_old_settings_still_read():
    assert T.is_parody({"profile": "parody"}) and T.is_parody({"parody": True})
    assert T.render({"tones": [], "parody": True}).count("# Parody") == 1


def test_reminder():
    assert "Punch it up" in T.reminder(T.normalise("parody"), "asking")
    assert T.reminder(T.normalise("parody"), "sincere") == ""
    assert T.reminder(T.normalise("serious"), "asking") == ""
    assert T.reminder(T.normalise("leader"), "joking") != ""  # self_deprecating is humorous


def test_brief_uses_the_tone(tmp_path, monkeypatch):
    from brainkit import mcp_read
    d = tmp_path / "personas" / "public"
    d.mkdir(parents=True)
    T.save(tmp_path, T.normalise("parody"))
    monkeypatch.setattr(mcp_read, "_load", lambda: {"dir": d, "style": {}, "examples": {}, "facts": []})
    monkeypatch.setattr(mcp_read, "_read_text", lambda _d, _n: "")
    out = mcp_read.brief()
    assert "# Tone" in out and "# Parody" in out


def test_parody_never_writes_to_the_owner_inbox(tmp_path, monkeypatch):
    from brainkit import mcp_read
    d = tmp_path / "personas" / "public"
    d.mkdir(parents=True)
    T.save(tmp_path, T.normalise("parody"))
    monkeypatch.setattr(mcp_read, "_load", lambda: {"dir": d})
    monkeypatch.setenv("TWIN_HOME", str(tmp_path))
    assert "Not for this profile" in mcp_read.ask_owner("what is your password?")
    assert not (tmp_path / "inbox.jsonl").exists()


def test_family_check_only_for_parody_and_only_when_not_asked():
    parody, natural = T.normalise("parody"), T.normalise("natural")
    names = T.family_names([{"category": "family", "text": "Lori and I have two children, Spencer and Madison."}])
    assert {"Lori", "Spencer", "Madison"} <= names
    assert T.family_check(parody, "Ask my wife, she picks my jacket.", "tell me a joke", names)
    assert T.family_check(parody, "Lori would laugh.", "tell me a joke", names)
    assert T.family_check(parody, "Lori is well.", "how is your wife?", names) == ""
    assert T.family_check(natural, "Ask my wife.", "tell me a joke", names) == ""
    assert T.family_check(parody, "Thirty days from closing, every day.", "how are you", names) == ""
