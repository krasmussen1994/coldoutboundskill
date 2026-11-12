# CLAUDE.md

Cold outbound skills for Claude Code — ICP definition, list building, domain/inbox
infrastructure, copywriting, sending, deliverability, and buying-signal playbooks.
Forked from [growthenginenowoslawski/coldoutboundskills](https://github.com/growthenginenowoslawski/coldoutboundskills).

## How this repo is wired into Claude Code

This repo is a Claude Code **plugin**, not a loose folder of markdown:

```
.claude-plugin/plugin.json       # plugin manifest (name: cold-outbound-skills)
.claude-plugin/marketplace.json  # single-plugin marketplace, source "./"
.claude/settings.json            # auto-registers the marketplace + enables the plugin
skills/<skill-name>/SKILL.md     # the 51 skills, all one level deep
```

Opening this repo in Claude Code registers the marketplace and enables the plugin, so all
51 skills are invocable as `/<skill-name>`. To use them from *other* projects:

```bash
claude plugin marketplace add krasmussen1994/coldoutboundskill
claude plugin install cold-outbound-skills@coldoutboundskill
```

### Rules when adding or editing skills

- **One level only.** Skill discovery does not recurse — `skills/foo/SKILL.md` loads,
  `skills/group/foo/SKILL.md` does not. (This is why the 20 Track 6 playbooks live at
  `skills/playbook-*` here rather than under `skills/playbooks/` as upstream has them.)
- Every skill needs YAML frontmatter with `name` (matching its directory) and `description`.
- The `description` is the only thing loaded into every session — write it as trigger text
  ("use when the user says X"), not as a summary.
- Adding a skill costs ~150 always-on tokens in every session. The 51 skills currently cost
  ~8.1k. Run `claude plugin details cold-outbound-skills` to re-measure.
- Validate before committing: `claude plugin validate .` and `claude plugin validate skills`.

## Running the scripts

Scripts are TypeScript run with `tsx`, and each skill's `SKILL.md` invokes them relative to
its own directory:

```bash
npm install -g tsx
cd skills/<skill-name> && npx tsx scripts/<name>.ts
```

### API keys — three different loading conventions

There is no single `.env` location that every script honors, so **export the keys into your
shell environment**: that is the one path all three loaders respect.

| Loader | Where it looks |
|---|---|
| `skills/list-expander/scripts/lib.ts` | walks up to the repo-root `.env`, then `$PWD/.env`, then `~/.env`; process env wins |
| `skills/cold-email-starter-kit/scripts/_lib.ts` | only `skills/cold-email-starter-kit/.env`; otherwise falls back to process env |
| `skills/smartlead-inbox-manager/scripts/_lib.ts` | process env only |

```bash
cp .env.example .env      # fill in the keys you need
set -a; source .env; set +a
```

`.env` files are gitignored at every level. Never commit a real key, and never paste one
into a SKILL.md, a script default, or a commit message.

Full key-by-key reference is in `.env.example` and the table in `README.md`. Minimum for a
first campaign: `DYNADOT_API_KEY` + `ZAPMAIL_API_KEY` + `PROSPEO_API_KEY` + `SMARTLEAD_API_KEY`.

## Working conventions

- **Uploads to Smartlead are always DRAFT.** `smartlead-campaign-upload-public` never starts a
  campaign — a human hits Start. Do not "helpfully" launch one.
- **Client work stays out of git.** `profiles/`, `campaign-plan-*.md`, `scorecard-*.md`,
  `health-*.csv` and `tmp-audit/` are gitignored on purpose — they hold real prospect data.
- **Don't email consumers, honor unsubscribes, include a real physical address.** The skills
  assume B2B cold email under CAN-SPAM/GDPR; keep it that way.
- `/cold-email-kickoff` is the entry point for a new client or a new campaign — it chains
  ICP → lead magnet → strategy → plan. Reach for it before hand-rolling a sequence.

## Not included in this fork

Upstream ships a `Common Outbound Lists/` directory (~500 MB of Google Maps and US SaaS
company zips). It is deliberately left out here to keep clones fast and stay under GitHub's
file-size limits. Pull it from upstream if you need it:

```bash
git clone --depth 1 https://github.com/growthenginenowoslawski/coldoutboundskills /tmp/upstream
cp -r "/tmp/upstream/Common Outbound Lists" .
```

`Common Outbound Lists/` is gitignored here so a local copy never gets committed back.
