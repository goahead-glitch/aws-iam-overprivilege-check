# IAM 과권한 역산 — CloudShell 실행 가이드 (읽기 전용)

IAM 사용자+역할의 **과권한을 점검**하고, CloudTrail 실사용 이력으로 **최소권한 정책을 역산**한다. 모든 단계는 읽기 전용(list/get/lookup)이며, 정책 변경·삭제는 산출물(제안)일 뿐 사람이 검토 후 직접 적용한다. 실제 실행 결과는 [results/](../results/) 참고.

## 0. 스캔 사용자(주체) 준비 — 한 번만

관리자 권한 있는 사람이 콘솔/CLI로 **읽기전용 스캔 사용자**를 만든다.
(아래는 생성 명령 예시 — 점검 대상이 아니라 스캔용 ID 부트스트랩이다.)

```bash
# 읽기전용 정책 생성
aws iam create-policy \
  --policy-name SecScanReadOnly \
  --policy-document file://scripts/scan-user-readonly-policy.json

# 사용자 생성 + 정책 부착
aws iam create-user --user-name sec-scan
aws iam attach-user-policy --user-name sec-scan \
  --policy-arn arn:aws:iam::<ACCOUNT_ID>:policy/SecScanReadOnly

# (선택) 콘솔 로그인 프로필 만들고 → 그 사용자로 콘솔 로그인 후 CloudShell 사용
#  CloudShell 은 로그인한 콘솔 신원을 그대로 쓰므로 액세스키 없이 동작한다.
```

AWS 관리형 `SecurityAudit` 정책으로 대체해도 대부분 커버되지만, `cloudtrail:LookupEvents` 포함 여부가 리전/시점마다 다를 수 있어 위 커스텀 정책을 권장.

## 1. CloudShell 부트스트랩

콘솔에서 **sec-scan 사용자로 로그인 → 서울 리전 → CloudShell** 열기. 이 저장소의 `scripts/`를 CloudShell에 업로드한 뒤:

```bash
chmod +x scripts/cloudtrail_rightsize.sh
pip install --quiet boto3   # CloudShell 기본 제공, 없을 때만
```

## 2. 실행 (처음부터 끝까지)

```bash
export AWS_DEFAULT_REGION=ap-northeast-2
export RUN_ID=run-$(date +%Y%m%d)-rightsize
export LOOKBACK_DAYS=7

# (1) IAM 인벤토리 수집 — 사용자+역할의 정책 문서
python3 scripts/collect_iam_inventory.py iam-over

# (2) 구조 과권한 점검 — 와일드카드/Admin/권한상승
python3 scripts/analyze_iam_overperm.py iam-over ${RUN_ID}-overperm

# (3) CloudTrail 실사용 수집 (사용자+역할, userIdentity 귀속, 페이지네이션)
./scripts/cloudtrail_rightsize.sh

# (4) 최소권한 역산
python3 scripts/analyze_iam_rightsize.py iam-out/${RUN_ID} iam-over ${RUN_ID}
```

## 3. 산출물

- `reports/${RUN_ID}-overperm/report.md` — 구조 과권한 FAIL 표
- `reports/${RUN_ID}/report.md` — 역산 결과(부여 vs 실사용, 제거후보, 와일드카드→ARN)
- `reports/${RUN_ID}/<entity>-rightsized-policy.json` — 제안 최소권한 정책

## 4. 한국어 해석 (오프라인 캐시, Bedrock 없이)

`analyze_iam_overperm.py`는 내부적으로 `interpret.py` + `report.py`를 호출해 finding에 한국어 설명을 붙인다. `cache_seed.json`에 사람이 미리 채워둔 시드만 사용하며, Bedrock은 호출하지 않는다. 캐시에 없는 check_id는 "(미해석)"으로 표시된다. Bedrock 연동은 `docs/architecture.md`에 설계로만 기록되어 있고 구현하지 않았다.

## 주의(역산 한계 — 자동 삭제 금지)
- 조회창이 짧으면(위 예시는 7일) 저빈도 정당 권한(월간 잡 등)이 '미관측'으로 보일 수 있음 → 제거 전 확인.
- `iam:PassRole`·`sts:AssumeRole`은 CloudTrail에 잘 안 잡혀 **미관측이어도 자동 보존**(🟣 표시).
- `s3:PutObject` 등 데이터 이벤트는 trail에 data event 로깅을 켜야 보임 → 미관측이어도 보존 검토.
- read(Get/List/Describe)는 🔵로 구분 — 삭제보다 유지 권장.
