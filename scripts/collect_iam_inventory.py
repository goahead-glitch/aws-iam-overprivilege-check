#!/usr/bin/env python3
"""
IAM 인벤토리 수집 (읽기 전용) — 새 계정에서 처음부터.
사용자 + 역할의 inline/관리형 정책 문서를 모아 analyze_iam_overperm.py /
analyze_iam_rightsize.py 가 먹는 policies-all.json 형태로 저장한다.

생성물(<out_dir>/, 기본 iam-over/):
  policies-all.json    : [{name,arn,type,attached_to,document}]  (entity×policy 1행씩)
  credential-report.csv
  admin-entities.json  : AdministratorAccess 부여 대상

안전: list/get/generate 만 호출 — IAM/리소스를 일절 수정하지 않는다(읽기 전용).
자격증명은 boto3 기본 체인(AWS_PROFILE/환경변수/CloudShell 역할)으로만.

사용:
  export AWS_DEFAULT_REGION=ap-northeast-2
  python3 scanners/iam-native/collect_iam_inventory.py [out_dir]
"""
from __future__ import annotations
import json
import os
import sys
import time

try:
    import boto3
except ImportError:
    sys.exit("boto3 가 필요합니다 (CloudShell 기본 제공). pip install boto3")

SKIP_ROLE_PATH = "/aws-service-role/"   # 서비스 연결 역할은 수정 불가 → 제외


def _doc_of_managed(iam, arn, default_ver):
    v = iam.get_policy_version(PolicyArn=arn, VersionId=default_ver)
    return v["PolicyVersion"]["Document"]


def collect_entity(iam, kind, name, arn):
    """kind in {user, role}. → policy 레코드 리스트."""
    recs = []
    label = f"{kind}:{name}"
    if kind == "user":
        inline_names = iam.list_user_policies(UserName=name)["PolicyNames"]
        get_inline = lambda pn: iam.get_user_policy(UserName=name, PolicyName=pn)["PolicyDocument"]
        attached = iam.list_attached_user_policies(UserName=name)["AttachedPolicies"]
    else:
        inline_names = iam.list_role_policies(RoleName=name)["PolicyNames"]
        get_inline = lambda pn: iam.get_role_policy(RoleName=name, PolicyName=pn)["PolicyDocument"]
        attached = iam.list_attached_role_policies(RoleName=name)["AttachedPolicies"]

    for pn in inline_names:
        recs.append({"name": pn, "arn": f"{kind}/{name}/{pn}", "type": "inline",
                     "attached_to": label, "document": get_inline(pn)})
    for ap in attached:
        parn = ap["PolicyArn"]
        pol = iam.get_policy(PolicyArn=parn)["Policy"]
        doc = _doc_of_managed(iam, parn, pol["DefaultVersionId"])
        recs.append({"name": ap["PolicyName"], "arn": parn, "type": "managed",
                     "attached_to": label, "document": doc})
    return recs


def credential_report(iam, out_dir):
    try:
        iam.generate_credential_report()
        for _ in range(6):
            try:
                rep = iam.get_credential_report()
                open(os.path.join(out_dir, "credential-report.csv"), "wb").write(rep["Content"])
                return True
            except iam.exceptions.CredentialReportNotPresentException:
                time.sleep(3)
            except iam.exceptions.CredentialReportNotReadyException:
                time.sleep(3)
    except Exception as e:
        print(f"  (경고) credential report 실패: {e}")
    return False


def main():
    out_dir = sys.argv[1] if len(sys.argv) > 1 else "iam-over"
    os.makedirs(out_dir, exist_ok=True)

    sts = boto3.client("sts")
    ident = sts.get_caller_identity()
    print(f"[*] 계정 {ident['Account']}  주체 {ident['Arn']}")

    iam = boto3.client("iam")
    recs = []

    print("[1] 사용자 열거")
    for page in iam.get_paginator("list_users").paginate():
        for u in page["Users"]:
            print(f"    - user:{u['UserName']}")
            recs += collect_entity(iam, "user", u["UserName"], u["Arn"])

    print("[2] 역할 열거 (서비스 연결 역할 제외)")
    for page in iam.get_paginator("list_roles").paginate():
        for r in page["Roles"]:
            if r["Path"].startswith(SKIP_ROLE_PATH):
                continue
            print(f"    - role:{r['RoleName']}")
            recs += collect_entity(iam, "role", r["RoleName"], r["Arn"])

    json.dump(recs, open(os.path.join(out_dir, "policies-all.json"), "w"),
              ensure_ascii=False, indent=2)
    print(f"[3] policies-all.json → {len(recs)}개 (entity×policy) 레코드")

    print("[4] AdministratorAccess 부여 대상")
    admin = iam.list_entities_for_policy(PolicyArn="arn:aws:iam::aws:policy/AdministratorAccess")
    json.dump({k: admin.get(k, []) for k in ("PolicyUsers", "PolicyRoles", "PolicyGroups")},
              open(os.path.join(out_dir, "admin-entities.json"), "w"),
              ensure_ascii=False, indent=2, default=str)

    print("[5] credential report")
    credential_report(iam, out_dir)

    print(f"[✓] 수집 완료 → {out_dir}/  (account={ident['Account']})")
    print(f"    다음: python3 glue/analyze_iam_overperm.py {out_dir} <run_id>   # 구조 점검")


if __name__ == "__main__":
    main()
