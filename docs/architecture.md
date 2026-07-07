# 아키텍처 — Security Hub 중심 설계

> **이 문서는 설계 문서다.** 아래에 기술된 Security Hub·Prowler·Bedrock 파이프라인은 AWS 상에서 아직 실행되지 않았다.
> 실제로 실행되어 결과가 나온 부분은 **IAM 과권한 점검**(CloudTrail 기반 별도 스크립트)뿐이며, 그 결과는 [results/rightsize](../results/rightsize/), [results/overperm](../results/overperm/)에 있다. 실행 여부는 [현재 진행 상태](#현재-진행-상태)에 단계별로 표시했다.

## 방향

이번 설계의 핵심은 "소프트웨어 파이프라인을 빌드"가 아니라 **"AWS 관리형 보안 서비스를 설계·운용"**하는 것이다. 직접 짠 글루 코드(정규화·집계·리포트)를 최소화하고, Security Hub가 집계·중복제거·심각도·대시보드를 담당한다. 무거운 CLI 스캐너(Prowler)는 Lambda에 넣지 않고 풀 셸 환경(CloudShell/EC2)에서 그대로 돌린다. AI(Bedrock)는 파이프라인의 중심이 아니라 finding에 한국어 해석을 붙이는 얇은 부가층이다. (Lambda로 시도했다가 포기한 과정은 [troubleshooting.md](troubleshooting.md) 참고.)

## 점검 대상

| 대상 | 설명 |
|---|---|
| AWS 계정 / IAM | 계정 보안 설정 + IAM 과도 권한 점검 (**1순위, 실행 완료**) |
| AWS EKS | 관리형 컨트롤플레인, 퍼블릭 서브넷, 단일 AZ. 웹서비스 운영 |
| EC2 자체설치 k8s | kubeadm 기반, 온프레미스 역할. 동일 웹서비스 운영 (설계만, 미실행) |

EKS와 온프레는 k8s 1.34 + 동일 워크로드로 통제 변수를 고정하도록 설계했다(EKS vs 온프레 비교는 백로그, 미실행).

## 핵심 결정 요약

- **성격**: 일회성 데모/포트폴리오, 재현성 최우선, 클라우드 엔지니어 관점
- **실행**: On-demand 수동 실행 (상시/cron 아님)
- **범위(설계)**: 점검 → Security Hub 집계 → 한국어 해석 → 리포트까지. 자동 승인·자동 적용 없음
- **수정 방식**: 사람이 리포트를 보고 수동 적용
- **Before/After(설계)**: run을 2번 실행해 Security Hub의 finding 상태 변화로 비교

모든 점검은 읽기 전용. 리소스를 변경·삭제하는 동작은 절대 금지. 자격증명은 코드/문서에 하드코딩하지 않고 환경변수·AWS 프로파일·IAM 역할로만 참조한다.

## 스캐너 구성 (설계)

스캐너는 각자 알맞은 곳에서 그대로 실행하고, 결과를 Security Hub(또는 S3)에 합류시킨 지점부터 공통 처리하도록 설계했다.

| 도구 | 무엇을 보나 | 실행 위치 | 상태 |
|---|---|---|---|
| **IAM 네이티브 점검** (직접 구현 스크립트) | 미사용 권한·부여 권한 대비 실사용·구조적 과권한 | CloudShell (AWS CLI + boto3) | **실행 완료** — [results/](../results/) |
| Prowler | AWS 계정/IAM/설정(CSPM), 500+ 체크, CIS AWS Foundations Benchmark(cis_3.0_aws) | CloudShell 또는 EC2 | 설계, 미실행 |
| Kube-bench | k8s 내부 CIS(노드·CP) | 클러스터 안 Job | 설계, 미실행 |
| rbac-tool | "누가 무엇을 할 수 있나" 유효 권한 | kubectl (관리 단말) | 설계, 미실행 |

## 데이터 흐름 (설계)

① Prowler(read-only) → `--security-hub` → AWS Security Hub, 원본은 S3 `/raw/{run_id}`
② IAM 네이티브 점검(Access Analyzer·Access Advisor·credential report) → S3 `/raw/{run_id}/iam`
③ 해석 글루 — Security Hub finding 조회 → check_id 캐시 확인 → miss만 Bedrock 1회 → S3 `/interpreted`
④ 리포트 — 요약 + finding별 위험도·조치 표 → S3 `/reports`

Security Hub가 정규화·집계를 대신하므로, 별도 정규화 Lambda는 두지 않는 것으로 설계했다. Before/After는 시스템이 루프를 돌리는 게 아니라, 사람이 추천대로 수정한 뒤 run을 한 번 더 실행해 Security Hub finding 상태(NEW→RESOLVED 등)를 비교하는 방식으로 설계했다.

실제로 실행된 IAM 과권한 점검(`scripts/collect_iam_inventory.py`, `scripts/analyze_iam_overperm.py`, `scripts/cloudtrail_rightsize.sh`, `scripts/analyze_iam_rightsize.py`)은 위 파이프라인 중 ②와 유사한 역할을 하되, Security Hub·Prowler 없이 CloudTrail 실사용 이력만으로 독립 실행되었다. 해석 글루(`scripts/interpret.py`, `scripts/report.py`)는 Bedrock 없이 사람이 미리 써 둔 `scripts/cache_seed.json` 캐시만으로 한국어 리포트를 만들었다 — Bedrock 실호출은 아직 없었다.

## 권한 모델 (읽기 전용 원칙, 설계)

| 주체 | 권한 |
|---|---|
| 점검 실행 단말(CloudShell/EC2) | `SecurityAudit` + `ViewOnlyAccess` (AWS 관리형, read-only) |
| Security Hub 연동 | `securityhub:BatchImportFindings` |
| 해석 글루 | S3 읽기/쓰기 + Bedrock `InvokeModel` |

점검 대상 리소스에 대한 쓰기/변경 권한은 부여하지 않는 것을 원칙으로 설계했다 — 도구는 읽고 알려주기만 한다. 실제로 실행된 IAM 과권한 점검도 이 원칙을 지켜 읽기 전용 스캔 사용자(`SecScanReadOnly` — `scripts/scan-user-readonly-policy.json`)로만 수행했다.

## 점검 범위 — IAM 과권한 4대 축

IAM 과권한은 Prowler 체크(설계) + AWS 네이티브 기능(실행)을 함께 4개 축으로 보도록 설계했고, 이 중 아래 4축은 CloudTrail·IAM 정책 파싱 스크립트로 **실제 실행**되었다.

| # | 점검 축 | 무엇을 찾나 | 데이터 소스 | 상태 |
|---|---|---|---|---|
| 1 | 와일드카드 정책 | `Action:"*"` 또는 `Resource:"*"`, `iam:PassRole *` 등 과대 정책 | IAM 정책 문서 파싱 | 실행 완료 |
| 2 | AdministratorAccess 부여 대상 | Admin 정책이 붙은 사용자/역할/그룹 목록 | IAM 정책 문서 파싱 | 실행 완료 |
| 3 | 미사용 권한/주체 | 부여됐지만 CloudTrail에 실사용 이력이 없는 액션 | CloudTrail lookup-events (7일) | 실행 완료 |
| 4 | 마지막 사용 시점 | 부여됐지만 실제로 안 쓰는 서비스 권한 | CloudTrail lookup-events (7일) | 실행 완료 |

> 원래 설계는 3·4축을 IAM Access Analyzer(unused access)·Access Advisor로 보는 것이었으나, 실제 실행에서는 CloudTrail 7일 조회 기반 자체 스크립트로 대체했다. 결과와 한계는 [results/rightsize/report.md](../results/rightsize/report.md) 상단 경고문 참고.

### 과권한 판정 가이드

| 신호 | 위험도 | 조치 방향 |
|---|---|---|
| `*:*` 또는 AdministratorAccess 직접 부여 | Critical/High | 직무별 최소권한 정책으로 교체 |
| `Resource:"*"` 인라인 정책 | High | 리소스 ARN 범위 한정 |
| PassRole/AssumeRole 광범위 허용 | High | 대상 역할·조건(Condition) 제한 |
| 미사용 역할·액세스키 | Medium | 비활성화 후 모니터링 → 삭제 권고 |
| MFA 미설정(콘솔 사용자) | High | MFA 강제 |

모든 "조치"는 추천이다. 권한 축소·삭제는 영향이 크므로 항상 "영향 범위 확인 후 적용" 주의가 붙는다. 실제 변경은 사람이 한다.

## 현재 진행 상태

| 단계 | 내용 | 상태 |
|---|---|---|
| Phase 0 | 사전조건(Security Hub·Bedrock·sec-readonly·S3) | 진행 중(미완) |
| Phase 1 | Prowler → Security Hub로 AWS/IAM 관통 | 설계·스캐폴딩 완료, AWS 실행 대기 |
| Phase 1.5 | IAM 과권한 네이티브 점검(CloudTrail 기반) | **실행 완료** — [results/](../results/) |
| Phase 2 | Kube-bench·rbac-tool | 매니페스트·런북 작성 완료, 실행 보류 |
| 이후 | EKS vs 온프레 비교, Trivy, 서버리스화 | 백로그(설계 문서만 보존) |

## 로드맵 / 다음 단계 (미실행)

1. Phase 0 사전조건 중 이미 된 것/안 된 것 확인 (Security Hub·Bedrock 활성화 여부)
2. Prowler 실제 스캔 + Security Hub 연동 (Phase 1)
3. Kube-bench·rbac-tool 실행 (Phase 2) — EKS vs 온프레 비교
4. Bedrock을 실제로 호출하는 한국어 해석 (현재는 `scripts/cache_seed.json` 오프라인 캐시로만 대체)
