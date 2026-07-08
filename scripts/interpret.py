"""
해석: 정규화 레코드에 한국어 해석(explanation_ko/recommendation_ko/false_positive_likelihood)을 부착.

순서 (docs/architecture.md §데이터 흐름):
  1) 캐시(cache_seed.json)에서 cache_key(check_id) 조회 → hit 면 재사용
  2) miss 면 미해석으로 표시

이번 프로젝트는 Bedrock을 실제로 호출하지 않았다. cache_seed.json은 사람이 미리 작성한
시드이며, 이 저장소에는 실제로 나온 iamx:* finding 7종의 해석만 담겨 있다.
Bedrock 연동은 docs/architecture.md에 설계로만 기록되어 있고 미구현 상태다.
"""
from __future__ import annotations
import json
import os
from typing import Optional

_HERE = os.path.dirname(os.path.abspath(__file__))
CACHE_PATH = os.path.join(_HERE, "cache_seed.json")

_MISS = {
    "title_ko": "",
    "explanation_ko": "(미해석 — 캐시에 없는 check_id)",
    "recommendation_ko": "(미해석 — 캐시에 없는 check_id)",
    "false_positive_likelihood": "unknown",
}


def _load_json(path: str) -> dict:
    if not os.path.exists(path):
        return {}
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)
    return {k: v for k, v in data.items() if not k.startswith("_")}


def load_cache() -> dict:
    """시드 캐시 로드."""
    return _load_json(CACHE_PATH)


def interpret(records: list[dict], cache: Optional[dict] = None) -> tuple[list[dict], dict]:
    if cache is None:
        cache = load_cache()
    stats = {"hit": 0, "miss": 0}
    out = []
    for r in records:
        key = r.get("cache_key")
        entry = cache.get(key)
        if entry:
            stats["hit"] += 1
        else:
            stats["miss"] += 1
            entry = _MISS
        merged = dict(r)
        merged["explanation_ko"] = entry.get("explanation_ko", "")
        merged["recommendation_ko"] = entry.get("recommendation_ko", "")
        merged["false_positive_likelihood"] = entry.get("false_positive_likelihood", "unknown")
        merged["title_ko"] = entry.get("title_ko", "")
        out.append(merged)
    return out, stats
