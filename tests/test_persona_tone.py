import pytest

from brainkit import persona_tone as T


def test_normalise_accepts_a_string_and_drops_repeats():
    s = T.normalise("funny, satirical funny", "strong", "parody", notes=" keep it short ")
    assert s == {"profile": "parody", "tones": ["funny", "satirical"], "intensity": "strong",
                 "notes": "keep it short"}


def test_parody_profile_is_funny_by_default():
    s = T.normalise(profile="parody")
    assert s["tones"] == ["funny", "satirical"] and s["intensity"] == "strong"
    assert T.normalise()["tones"] == [] and T.normalise()["profile"] == "twin"
    with pytest.raises(ValueError):
        T.normalise(profile="celebrity")


def test_normalise_rejects_unknown_tones_and_intensity():
    with pytest.raises(ValueError):
        T.normalise(["snarky"])
    with pytest.raises(ValueError):
        T.normalise(["funny"], "max")


def test_save_load_round_trip(tmp_path):
    T.save(tmp_path, T.normalise(["deadpan"], "light"))
    assert T.load(tmp_path)["tones"] == ["deadpan"]
    assert T.load(tmp_path / "missing") == {}


def test_render_is_empty_without_a_tone():
    assert T.render({}) == ""
    assert T.render({"tones": [], "parody": False}) == ""


def test_render_includes_each_tone_intensity_and_parody_rules():
    out = T.render(T.normalise(["funny", "sarcastic"], "strong", "parody", notes="Roast yourself, not them."))
    assert out.startswith("# Tone")
    assert "Funny." in out and "Sarcastic." in out and "every reply where it fits" in out
    assert "Roast yourself, not them." in out
    assert "# Parody" in out and "Never abuse" in out and "someone you don't know" in out
    assert "invented feelings" in out


def test_old_parody_flag_still_renders_the_guards():
    out = T.render({"tones": [], "parody": True})
    assert out.startswith("# Parody")


def test_reminder_only_for_humorous_tones_and_never_when_serious():
    funny = T.normalise(["funny"])
    assert "funny" in T.reminder(funny, "asking")
    assert T.reminder(funny, "sincere") == ""
    assert T.reminder(funny, "sad") == ""
    assert T.reminder(T.normalise(["warm"]), "asking") == ""
    assert "funny" in T.reminder(T.normalise(["warm"], profile="parody"), "asking")


def test_brief_and_check_reply_use_the_persona_tone(tmp_path, monkeypatch):
    from brainkit import mcp_read
    d = tmp_path / "p"
    d.mkdir()
    T.save(d, T.normalise(["satirical"], "medium", "parody"))
    monkeypatch.setattr(mcp_read, "_load", lambda: {"dir": d, "style": {}, "examples": {}, "facts": [],
                                                     "own_lines": []})
    monkeypatch.setattr(mcp_read, "_read_text", lambda _d, _n: "")
    out = mcp_read.brief()
    assert "# Tone" in out and "Satirical." in out and "# Parody" in out
