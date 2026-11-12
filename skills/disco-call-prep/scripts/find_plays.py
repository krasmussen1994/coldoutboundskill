#!/usr/bin/env python3
"""Find IntentSignal's closest proven plays for a prospect's buyer, and pull a real email
that got a positive reply.

Reads <CLIENT>_INSTANTLY_API_KEY and <CLIENT>_EMAILBISON_API_KEY from the environment.
Prints JSON. Never prints lead names or email addresses except inside the example email body.

  python3 find_plays.py rank --persona own --persona hr [--min-people 3000] [--min-pos 15] [--top 6]
  python3 find_plays.py example --ws BRIDGEWOOD_CREATIVE --tool emailbison --campaign 113
"""
import argparse, html, json, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
EB = "https://send.intentsignal.ai/api/"
INST = "https://api.instantly.ai/api/v2/"


def curl(url, key, body=None):
    cmd = ["curl", "-sS", "-m", "90", "-H", "Authorization: Bearer " + key, "-H", "Accept: application/json"]
    if body is not None:
        cmd += ["-X", "POST", "-H", "Content-Type: application/json", "-d", json.dumps(body)]
    r = subprocess.run(cmd + [url], capture_output=True, text=True)
    try:
        return json.loads(r.stdout)
    except Exception:
        return {}


def keys(suffix):
    return {k[: -len(suffix)]: v for k, v in os.environ.items() if k.endswith(suffix) and v}


def clean(txt):
    t = re.sub(r"<br\s*/?>|</p>|</div>", "\n", txt or "")
    t = re.sub(r"<[^>]+>", "", t)
    t = html.unescape(t)
    t = re.sub(r"\n{3,}", "\n\n", t)
    # drop signature / footer
    t = re.split(r"\n--|\{\{accountSignature\}\}|\{SENDER_EMAIL_SIGNATURE\}", t)[0]
    return t.strip()


def campaigns():
    out = []
    for ws, key in keys("_INSTANTLY_API_KEY").items():
        d = curl(INST + "campaigns/analytics", key)
        if not isinstance(d, list):
            continue
        for x in d:
            out.append(dict(ws=ws, tool="instantly", id=x["campaign_id"], name=x["campaign_name"],
                            people=x.get("new_leads_contacted_count") or 0, pos=x.get("total_opportunities") or 0,
                            replies=x.get("reply_count_unique") or 0))
    for ws, key in keys("_EMAILBISON_API_KEY").items():
        p = 1
        while p <= 20:
            d = curl(EB + f"campaigns?page={p}", key)
            for x in d.get("data", []) or []:
                out.append(dict(ws=ws, tool="emailbison", id=x["id"], name=x["name"],
                                people=x.get("total_leads_contacted") or 0, pos=x.get("interested") or 0,
                                replies=x.get("unique_replies") or 0))
            if p >= (d.get("meta", {}) or {}).get("last_page", 1):
                break
            p += 1
    return out


def rank(a):
    meta = json.load(open(os.path.join(HERE, "plays.json")))["clients"]
    rows = []
    for c in campaigns():
        m = meta.get(c["ws"])
        if not m or (a.persona and m["p"] not in a.persona):
            continue
        if c["people"] < a.min_people or c["pos"] < a.min_pos:
            continue
        c.update(persona=m["p"], descriptor=m["d"], who=m["who"], rate=round(c["people"] / c["pos"]))
        rows.append(c)
    rows.sort(key=lambda r: r["rate"])
    # at most 2 plays per client so one client can't fill the list
    seen, top = {}, []
    for r in rows:
        if seen.get(r["ws"], 0) >= 2:
            continue
        seen[r["ws"]] = seen.get(r["ws"], 0) + 1
        top.append(r)
        if len(top) >= a.top:
            break
    print(json.dumps(top, indent=1))


def example(a):
    key = os.environ.get(f"{a.ws}_{'INSTANTLY' if a.tool == 'instantly' else 'EMAILBISON'}_API_KEY")
    if not key:
        sys.exit("no API key for " + a.ws)
    subj = body = None
    if a.tool == "instantly":
        d = curl(INST + "leads/list", key, {"limit": 50, "campaign": a.campaign, "filter": "FILTER_LEAD_INTERESTED"})
        for x in d.get("items", []):
            pl = x.get("payload") or {}
            b = pl.get("email_1") or pl.get("Email 1") or pl.get("email1")
            if b:
                subj, body = pl.get("subject_line") or pl.get("Subject Line") or "", b
                break
        if not body:
            c = curl(INST + f"campaigns/{a.campaign}", key)
            try:
                v = c["sequences"][0]["steps"][0]["variants"][0]
                subj, body = v.get("subject"), v.get("body")
            except Exception:
                pass
    else:
        p = 1
        while p <= 15 and not body:
            d = curl(EB + f"replies?status=interested&page={p}", key)
            for r in d.get("data", []) or []:
                if str(r.get("campaign_id")) != str(a.campaign):
                    continue
                cv = {c.get("name", "").lower(): c.get("value") for c in ((r.get("lead") or {}).get("custom_variables") or []) if isinstance(c, dict)}
                if cv.get("email_1"):
                    subj, body = cv.get("subject_line") or "", cv["email_1"]
                    break
            if p >= (d.get("meta", {}) or {}).get("last_page", 1):
                break
            p += 1
        if not body:
            s = curl(EB + f"campaigns/{a.campaign}/sequence-steps", key)
            try:
                st = s["data"][0]
                subj, body = st.get("email_subject"), st.get("email_body")
            except Exception:
                pass
    templated = bool(re.search(r"\{\{|\{[A-Z_]+\}", (body or "") + (subj or "")))
    print(json.dumps({"subject": clean(subj or ""), "body": clean(body or ""), "is_template": templated}, indent=1))


ap = argparse.ArgumentParser()
sp = ap.add_subparsers(dest="cmd", required=True)
r = sp.add_parser("rank")
r.add_argument("--persona", action="append", default=[])
r.add_argument("--min-people", type=int, default=3000)
r.add_argument("--min-pos", type=int, default=15)
r.add_argument("--top", type=int, default=6)
e = sp.add_parser("example")
e.add_argument("--ws", required=True)
e.add_argument("--tool", choices=["instantly", "emailbison"], required=True)
e.add_argument("--campaign", required=True)
args = ap.parse_args()
{"rank": rank, "example": example}[args.cmd](args)
