#!/usr/bin/env python3
"""
IAM 최소권한 역산 — CloudTrail 실사용 이력으로 "부여 권한"을 깎는다 (사용자+역할).

입력:
  <ct_dir>     : cloudtrail_rightsize.sh 출력 디렉터리 (cloudtrail-all.json)
                 (구버전 호환: cloudtrail-<user>.json 도 인식)
  <policy_dir> : policies-all.json 이 있는 디렉터리 (기본 iam-over)
  <run_id>     : 리포트 폴더명

로직(전부 오프라인·읽기 전용):
  1) CloudTrail Events → userIdentity 로 사용자(IAMUser)·역할(AssumedRole)에 귀속
     → 엔티티별 실사용 IAM 액션(eventSource+eventName) + 관측 리소스 ARN
  2) policies-all.json 의 정책(attached_to=user:/role:)과 대조
  3) 부여 패턴 중 미관측 = 제거 후보, Resource:* = 관측 ARN 으로 치환 제안
  4) <entity>-rightsized-policy.json + report.md 출력

주의: 조회창이 짧으면 저빈도 정당 권한이 '미관측'으로 보인다. read(Get/List/Describe)와
      iam:PassRole·S3 데이터이벤트는 누락되기 쉬우니 자동 삭제 금지 — 사람 확인 후 적용.
"""
from __future__ import annotations
import fnmatch
import json
import os
import sys

SOURCE_PREFIX = {
    "monitoring.amazonaws.com": "cloudwatch",
    "logs.amazonaws.com": "logs",
    "email.amazonaws.com": "ses",
    "tagging.amazonaws.com": "tag",
}
READ_VERBS = ("get", "list", "describe", "batchget", "search", "lookup",
              "head", "select", "query", "scan", "view", "check")
# CloudTrail 에 잘 안 잡히지만 빠지면 동작이 깨지는 액션 → 미관측이어도 보존
BLIND_KEEP = {"iam:passrole", "sts:assumerole"}


def _prefix(src: str) -> str:
    return SOURCE_PREFIX.get(src, src.replace(".amazonaws.com", ""))


def _is_read(action: str) -> bool:
    return action.split(":", 1)[-1].lower().startswith(READ_VERBS)


def _as_list(x):
    return [] if x is None else (x if isinstance(x, list) else [x])


def _collect_arns(detail: dict) -> set:
    arns = set()
    for r in _as_list(detail.get("Resources")):
        if isinstance(r, dict):
            nm = r.get("ResourceName") or r.get("resourceName")
            if nm and str(nm).startswith("arn:"):
                arns.add(nm)

    def _walk(o):
        if isinstance(o, dict):
            for v in o.values():
                _walk(v)
        elif isinstance(o, list):
            for v in o:
                _walk(v)
        elif isinstance(o, str) and o.startswith("arn:"):
            arns.add(o)
    _walk(detail.get("requestParameters"))
    _walk(detail.get("responseElements"))
    return arns


def _entity_of(ui: dict):
    """userIdentity → 'user:<name>' / 'role:<name>' / None."""
    t = ui.get("type")
    if t == "IAMUser":
        return f"user:{ui.get('userName')}" if ui.get("userName") else None
    if t == "AssumedRole":
        iss = ui.get("sessionContext", {}).get("sessionIssuer", {})
        if iss.get("type") == "Role" and iss.get("userName"):
            return f"role:{iss['userName']}"
    return None


def usage_from_all(ct_path: str) -> dict:
    """cloudtrail-all.json → {entity: {'used':set,'arns':set}}."""
    out = {}
    if not os.path.exists(ct_path):
        return out
    data = json.load(open(ct_path, encoding="utf-8"))
    for ev in data.get("Events", []):
        try:
            detail = json.loads(ev.get("CloudTrailEvent", "{}"))
        except Exception:
            detail = {}
        detail.setdefault("Resources", ev.get("Resources"))
        ent = _entity_of(detail.get("userIdentity", {}))
        if not ent:
            continue
        src = detail.get("eventSource") or ev.get("EventSource", "")
        name = detail.get("eventName") or ev.get("EventName", "")
        if not src or not name:
            continue
        rec = out.setdefault(ent, {"used": set(), "arns": set()})
        rec["used"].add(f"{_prefix(src)}:{name}")
        rec["arns"] |= _collect_arns(detail)
    return out


def usage_from_peruser(ct_dir: str, user: str) -> dict:
    """구버전 호환: cloudtrail-<user>.json."""
    p = os.path.join(ct_dir, f"cloudtrail-{user}.json")
    if not os.path.exists(p):
        return {"used": set(), "arns": set()}
    used, arns = set(), set()
    for ev in json.load(open(p, encoding="utf-8")).get("Events", []):
        src, name = ev.get("EventSource", ""), ev.get("EventName", "")
        if src and name:
            used.add(f"{_prefix(src)}:{name}")
        try:
            arns |= _collect_arns(json.loads(ev.get("CloudTrailEvent", "{}")))
        except Exception:
            pass
    return {"used": used, "arns": arns}


def rightsize_statement(stmt: dict, used: set, observed_arns: set):
    rows = []
    patterns = [str(a) for a in _as_list(stmt.get("Action"))]
    resources = [str(r) for r in _as_list(stmt.get("Resource"))]
    has_wild = any(r == "*" for r in resources)
    matched = set()
    blind = set()  # 미관측이지만 보존할 액션(PassRole 등)
    for pat in patterns:
        hits = sorted(u for u in used if fnmatch.fnmatch(u.lower(), pat.lower()))
        is_blind = pat.lower() in BLIND_KEEP
        if hits:
            status, kind = "USED", ("read" if _is_read(pat) else "write")
        elif is_blind:
            status, kind = "BLIND", "blind"
            blind.add(pat)
        else:
            status, kind = "UNUSED", ("read" if _is_read(pat) else "write")
        rows.append({"pattern": pat, "status": status, "hits": hits, "kind": kind})
        matched.update(hits)
    if not matched and not blind:
        return None, rows
    keep_actions = sorted(matched | blind)
    if has_wild:
        svc = {a.split(":", 1)[0] for a in matched}
        scoped = sorted(a for a in observed_arns
                        if any(a.startswith(f"arn:aws:{p}:") for p in svc))
        new_res = scoped if scoped else resources
    else:
        new_res = resources
    rs = {k: v for k, v in stmt.items() if k not in ("Action", "Resource")}
    rs["Action"] = keep_actions
    rs["Resource"] = new_res if len(new_res) != 1 else new_res[0]
    return rs, rows


def analyze_entity(entity: str, policy_recs: list, usage: dict):
    used, arns = usage.get("used", set()), usage.get("arns", set())
    mine = [p for p in policy_recs if p.get("attached_to") == entity]
    out_stmts, table = [], []
    for p in mine:
        for stmt in _as_list((p.get("document") or {}).get("Statement")):
            rs, rows = rightsize_statement(stmt, used, arns)
            sid = stmt.get("Sid", "(no-sid)")
            for r in rows:
                r["policy"], r["sid"], r["ptype"] = p.get("name"), sid, p.get("type")
            table.extend(rows)
            if rs is not None:
                rs.setdefault("Sid", sid)
                out_stmts.append(rs)
    return {"policy": {"Version": "2012-10-17", "Statement": out_stmts},
            "table": table, "used": used, "arns": arns}


def render_md(run_id: str, results: dict) -> str:
    L = [f"# IAM 최소권한 역산 리포트 — run `{run_id}`", "",
         "> CloudTrail 실사용 이력(lookup-events)으로 부여 권한을 역산. 모두 읽기 전용 분석이며, "
         "**제거·치환은 제안일 뿐 실제 변경은 사람이 검토 후 수행**한다.", "",
         "> ⚠️ 조회창이 짧으면 저빈도 정당 권한이 '미관측'으로 보일 수 있다. 특히 read(Get/List/"
         "Describe), `iam:PassRole`(소비 서비스 이벤트에 묻힘), S3 데이터이벤트는 누락되기 쉬움.", ""]
    L += ["## 요약", "", "| 엔티티 | 실사용 액션 | 부여 패턴 | 사용 | 미관측(제거후보) | 관측 ARN |",
          "|---|---|---|---|---|---|"]
    for ent, R in results.items():
        rows = R["table"]
        nu = sum(1 for r in rows if r["status"] == "USED")
        nun = sum(1 for r in rows if r["status"] == "UNUSED")
        L.append(f"| `{ent}` | {len(R['used'])} | {len(rows)} | {nu} | {nun} | {len(R['arns'])} |")
    L.append("")
    for ent, R in results.items():
        rows = R["table"]
        if not rows:
            continue
        L += [f"## `{ent}`", "",
              "| 정책 | 유형 | Sid | 부여 패턴 | 종류 | 상태 | 실관측 액션 |",
              "|---|---|---|---|---|---|---|"]
        for r in rows:
            kind = {"read": "🔵read", "write": "🟠write"}.get(r["kind"], "🟣blind")
            status = {"USED": "✅ 사용", "BLIND": "🟣 미관측·보존"}.get(r["status"], "⬜ 미관측")
            hits = ", ".join(r["hits"]) if r["hits"] else "—"
            L.append(f"| {r['policy']} | {r.get('ptype','')} | {r['sid']} | `{r['pattern']}` "
                     f"| {kind} | {status} | {hits} |")
        safe = ent.replace(":", "-")
        L += ["", f"**제안 최소권한 정책**: ✅만 남기고 와일드카드 `Resource:*`는 관측 ARN으로 좁힌 "
              f"`{safe}-rightsized-policy.json` 참조.", ""]
        if R["arns"]:
            L += ["관측 리소스 ARN:", ""] + [f"- `{a}`" for a in sorted(R["arns"])] + [""]
    return "\n".join(L)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    ct_dir = args[0] if args else "iam-out"
    policy_dir = args[1] if len(args) > 1 else "iam-over"
    run_id = args[2] if len(args) > 2 else "iam-rightsize"

    pol_path = os.path.join(policy_dir, "policies-all.json")
    policy_recs = json.load(open(pol_path, encoding="utf-8")) if os.path.exists(pol_path) else []
    entities = sorted({p["attached_to"] for p in policy_recs
                       if str(p.get("attached_to", "")).startswith(("user:", "role:"))})

    all_path = os.path.join(ct_dir, "cloudtrail-all.json")
    usage_map = usage_from_all(all_path)

    out = os.path.join("reports", run_id)
    os.makedirs(out, exist_ok=True)
    results = {}
    for ent in entities:
        usage = usage_map.get(ent)
        if usage is None and ent.startswith("user:"):
            usage = usage_from_peruser(ct_dir, ent.split(":", 1)[1])  # 구버전 호환
        usage = usage or {"used": set(), "arns": set()}
        R = analyze_entity(ent, policy_recs, usage)
        results[ent] = R
        safe = ent.replace(":", "-")
        json.dump(R["policy"], open(os.path.join(out, f"{safe}-rightsized-policy.json"), "w"),
                  ensure_ascii=False, indent=2)

    open(os.path.join(out, "report.md"), "w").write(render_md(run_id, results))
    print(f"[✓] 역산 완료 — 엔티티 {len(entities)}개")
    for ent, R in results.items():
        nu = sum(1 for r in R["table"] if r["status"] == "USED")
        nun = sum(1 for r in R["table"] if r["status"] == "UNUSED")
        print(f"    - {ent}: 실사용 {len(R['used'])}종 / 사용 {nu} / 미관측 {nun} / ARN {len(R['arns'])}")
    print(f"[✓] 출력: {out}/report.md , <entity>-rightsized-policy.json")


if __name__ == "__main__":
    main()
