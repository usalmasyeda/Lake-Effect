# How we work in this repo

Simple rules so five people can work at once without breaking each other's work.

## 1. Get the code (once)

```bash
git clone https://github.com/usalmasyeda/Lake-Effect.git
cd lake-effect
```

New to Git? GitHub Desktop (desktop.github.com) does all of this with buttons.

## 2. Work on a branch, never directly on `main`

```bash
git checkout main
git pull                          # get everyone's latest work first
git checkout -b data/chlorophyll  # name it <area>/<what-you-are-doing>
```

Branch prefixes: `data/`, `web/`, `design/`, `docs/`, `story/`.

## 3. Save and share often

```bash
git add .
git commit -m "Add MODIS chlorophyll download script"
git push -u origin data/chlorophyll
```

Then open a **Pull Request** on GitHub into `main`. Small PRs, every hour or two, beat one giant PR on Sunday.

## 4. Reviews

- Anyone on the team can review and merge a PR. Don't wait hours for a review.
- If your PR changes the files the web app reads, follow [docs/data-format.md](docs/data-format.md) exactly, or tell the web developer first.

## 5. Tasks

Every task is a **GitHub Issue** with your name on it. Write `Closes #12` in your PR description and the issue closes when it's merged. Stuck for more than 30 minutes? Say so in Discord.

## 6. Hand-offs

Before you log off, add a short entry to [docs/handoffs.md](docs/handoffs.md) **and** post it in Discord: what's done, what's broken, what the next person should pick up.

## 7. Don't commit

- Raw satellite files (`data/raw/` is ignored; they're too big for GitHub)
- Passwords, API keys or Earthdata logins
- Sample numbers in the story or slides
