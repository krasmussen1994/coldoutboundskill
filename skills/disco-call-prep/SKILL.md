---
name: disco-call-prep
description: Use when Kyle wants prep for an upcoming new-business / intro / discovery call, says "prep my call with X", "set up the calculator for <prospect>", or when the scheduled call-prep task fires. Prefills the IntentSignal Outbound ROI calculator for the prospect and emails Kyle a one-page brief with the closest proven plays and a real email that got a positive reply.
---

# Discovery call prep

Output per call: (1) a preset in the ROI calculator's database so `https://claude.ai/artifact/X4BAkr62irNyypZ3nYcHkJ#<slug>` opens prefilled, and (2) an email to kyle@intentsignal.co with the brief and that link.

## 1. Find the calls

Google Calendar, today and tomorrow before noon (America/Chicago). A new-business call is an event with at least one attendee outside `intentsignal.co`, and usually the Calendly event "Intro Call - Cold Email" (its description carries "Company Name" and "Your Job Title"). Skip internal meetings, existing clients (check the agreements in Agree or Clarify deals in a Won/In Pilot stage), and anything already prepped: read `presets/<slug>` with ArtifactData first; if it exists and its `call` matches the event start, skip it.

`slug` = the prospect's domain without the TLD, lowercase, letters/digits/hyphens only (backd.com → `backd`).

## 2. Research the prospect

- Clay `search-companies` with `where domain = "<domain>"`: size, industry, location, description. Free; never run enrichment.
- The calendar description and any Calendly / Gmail thread for their title and what they asked about.
- Decide who THEY sell to (their buyer, not them): department, seniority, company size, industry. That is what the calculator models.

## 3. Pick the closest plays

```bash
cd skills/disco-call-prep/scripts
python3 -I find_plays.py rank --persona <key> [--persona <key2>] --top 6
python3 -I find_plays.py example --ws <WS> --tool <instantly|emailbison> --campaign <id>
```

Persona keys: sales, mkt, hr, fin, cs, it, ecom, prod, own. Read `plays.json` for what each client sells and who it emails, and choose the 2 plays whose buyer is genuinely closest (same buyer type and company size beats a better reply rate). Read every `who` line: a play listed under a persona can still email a different buyer (the business lender emails restructuring advisors, not owners). Use `example` to pull a real email that got a positive reply. If `is_template` is true the body is a template, not a sent email: say so or pick another play.

Never name the client in anything prospect-facing: use its `d` description.

## 4. Write the preset

ArtifactData `set` on `https://claude.ai/artifact/X4BAkr62irNyypZ3nYcHkJ`, collection `presets`, doc_id `<slug>` (read it first; pass `if_version` if it exists):

```json
{"name": "Backd", "persona": "own", "sen": "own", "size": "s2", "ind": "any",
 "client": "Creative agency", "tam": 50000, "cpc": 1, "win": 15, "deal": 6000,
 "call": "<event start ISO>", "contact": "<name, title>",
 "note": "<one sentence on why these plays>",
 "plays": [{"label": "...", "who": "...", "rate": 105, "people": 3560, "positives": 34, "subject": "...", "body": "..."}]}
```

- `sen`, `size` and `ind` each take one key or an array of keys (several = an equal mix, e.g. `"sen": ["vp","c"]`). `sen`: any | own | c | vp | dir. `size`: any | s1 (1-10) | s2 (11-50) | s3 (51-200) | s4 (201-1,000) | s5 (1,001-5,000) | s6 (5,001-10,000) | s7 (10,000+). `ind`: any | sw | ret | hc | con | ps | mfg | fin | hosp | ag | edu.
- `client` is optional: a `d` description from plays.json to use as the IntentSignal benchmark instead of the persona median. Use it when one play is clearly closer than the persona average.
- `tam` = companies in their ICP, `cpc` = decision makers per company, `win` = meeting-to-deal %, `deal` = first-year deal value. These are starting guesses: base them on the company's size, price point and market, and say in the email that they are guesses. There is no meeting goal: the page works out the meeting ceiling from the market.

## 5. Email Kyle

Gmail `send_message` to kyle@intentsignal.co only. Subject `Call prep: <Company> (<Name>, <Title>) <time> <day>`. Short HTML:

1. Two lines on the company and the person.
2. The prefilled link `https://claude.ai/artifact/X4BAkr62irNyypZ3nYcHkJ#<slug>` and the settings it loads.
3. What the calculator shows: industry vs IntentSignal people per positive reply, the meeting ceiling (industry average vs our approach), the test package and the package that reaches the ceiling, and the weakest assumption.
4. The two plays: buyer, people per positive reply (people emailed, positives), and the real email in a blockquote.
5. Four questions to confirm on the call.

Plain language, no em dashes, no hype. Apply the humanizer rules before sending.

## Rules

- Read-only on every sending platform: never change campaigns, leads or inboxes.
- Email only Kyle. Never email the prospect.
- If a step fails (no calendar match, no domain, no plays), still email Kyle what you found and what is missing.
