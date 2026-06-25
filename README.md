# Lemma Quickstart

An interactive "Get started with Lemma" guide. The reader picks a path
(developer or non-developer, and which AI coding agent they have) and gets a
step-by-step walkthrough to a working pod.

`index.html` is a single self-contained page — every screenshot is embedded, so
it works anywhere with no external files and no build step.

## Project structure

| Path | What it is |
|------|------------|
| `index.html` | The deployable page (generated). All images embedded. |
| `lemma-quickstart.template.html` | Source HTML with `{{IMG_*}}` placeholders. **Edit copy here.** |
| `screenshots/` | Source screenshots used to build the images. |
| `opencode-desktop-walkthrough.gif` | OpenCode setup walkthrough (embedded into the page). |
| `build.py` | Regenerates `index.html` from the template + screenshots. |

## Editing

- **Text / layout / steps** → edit `lemma-quickstart.template.html`, then rebuild.
- **Screenshots** → replace files in `screenshots/` (keep the same names), then rebuild.

```bash
pip install pillow
python3 build.py        # writes index.html
```

`build.py` redacts a private email on the sign-in shot, crops the browser chrome
off the Step-1 shots, draws the annotation boxes (Recheck, harness, model
selector), encodes everything to WebP, and embeds the GIF.

> Don't hand-edit the base64 images inside `index.html` — change the source and
> rebuild instead.

## Deploy

Static site — no framework, no build command on the host. On Vercel it serves
`index.html` at the root.
