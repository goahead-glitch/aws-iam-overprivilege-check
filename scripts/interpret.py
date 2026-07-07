"""
해석: 정규화 레코드에 한국어 해석(explanation_ko/recommendation_ko/false_positive_likelihood)을 부착.

순서 (03_프롬프트.md §캐시 연동):
  1) 캐시(cache_seed.json + cache_learned.json) 에서 cache_key(check_id) 조회 → hit 면 재사용
  2) miss 면:
       - use_bedrock=False → 미해석 표시(오프라인)
       - use_bedrock=True  → Bedrock 1회 호출 → 결과를 cache_learned.json 에 누적 → 사용

캐시 분리: cache_seed.json(사람이 쓴 시드, 손대지 않음) / cache_learned.json(Bedrock이 채운 것).
Bedrock 호출은 AWS 자격증명 + bedrock:InvokeModel + 모델 접근이 필요하다(CloudShell 또는 프로파일).
"""
from __future__ import annotations
import json
import os
from typing import Optional

_HERE = os.path.dirname(os.path.abspath(__file__))
CACHE_PATH = os.path.join(_HERE, "cache_seed.json")
LEARNED_PATH = os.path.join(_HERE, "cache_learned.json")

_MISS = {
    "title_ko": "",
    "explanation_ko": "(미해석 — Bedrock 보완 대상)",
    "recommendation_ko": "(미해석 — Bedrock 보완 대상)",
    "false_positive_likelihood": "unknown",
}


def _load_json(path: str) -> dict:
    if not os.path.exists(path):
        return {}
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)
    return {k: v for k, v in data.items() if not k.startswith("_")}


def load_cache() -> dict:
    """시드 + 학습 캐시 병합 (학습이 시드를 덮어쓰지 않도록 시드 우선)."""
    merged = dict(_load_json(LEARNED_PATH))
    merged.update(_load_json(CACHE_PATH))   # 시드 우선
    return merged


def _save_learned(entries: dict) -> None:
    if not entries:
        return
    existing = _load_json(LEARNED_PATH)
    existing.update(entries)
    with open(LEARNED_PATH, "w", encoding="utf-8") as fh:
        json.dump(existing, fh, ensure_ascii=False, indent=2)


def call_bedrock(check_id: str, title: str, severity: str,
                 service: str = "iam") -> Optional[dict]:
    """Bedrock Claude 1회 호출 → {explanation_ko, recommendation_ko, false_positive_likelihood}.
    boto3 + bedrock-runtime 필요. 실패 시 None(미스 유지)."""
    try:
        import boto3
        from prompt import SYSTEM_PROMPT, build_user_message, MODEL_ID, REGION
    except Exception as e:  # boto3 미설치/임포트 실패
        print(f"  [bedrock] 사용 불가: {e}")
        return None
    try:
        client = boto3.client("bedrock-runtime", region_name=REGION)
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 512,
            "temperature": 0,
            "system": SYSTEM_PROMPT,
            "messages": [
                {"role": "user", "content": build_user_message(check_id, title, severity, service)}
            ],
        }
        resp = client.invoke_model(modelId=MODEL_ID, body=json.dumps(body))
        payload = json.loads(resp["body"].read())
        text = payload["content"][0]["text"].strip()
        data = json.loads(text)   # 프롬프트가 JSON 객체만 출력하도록 강제됨
        return {
            "title_ko": data.get("title_ko", ""),
            "explanation_ko": data.get("explanation_ko", ""),
            "recommendation_ko": data.get("recommendation_ko", ""),
            "false_positive_likelihood": data.get("false_positive_likelihood", "unknown"),
        }
    except Exception as e:
        print(f"  [bedrock] check_id={check_id} 호출 실패: {e}")
        return None


def interpret(records: list[dict], cache: Optional[dict] = None,
              use_bedrock: bool = False) -> tuple[list[dict], dict]:
    if cache is None:
        cache = load_cache()
    stats = {"hit": 0, "miss": 0, "bedrock": 0}
    learned: dict = {}
    out = []
    for r in records:
        key = r.get("cache_key")
        entry = cache.get(key)
        if entry:
            stats["hit"] += 1
        else:
            stats["miss"] += 1
            entry = None
            if use_bedrock and key not in learned:
                entry = call_bedrock(key, r.get("title", ""), r.get("severity", ""),
                                     r.get("tool", "iam"))
                if entry:
                    cache[key] = entry
                    learned[key] = entry
                    stats["bedrock"] += 1
            elif use_bedrock:
                entry = learned.get(key)
            if not entry:
                entry = _MISS
        merged = dict(r)
        merged["explanation_ko"] = entry.get("explanation_ko", "")
        merged["recommendation_ko"] = entry.get("recommendation_ko", "")
        merged["false_positive_likelihood"] = entry.get("false_positive_likelihood", "unknown")
        merged["title_ko"] = entry.get("title_ko", "")
        out.append(merged)
    _save_learned(learned)
    return out, stats


if __name__ == "__main__":
    import sys
    from normalize import normalize_file
    src = sys.argv[1] if len(sys.argv) > 1 else "samples/prowler-ocsf-sample.json"
    use_bed = "--bedrock" in sys.argv
    recs = normalize_file(src, "demo-run")
    interp, stats = interpret(recs, use_bedrock=use_bed)
    print(json.dumps(interp, ensure_ascii=False, indent=2))
    print("STATS:", stats, file=sys.stderr)
