# 클라우드 보안 점검 — AWS IAM 과권한 점검 & 최소권한 재설계

AWS 계정의 IAM 과권한을 읽기 전용으로 점검하고, 실제 사용 이력을 근거로 최소권한 정책을 역산한 프로젝트다. (2026년 6월, 2주간 수행)

## 왜 했나

팀 프로젝트를 진행하면서 배포·운영 편의를 위해 Admin급 권한을 별 고민 없이 붙여 쓰는 경우를 여러 번 봤다. "일단 되게 하자"로 부여한 권한이 프로젝트가 끝난 뒤에도 그대로 남아있는 경우가 많았고, 정작 "이 계정에 누가 뭘 할 수 있는가"를 객관적으로 답하기는 어려웠다. 이 프로젝트는 그 질문에 데이터로 답해보려는 시도다 — 부여된 권한과 실제로 쓰인 권한을 CloudTrail 로그로 대조해서, 감으로 판단하지 않고 최소권한을 역산했다.

## 실행 결과 요약

### 1. IAM 최소권한 역산 (`run-20260626-rightsize`)

CloudTrail 실사용 이력(7일, lookup-events)으로 IAM 엔티티 7개(사용자 5, 역할 2)의 부여 권한 대비 실사용 권한을 대조했다.

| 엔티티 | 부여 패턴 | 실사용 | 미관측(제거 후보) | 관측 ARN |
|---|---|---|---|---|
| `user:Admin_User` | 1 | 1 | 0 | 0 |
| `user:eks` | 1 | 1 | 0 | 0 |
| `user:infra` | 12 | **1** | 11 | 446 |
| `user:k8s` | 2 | 0 | 2 | 1 |
| `user:sec-scan` | 15 | **0** | 15 | 0 |
| `role:aws-ec2-spot-fleet-tagging-role` | 10 | 3 | 6 | 0 |
| `role:lamdaaaa-role-3w4ttpc4` | 3 | 0 | 3 | 0 |

대표 사례:
- **`user:infra`** — `IAMFullAccess`(`iam:*` 등 11개 패턴) + `AWSCloudShellFullAccess` 두 정책이 부여됐지만, 7일간 실제로 쓰인 건 `cloudshell:*` 계열 9개 액션(166회 호출)뿐이었다. `IAMFullAccess`의 11개 패턴은 전부 미관측.
- **`user:sec-scan`** — IAM 인벤토리 조회 15개 액션이 부여됐지만, 7일 관측 기간 동안 단 하나도 호출되지 않았다.

엔티티별 제안 최소권한 정책 JSON 7개를 산출했다 → [results/rightsize/](results/rightsize/)

### 2. IAM 과권한 위험 점검 (`run-20260626-rightsize-overperm`)

정책 문서 구조 분석(와일드카드, Admin 직접부여, 권한상승 가능성, MFA)으로 11건의 과권한 위험을 식별했다.

| 심각도 | 건수 | 예시 |
|---|---|---|
| 🔴 CRITICAL | 2 | 전체 관리자급 정책(`*:*`) — `Admin_User`, `eks` |
| 🟠 HIGH | 6 | 권한 상승 가능 정책, 광범위 PassRole, AdministratorAccess 직접 부여 ×2, MFA 미설정 ×2 |
| 🟡 MEDIUM | 3 | 와일드카드 Action/Resource 정책 |

각 항목에 위험 이유·조치 방향·오탐 가능성을 붙였다 → [results/overperm/](results/overperm/)

## 산출물

```
docs/architecture.md        전체 설계(Security Hub 중심) — 실행 완료/미완료 구분 표시
docs/troubleshooting.md     Prowler를 Lambda로 돌리려다 실패한 기록 (T001~T007) → ECS Fargate 전환 결론
results/rightsize/          IAM 최소권한 역산: report.md/html + 제안 정책 JSON 7개
results/overperm/           IAM 과권한 위험 점검: report.md/html + normalized.json
scripts/                    실제 실행에 쓰인 수집·분석 스크립트
```

## 점검 원칙과 한계

- **모든 점검은 읽기 전용.** 리소스를 변경·삭제하는 동작은 없다. 스캔 전용 읽기 전용 IAM 사용자(`SecScanReadOnly`)로만 실행했고, 정책 축소·MFA 강제 등 실제 조치는 사람이 리포트를 검토한 뒤 수동으로 적용하는 것을 원칙으로 했다.
- **한계 — 조회 기간이 짧다.** CloudTrail 조회창을 7일로 잡았기 때문에, 월간 배치 작업처럼 저빈도로 쓰이는 정당한 권한이 "미관측(제거 후보)"으로 잘못 보일 수 있다. 특히 read(Get/List/Describe), `iam:PassRole`, S3 데이터 이벤트는 짧은 조회창에서 누락되기 쉽다. 그래서 `iam:PassRole`/`sts:AssumeRole`은 미관측이어도 자동으로 보존 대상으로 표시했다. 제거 후보는 실제 삭제 전 반드시 재확인이 필요하다.

## 트러블슈팅 요약

Prowler(CLI 보안 스캐너)를 Lambda로 서버리스화하려다 컨테이너 이미지 형식, Lambda Layer 250MB 한도, Python 버전 불일치, 의존성 누락을 순서대로 만났다(T001~T007). 최종 결론은 "Prowler는 Lambda용 도구가 아니다" — 무거운 CLI 스캐너는 ECS Fargate(셸 환경 완전, 용량 제한 없음)로 돌리고, Lambda는 가벼운 정규화·해석 로직에만 쓰는 것으로 설계를 전환했다. 상세 기록은 [docs/troubleshooting.md](docs/troubleshooting.md).

## 로드맵 (설계만 완료, 미실행)

- **Prowler → Security Hub 집계 → Bedrock Claude 한국어 해석** 파이프라인 — 스캐폴딩·오프라인 글루 코드는 작성했으나 AWS 상에서 실제 실행하지 않았다. 현재 결과의 한국어 해석은 Bedrock 실호출이 아니라 사람이 미리 써 둔 캐시(`scripts/cache_seed.json`)로 대체한 것이다.
- **Kube-bench(k8s CIS 벤치마크) / rbac-tool(RBAC 유효 권한 추적)** — 매니페스트·런북 작성 완료, 클러스터에서 실행하지 않았다.
- **EKS vs EC2 자체설치 k8s 비교** — 통제 변수(k8s 1.34, 동일 워크로드)까지는 설계했으나 Kube-bench 실행 전까지는 비교할 데이터가 없다.

설계 상세는 [docs/architecture.md](docs/architecture.md) 참고.
