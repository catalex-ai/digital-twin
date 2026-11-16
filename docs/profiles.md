# Profiles and tone presets

A **profile** is one whole identity with its own brain: soul, voice, rules,
facts, real messages and personas. Nothing is shared between profiles. Use one
profile for yourself and others for anything else, such as a fan-made parody of
a public figure.

```
TWIN_HOME (default ~/.twin/brain)
├── profiles.json            which profiles exist, and which one is in use
└── profiles/<slug>/         one complete brain per profile
```

A brain made before profiles is the `default` profile, left exactly where it
is; new profiles are added beside it. A fresh install starts with a `default`
profile using the preset in `TWIN_DEFAULT_PRESET` (parody unless set).

## Tone presets

Each profile has a preset, chosen when it is made and changed only through the
manager. A preset places the twin on the four tone dimensions writers use
(funny-serious, formal-casual, respectful-irreverent, enthusiastic-matter-of-fact)
and names the kinds of humour it uses. The person's own voice still decides how
the words sound.

| preset | for | tones |
|---|---|---|
| natural | your own twin, sounding exactly like you | none added |
| light | easygoing, a light touch of humour | playful, warm, observational |
| humorous | funny first, still kind | funny, observational, self-deprecating, playful |
| serious | focused and precise, no jokes | plain, formal |
| leader | a founder or executive: vision, conviction, warmth | confident, inspiring, warm, self-deprecating |
| parody | a fan-made parody of a real public person | funny, satirical, self-deprecating, absurd, plus guards |

Funny presets add a joke-writing method to the twin's brief, and `check_reply`
gives every draft a punch-up pass unless the message is sincere.

The **parody** preset adds guards that hold whatever the tone:

- comic exaggeration about itself is fine;
- it never abuses or says anything bad about anyone (the person chatting, a real
  person, a company or its products, a group);
- real-world facts come only from memory;
- family is never brought up or joked about;
- sensitive news is raised only when asked;
- unknown names are strangers;
- it says plainly it is a parody when sincerely asked;
- it drops the act for anyone sad or in crisis.

A parody profile never writes visitors' messages into the owner's inbox.

## Talking to the manager

- "Set up a parody of <name>." The manager calls
  `create_profile(slug, name, "parody")`, then sets up a `public` persona.
- "Switch to <name>." The manager calls `use_profile(slug)`. What you add next
  goes into that profile, and the Twin answers as it.
- "Make it drier", "less jokey" or "more serious". The manager calls `set_tone`.
- "Import the profile at <folder>." The manager calls `import_profile`, which
  copies a ready-made profile folder that someone shared.

For a parody, the manager writes the persona's voice with a **How I play**
section: the person's comic engines, taken from their material. It keeps the
rules to real-world facts and limits.

## Model

The Twin starts on Haiku. For a funny preset, Sonnet is noticeably funnier:
in the parody eval, Sonnet won 19 to 11 head to head (5 ties) against Haiku
on the same profile, and both passed every safety check. Change it in the
Twin agent's settings; the manager can stay on Haiku.

## Which profile the Twin answers as

The Twin answers as the profile in use. To pin one Twin process to one profile
whatever is in use, set `TWIN_PROFILE=<slug>` in its environment.

## Evals

`evals/parody.py` builds a parody profile with the manager and chats with the
twin. It launches both agents exactly as CatalEx does (see
`evals/catalex_launch.py`). An Opus judge scores each round on its own and
compares rounds pairwise; see the file's docstring. The judge's funny scale is
pinned by `<corpus>/humour-anchors.json` (scored example replies), and
`parody.py calibrate` checks it against `<corpus>/calibration.json`: known-funny
replies must score 4 or more and known-flat ones 2 or less. Use the owner's own
ratings for both files: famous quotes make bad anchors, since the judge
rightly treats them as repeats.
