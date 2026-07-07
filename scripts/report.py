"""
리포트: 해석된 레코드 → 요약 + finding별 위험도·조치 표 (MD / HTML).
환경 구분은 VPC 기준(05 문서). 산출물 형식은 04_실행계획.md §3.
"""
from __future__ import annotations
import html
from collections import Counter

SEV_ORDER = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3, "INFORMATIONAL": 4, "UNKNOWN": 5}
SEV_BADGE = {"CRITICAL": "🔴", "HIGH": "🟠", "MEDIUM": "🟡", "LOW": "🟢", "UNKNOWN": "⚪"}


def _sev_key(r):
    return SEV_ORDER.get(str(r.get("severity", "UNKNOWN")).upper(), 9)


def _summary(records):
    fails = [r for r in records if r.get("status") == "FAIL"]
    sev_counts = Counter(str(r.get("severity", "UNKNOWN")).upper() for r in fails)
    status_counts = Counter(r.get("status") for r in records)
    vpc_counts = Counter(r.get("vpc_id", "-") for r in fails)
    return fails, sev_counts, status_counts, vpc_counts


def render_markdown(records, run_id="demo-run") -> str:
    fails, sev, status, vpc = _summary(records)
    L = []
    L.append(f"# 보안 점검 리포트 — run `{run_id}`\n")
    L.append("> 모든 점검은 읽기 전용. 조치는 추천이며 실제 변경은 사람이 수행한다.\n")

    L.append("## 요약\n")
    L.append(f"- 전체 항목: {len(records)}  |  FAIL: {len(fails)}  |  PASS: {status.get('PASS',0)}  |  WARN: {status.get('WARN',0)}")
    sev_line = ", ".join(f"{SEV_BADGE.get(k,'')} {k} {sev.get(k,0)}" for k in ["CRITICAL","HIGH","MEDIUM","LOW"])
    L.append(f"- FAIL 심각도: {sev_line}")
    if vpc:
        L.append("- VPC(환경)별 FAIL: " + ", ".join(f"`{k}` {v}" for k, v in vpc.items()))
    L.append("")

    L.append("## finding별 위험도·조치 (FAIL)\n")
    L.append("| 심각도 | check_id | 항목 | 대상 | VPC | 위험 이유 | 조치 | 오탐 |")
    L.append("|---|---|---|---|---|---|---|---|")
    for r in sorted(fails, key=_sev_key):
        sevu = str(r.get("severity","")).upper()
        L.append("| {b} {sev} | `{cid}` | {title} | `{res}` | `{vpc}` | {why} | {rec} | {fp} |".format(
            b=SEV_BADGE.get(sevu, ""), sev=sevu,
            cid=r.get("check_id",""),
            title=(r.get("title_ko") or r.get("title","")).replace("|", "\\|"),
            res=str(r.get("resource","")).replace("|","\\|"),
            vpc=r.get("vpc_id","-"),
            why=str(r.get("explanation_ko","")).replace("|","\\|"),
            rec=str(r.get("recommendation_ko","")).replace("|","\\|"),
            fp=r.get("false_positive_likelihood","-"),
        ))
    L.append("")
    return "\n".join(L)


def render_html(records, run_id="demo-run") -> str:
    fails, sev, status, vpc = _summary(records)
    color = {"CRITICAL":"#ef4444","HIGH":"#f97316","MEDIUM":"#eab308","LOW":"#22c55e","UNKNOWN":"#9ca3af"}
    rows = []
    for r in sorted(fails, key=_sev_key):
        sevu = str(r.get("severity","")).upper()
        rows.append(
            "<tr>"
            f"<td><span class='sev' style='background:{color.get(sevu,'#9ca3af')}'>{html.escape(sevu)}</span></td>"
            f"<td><code>{html.escape(str(r.get('check_id','')))}</code></td>"
            f"<td>{html.escape(r.get('title_ko') or r.get('title',''))}</td>"
            f"<td><code>{html.escape(str(r.get('resource','')))}</code></td>"
            f"<td><code>{html.escape(str(r.get('vpc_id','-')))}</code></td>"
            f"<td>{html.escape(str(r.get('explanation_ko','')))}</td>"
            f"<td>{html.escape(str(r.get('recommendation_ko','')))}</td>"
            f"<td>{html.escape(str(r.get('false_positive_likelihood','-')))}</td>"
            "</tr>"
        )
    sev_chips = "".join(
        f"<span class='chip' style='border-color:{color.get(k)}'>{k} {sev.get(k,0)}</span>"
        for k in ["CRITICAL","HIGH","MEDIUM","LOW"]
    )
    vpc_chips = "".join(f"<span class='chip'>{html.escape(str(k))}: {v}</span>" for k, v in vpc.items())
    return f"""<!doctype html><html lang="ko"><head><meta charset="utf-8">
<title>보안 점검 리포트 — {html.escape(run_id)}</title>
<style>
body{{font-family:system-ui,'Apple SD Gothic Neo',sans-serif;margin:32px;color:#1f2937;line-height:1.5}}
h1{{font-size:22px}} .muted{{color:#6b7280}}
.chip{{display:inline-block;border:1px solid #d1d5db;border-radius:999px;padding:2px 10px;margin:2px;font-size:13px}}
table{{border-collapse:collapse;width:100%;margin-top:14px;font-size:13.5px}}
th,td{{border:1px solid #e5e7eb;padding:8px 10px;text-align:left;vertical-align:top}}
th{{background:#f9fafb}} code{{background:#f3f4f6;padding:1px 5px;border-radius:4px;font-size:12px}}
.sev{{color:#fff;border-radius:6px;padding:2px 8px;font-size:12px;font-weight:700}}
</style></head><body>
<h1>보안 점검 리포트 <span class="muted">— run {html.escape(run_id)}</span></h1>
<p class="muted">모든 점검은 읽기 전용. 조치는 추천이며 실제 변경은 사람이 수행한다.</p>
<p>전체 {len(records)} · FAIL {len(fails)} · PASS {status.get('PASS',0)} · WARN {status.get('WARN',0)}</p>
<p>{sev_chips}</p>
<p class="muted">VPC(환경)별 FAIL: {vpc_chips or '-'}</p>
<table><thead><tr>
<th>심각도</th><th>check_id</th><th>항목</th><th>대상</th><th>VPC</th><th>위험 이유</th><th>조치</th><th>오탐</th>
</tr></thead><tbody>
{''.join(rows)}
</tbody></table></body></html>"""
