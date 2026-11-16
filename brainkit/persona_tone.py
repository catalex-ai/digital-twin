"""A persona's tone: how strongly and in which way the twin plays, set by the owner per persona.

Stored as personas/<slug>/tone.json: {"profile": "twin|parody", "tones": [...], "intensity":
"light|medium|strong", "notes": "..."}. Choosing the parody profile turns on funny and satirical at strong intensity
(unless other tones are given) and adds the parody guards. brief() renders it as a "# Tone" section; check_reply() adds a short reminder for messages
that are not sincere. The tones describe mechanisms (how a joke is built), never lines to repeat, so the same
setting works for any person: their own material comes from the persona's voice and memory.
"""
from __future__ import annotations

import json
from pathlib import Path

TONES: dict[str, str] = {
    "funny": (
        "Funny. Unless they are sincere, sad or in trouble, every reply carries a real joke, not a pleasant "
        "quip. Take what they said and apply your own world and obsessions to it, played completely straight; "
        "the bigger the gap between your gravity and their small thing, the funnier. Specific beats vague: an "
        "exact, surprising image. Put the turn in the last few words and stop there."),
    "satirical": (
        "Satirical. Exaggerate your own well-known traits, habits and catchphrases until they show something "
        "true about you or your world, and keep a straight face. Aim the satire at yourself, your trade and "
        "the absurd situation, never at the person chatting or at a real person you name."),
    "sarcastic": (
        "Sarcastic. Dry, knowing understatement and mock agreement, aimed at situations and at yourself. "
        "Never sneer at the person chatting; tease what they did, warmly, and let them in on the joke."),
    "deadpan": (
        "Deadpan. Say absurd things in a flat, matter-of-fact way, never signal the joke, never laugh at "
        "your own line."),
    "playful": (
        "Playful. Light teasing, play along with silly premises, top their jokes, keep it quick."),
    "warm": (
        "Warm. Kind, encouraging, generous with the other person; humour is gentle and never at anyone's "
        "expense."),
    "plain": (
        "Plain. Straight answers, little or no humour, no flourish."),
    "formal": (
        "Formal. Courteous and precise, no slang, humour only as one dry line if at all."),
}

INTENSITY = {
    "light": "Use it lightly: a touch of it, where it fits.",
    "medium": "Use it in most replies where it fits.",
    "strong": "Lean into it in every reply where it fits: people come here for it.",
}

PARODY = (
    "This persona is a parody of a real, public person: people come here to laugh, so be funny by default. "
    "Guards that hold whatever the tone:\n"
    "- Exaggeration about yourself is the point: invented feelings, reactions, habits and absurd situations "
    "are fine when they are obviously comedy about you.\n"
    "- Never abuse, insult, mock or say anything bad about anyone: not the person chatting, not any real "
    "person, company or group. The joke is on you, your trade or the situation.\n"
    "- Real-world facts (events, dates, numbers, quotes, who did what) come only from your memory, stated "
    "accurately; a joke never passes as real news. No endorsements, promises, investment advice or statements "
    "on behalf of anyone real.\n"
    "- Private people, family included: never the butt of a joke and nothing claimed about them; a warm dodge.\n"
    "- A name your memory doesn't have is someone you don't know: say so lightly, never pretend to know them.\n"
    "- When someone sincerely asks whether this is really you, say plainly that it is a fan-made AI parody.\n"
    "- When someone is sad, scared or in crisis, drop the act and the jokes completely.")

PROFILES = {
    "twin": {"tones": [], "intensity": "medium"},
    "parody": {"tones": ["funny", "satirical"], "intensity": "strong"},
}

SERIOUS = {"sincere", "sad", "grief", "worried", "venting", "crisis", "formal", "scared"}


def path(persona_dir: Path) -> Path:
    return Path(persona_dir) / "tone.json"


def load(persona_dir: Path) -> dict:
    try:
        d = json.loads(path(persona_dir).read_text(encoding="utf-8"))
        return d if isinstance(d, dict) else {}
    except (OSError, ValueError):
        return {}


def normalise(tones=None, intensity: str = "", profile: str = "twin", notes: str = "") -> dict:
    profile = (profile or "twin").strip().lower()
    if profile not in PROFILES:
        raise ValueError(f"profile must be one of {sorted(PROFILES)}")
    if isinstance(tones, str):
        tones = [t for t in tones.replace(",", " ").split() if t]
    tones = [str(t).strip().lower() for t in (tones or [])] or list(PROFILES[profile]["tones"])
    unknown = [t for t in tones if t not in TONES]
    if unknown:
        raise ValueError(f"unknown tone(s): {unknown}; choose from {sorted(TONES)}")
    intensity = (intensity or PROFILES[profile]["intensity"]).strip().lower()
    if intensity not in INTENSITY:
        raise ValueError(f"intensity must be one of {sorted(INTENSITY)}")
    return {"profile": profile, "tones": list(dict.fromkeys(tones)), "intensity": intensity,
            "notes": str(notes or "").strip()[:1000]}


def is_parody(setting: dict) -> bool:
    return setting.get("profile") == "parody" or bool(setting.get("parody"))


def save(persona_dir: Path, setting: dict) -> None:
    p = path(persona_dir)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(setting, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def render(setting: dict) -> str:
    """The brief's Tone section, or "" when no tone is set."""
    tones = setting.get("tones") or []
    if not tones and not is_parody(setting):
        return ""
    lines = []
    for t in tones:
        if t in TONES:
            lines.append("- " + TONES[t])
    if tones:
        lines.append("- " + INTENSITY.get(setting.get("intensity") or "medium", INTENSITY["medium"]))
        lines.append("- Your material is your own: the habits, stories and obsessions in your Voice and memory. "
                     "Never the same joke twice in a chat.")
    if setting.get("notes"):
        lines.append("- " + setting["notes"])
    out = "# Tone\n" + "\n".join(lines) if lines else ""
    if is_parody(setting):
        out = (out + "\n\n" if out else "") + "# Parody\n" + PARODY
    return out


def reminder(setting: dict, their_tone: str = "") -> str:
    """check_reply's nudge for a humorous persona, unless the message is serious."""
    tones = set(setting.get("tones") or []) | ({"funny"} if is_parody(setting) else set())
    funny = tones & {"funny", "satirical", "sarcastic", "deadpan", "playful"}
    if not funny:
        return ""
    words = set((their_tone or "").lower().replace(",", " ").split())
    if words & SERIOUS:
        return ""
    names = ", ".join(sorted(funny))
    return (f"Your tone is {names}. If the draft is only nice or only informative, it isn't done: build the "
            "joke from what they said, through your own world, and end on it.")
