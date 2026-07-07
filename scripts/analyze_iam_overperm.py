#!/usr/bin/env python3
"""
IAM 과권한(구조 기반) 분석 — 이력 길이와 무관하게 "설계상 과한 권한"을 본다.
입력 디렉터리(iam-over/):
  policies-all.json   : [{name,arn,type,attached_to,document}]  (관리형+인라인)
  credential-report.csv (선택)
  admin-entities.json   (선택, list-entities-for-policy AdministratorAccess)
출력: reports/<run_id>/ (FAIL 표). 시간 기반 '미사용'은 다루지 않음(Access Advisor 별도).
"""
from __future__ import annotations
import csv
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from interpret import interpret
from report import render_markdown, render_html

# 권한 상승에 직접 쓰이는 IAM/STS 액션
ESCALATION = {
    "iam:createpolicyversion", "iam:setdefaultpolicyversion",
    "iam:attachuserpolicy", "iam:attachrolepolicy", "iam:attachgrouppolicy",
    "iam:putuserpolicy", "iam:putrolepolicy", "iam:putgrouppolicy",
    "iam:createaccesskey", "iam:createloginprofile", "iam:updateloginprofile",
    "iam:updateassumerolepolicy", "iam:addusertogroup",
}
PASSROLE = {"iam:passrole", "sts:assumerole"}

# 신호 → (check_id, severity, 우선순위)
SIG = {
    "FULL_ADMIN":      ("iamx:full_admin",          "CRITICAL", 0),
    "PRIV_ESCALATION": ("iamx:privilege_escalation", "HIGH",    1),
    "RISKY_PASSROLE":  ("iamx:risky_passrole",       "HIGH",    2),
    "WILDCARD_ACTION": ("iamx:wildcard_action",      "MEDIUM",  3),
    "WILDCARD_RESRC":  ("iamx:wildcard_resource",    "MEDIUM",  4),
}


def _as_list(x):
    return [] if x is None else (x if isinstance(x, list) else [x])


def classify(doc) -> set:
    s = set()
    for st in _as_list((doc or {}).get("Statement")):
        if str(st.get("Effect", "")).lower() != "allow":
            continue
        acts = [str(a).lower() for a in _as_list(st.get("Action"))]
        res = [str(r) for r in _as_list(st.get("Resource"))]
        aw = any(a == "*" or a.endswith(":*") for a in acts)
        af = "*" in acts
        rw = "*" in res
        if af and rw:
            s.add("FULL_ADMIN")
        if aw:
            s.add("WILDCARD_ACTION")
        if rw:
            s.add("WILDCARD_RESRC")
        if any(a in PASSROLE for a in acts) and (rw or not res):
            s.add("RISKY_PASSROLE")
        if "iam:*" in acts or af or (ESCALATION & set(acts)):
            s.add("PRIV_ESCALATION")
    return s


def from_policies(path, run_id):
    recs = []
    if not os.path.exists(path):
        return recs
    for p in json.load(open(path, encoding="utf-8")):
        sigs = classify(p.get("document"))
        if not sigs:
            continue
        worst = min(sigs, key=lambda x: SIG[x][2])
        cid, sev, _ = SIG[worst]
        ptype = p.get("type", "managed")
        target = p.get("attached_to", "-")
        recs.append(_rec(run_id, cid, sev,
                         f"[{ptype}] 정책 '{p.get('name')}' ({','.join(sorted(sigs))})",
                         target if target != "-" else p.get("arn", "-")))
    return recs


def from_admin(path, run_id):
    recs = []
    if not os.path.exists(path):
        return recs
    d = json.load(open(path, encoding="utf-8"))
    for u in d.get("PolicyUsers", []):
        recs.append(_rec(run_id, "iamx:admin_attached", "HIGH",
                         "AdministratorAccess 직접 부여", f"user:{u.get('UserName')}"))
    for r in d.get("PolicyRoles", []):
        recs.append(_rec(run_id, "iamx:admin_attached", "HIGH",
                         "AdministratorAccess 직접 부여", f"role:{r.get('RoleName')}"))
    for g in d.get("PolicyGroups", []):
        recs.append(_rec(run_id, "iamx:admin_attached", "HIGH",
                         "AdministratorAccess 직접 부여", f"group:{g.get('GroupName')}"))
    return recs


def from_credreport(path, run_id):
    recs = []
    if not os.path.exists(path):
        return recs
    for row in csv.DictReader(open(path, encoding="utf-8")):
        user = row.get("user", "")
        is_root = user == "<root_account>"
        mfa = row.get("mfa_active") == "true"
        if is_root:
            if row.get("access_key_1_active") == "true" or row.get("access_key_2_active") == "true":
                recs.append(_rec(run_id, "iamx:root_access_key", "CRITICAL",
                                 "루트 계정 액세스키 존재", "root"))
            if not mfa:
                recs.append(_rec(run_id, "iamx:root_mfa_disabled", "CRITICAL",
                                 "루트 계정 MFA 미설정", "root"))
            continue
        if row.get("password_enabled") == "true" and not mfa:
            recs.append(_rec(run_id, "iamx:user_mfa_disabled", "HIGH",
                             "콘솔 사용자 MFA 미설정", f"user:{user}"))
    return recs


def _rec(run_id, cid, sev, title, resource):
    return {
        "account_id": "-", "run_id": run_id, "tool": "iam-overperm",
        "check_id": cid, "title": title, "resource": resource,
        "region": "-", "vpc_id": "iam", "severity": sev, "status": "FAIL",
        "workflow_state": "NEW", "compare_key": f"iamx|{cid}|{resource}",
        "cache_key": cid, "raw_ref": "iam-over",
    }


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    d = args[0] if args else "iam-over"
    run_id = args[1] if len(args) > 1 else "iam-overperm"
    recs = (from_policies(os.path.join(d, "policies-all.json"), run_id)
            + from_admin(os.path.join(d, "admin-entities.json"), run_id)
            + from_credreport(os.path.join(d, "credential-report.csv"), run_id))
    interp, stats = interpret(recs, use_bedrock="--bedrock" in sys.argv)
    out = os.path.join("reports", run_id); os.makedirs(out, exist_ok=True)
    json.dump(interp, open(os.path.join(out, "normalized.json"), "w"), ensure_ascii=False, indent=2)
    open(os.path.join(out, "report.md"), "w").write(render_markdown(interp, run_id))
    open(os.path.join(out, "report.html"), "w").write(render_html(interp, run_id))
    print(f"[✓] IAM 과권한 FAIL {len([r for r in interp if r['status']=='FAIL'])} | {stats}")
    print(f"[✓] 출력: {out}/report.md , report.html")


if __name__ == "__main__":
    main()
