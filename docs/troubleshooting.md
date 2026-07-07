# 트러블슈팅

> **교훈 (왜 Security Hub 중심 설계로 갔나).** 아래 T-001~T-007은 Prowler를 Lambda(서버리스)로 돌리려다 부딪힌 기록이다. 결론: **Prowler는 Lambda용으로 설계된 도구가 아니다** — 컨테이너 이미지 형식, Layer 250MB 한도, 의존성 누락, Python 버전 벽이 반복된다. 그래서 이번 설계는 Prowler를 **풀 셸(CloudShell/EC2)에서 그대로 실행**하고, 집계는 **Security Hub** 관리형 서비스에 맡기는 방식으로 전환했다. 이 기록은 그 전환의 근거로 보존한다. 설계 상세는 [architecture.md](architecture.md) 참고.

## T-001. Prowler Lambda 컨테이너 이미지 형식 오류

**발생 단계**: 0단계 — Prowler ECR 이미지 빌드·푸시 후 Lambda 연결 시

**증상**
```
The image manifest, config or layer media type for the source image
<ACCOUNT_ID>.dkr.ecr.ap-northeast-2.amazonaws.com/prowler-scanner@sha256:...
is not supported.
```

**원인**
- Prowler 공식 이미지(`public.ecr.aws/prowler-cloud/prowler:latest`)가 OCI 형식으로 배포됨
- AWS Lambda 컨테이너는 **Docker schema v2** 형식만 지원
- Mac(ARM) 환경에서 `docker buildx`로 빌드 시 멀티플랫폼 매니페스트가 생성되어 Lambda가 인식 불가

**시도한 방법 (실패)**
1. `docker buildx build --platform linux/amd64` — 동일 오류
2. `docker buildx build --platform linux/amd64 --output type=docker` — 동일 오류
3. Lambda 베이스 이미지 + pip 설치 방식 — 동일 오류
4. `docker inspect`로 로컬 확인 시도 → 로컬에 이미지 없음 (`--output type=docker`로 빌드 시 로컬 미저장)

**결론**: 컨테이너 이미지 방식 포기 → **Lambda Layer 방식으로 전환**

**전환 이유**
- 컨테이너 이미지 형식 호환 문제가 반복 발생
- 로컬에 이미지가 남지 않아 디버깅도 어려움
- Prowler를 Lambda Layer로 패키징하는 방식이 더 단순하고 안정적

**대안: Lambda Layer 방식**
- Prowler pip 설치 → zip → S3 → Lambda Layer 등록
- Lambda 본체는 handler 코드만 (가벼운 zip)
- Layer S3 경유 업로드: 250MB 제한 적용

## T-002. Prowler Lambda Layer pip 설치 의존성 충돌

**발생 단계**: 0단계 — Lambda Layer 패키징 시

**증상**
```
ERROR: Cannot install prowler because these package versions have conflicting dependencies.
prowler 3.x.x depends on shodan==1.x.x
ResolutionImpossible
```

**원인**
- `--platform manylinux2014_x86_64 --only-binary=:all:` 옵션 사용 시
- shodan 패키지의 특정 버전이 manylinux 바이너리로 제공되지 않아 의존성 해결 실패

**해결 방법**: `--platform` 옵션 제거 + `shodan` 제외하고 설치

## T-003. prowler IAM 사용자 권한 부족 (반복)

**발생 단계**: 0단계 — Lambda Layer 등록 시

**증상**
```
AccessDeniedException: User: arn:aws:iam::<ACCOUNT_ID>:user/prowler is not authorized
to perform: lambda:PublishLayerVersion
```

**원인**
- `prowler` IAM 사용자에 권한 없이 액세스키만 발급한 상태
- S3 PutObject, lambda:PublishLayerVersion 등 작업마다 권한 부족 오류 반복

**근본 해결**: 작업마다 권한 추가하는 대신 **필요한 권한을 한 번에 정리해서 붙이기**

필요한 권한 목록:
- S3: PutObject, GetObject, ListBucket (스캔 버킷)
- Lambda: PublishLayerVersion, GetLayerVersion, UpdateFunctionCode, UpdateFunctionConfiguration, GetFunction, InvokeFunction
- ECR: GetAuthorizationToken, BatchCheckLayerAvailability, PutImage, InitiateLayerUpload, UploadLayerPart, CompleteLayerUpload
- IAM: PassRole (Lambda 실행 역할 전달용)

## T-004. Lambda에서 Prowler CLI subprocess 실행 불가

**발생 단계**: 1단계 — Prowler Lambda 테스트 실행 시

**증상**
```
{"error": "[Errno 2] No such file or directory: 'prowler'"}
{"error": "[Errno 2] No such file or directory: '/opt/python/bin/prowler'"}
{"errorMessage": "[Errno 2] No such file or directory: 'find'"}
```

**근본 원인**
- Lambda 실행 환경은 보안상 극도로 제한된 컨테이너
- `find`, `ls`, `which` 등 기본 shell 명령어도 없음
- `/bin`, `/usr/bin` 대부분 비어있음
- Prowler는 원래 CLI 도구라 subprocess 호출 방식이 Lambda와 근본적으로 안 맞음

**현업에서 Prowler 자동화 방법**
1. EC2 / ECS Fargate — shell 환경 완전, CLI 그대로 실행 (가장 흔함)
2. Prowler SaaS — 계정 연결만 하면 자동 스캔 (직접 구현 아님)
3. Lambda + Prowler Python SDK — subprocess 대신 Python import로 실행

**해결 방향 (선택 중)**
- A. ECS Fargate로 전환 — shell 완전, Prowler CLI 그대로, 설정 복잡
- B. Lambda + Prowler Python SDK — Lambda 유지, Python import로 실행

## T-005. Lambda Layer Python 버전 불일치 (3.13 vs 3.11)

**발생 단계**: 1단계 — Prowler Python SDK import 시도 시

**증상**
- Layer 내 파일이 `.cpython-313.pyc`로 컴파일됨
- Lambda 런타임은 python3.11인데 3.13으로 컴파일된 패키지 로드 불가

**원인**
- 로컬 Mac의 Python(3.13)으로 `pip install` → 3.13 기준으로 패키징됨
- Lambda python3.11 런타임과 버전 불일치

**해결 방법**
Lambda 런타임과 동일한 환경(python3.11 + linux/amd64)에서 Docker로 패키징:

```bash
rm -rf python prowler-layer.zip

docker run --platform linux/amd64 \
  -v $(pwd):/output \
  public.ecr.aws/lambda/python:3.11 \
  pip install prowler -t /output/python

zip -r prowler-layer.zip python/
```

## T-006. Lambda Layer 용량 초과 (435MB > 250MB 한도)

**발생 단계**: 1단계 — prowler-layer.zip 생성 시

**증상**
```
prowler-layer.zip 435MB (Lambda Layer 한도 250MB 초과)
```

**원인**
- Prowler가 AWS 외 Azure·GCP·Vercel 등 모든 프로바이더 의존성을 포함
- 전체 설치 시 435MB로 한도 초과

**해결 방법**
`--no-deps`로 prowler 본체만 설치 후 AWS 필수 의존성만 추가:
```bash
pip install prowler boto3 --no-deps -t /output
pip install botocore pydantic alive-progress colorama python-dateutil -t /output
```

## T-007. Prowler Lambda Layer 근본적 용량 한계

**발생 단계**: 1단계 — Prowler Python SDK 의존성 설치 반복

**증상**
- `requests` 없음 → 추가 → `yaml` 없음 → 추가 → 의존성 끝없이 누락
- `prowler[aws]` 전체 설치 시 다시 436MB (250MB 한도 초과)
- `--no-deps`로 줄이면 런타임에 모듈 누락 오류 반복

**근본 원인 (중요)**
- **Prowler는 Lambda용으로 설계된 도구가 아님**
- AWS 전체를 스캔하는 무거운 CLI 도구라 의존성 포함 시 250MB 초과 불가피
- Layer 방식으로는 "용량 줄이면 모듈 누락 / 다 넣으면 용량 초과"의 딜레마에서 벗어날 수 없음

**결론: Lambda + Prowler 조합 포기 → ECS Fargate로 전환 (설계)**

**전환 후 구조 (설계)**
- 스캔(Prowler): ECS Fargate Task (shell 완전, 용량 제한 없음, CLI 그대로)
- 정규화·해석·리포트: Lambda 유지
- 오케스트레이션: Step Functions (Fargate Task + Lambda 혼합)

**교훈**
- 무거운 CLI 보안 도구(Prowler 등)는 Lambda보다 컨테이너 실행 환경(Fargate/ECS)이 적합
- Lambda는 가벼운 변환·분석 로직에만 사용

---

# Security Hub 중심 설계 운영 시 자주 막히는 곳 (설계 단계에서 예상되는 이슈, 미실행)

## T-101. Security Hub Integrations에 Prowler가 안 뜸

**증상**: Security Hub 콘솔 Integrations에서 "Prowler"를 검색해도 목록에 안 나옴.

**원인**
- Security Hub CSPM 콘솔은 **현재 로그인한 리전에서 지원/활성화된 통합만** 보여준다.
- (a) 콘솔 리전이 ap-northeast-2가 아니거나, (b) 그 리전에 **Security Hub CSPM**(새 "Security Hub"가 아니라 CSPM)이 안 켜졌거나, (c) 통합을 아직 구독(enable)하지 않은 상태.

**해결 (CLI로 직접 구독 — 콘솔 UI 우회, 루트/관리자 1회)**
```bash
aws securityhub enable-import-findings-for-product \
  --region ap-northeast-2 \
  --product-arn arn:aws:securityhub:ap-northeast-2::product/prowler/prowler
# 확인
aws securityhub list-enabled-products-for-import --region ap-northeast-2
```
- 권한: `securityhub:EnableImportFindingsForProduct` 필요 → sec-readonly 말고 셋업 권한 주체(루트)로 1회.
- 구독 안 된 상태로 `--security-hub` 업로드 시 BatchImportFindings가 "product not subscribed"로 실패.
- 노이즈·비용 절감: 스캔 때 `--send-sh-only-fails`로 FAIL만 업로드 가능.

## T-102. Bedrock 모델 접근 (서울 리전)

**주의**: 해석에 쓸 모델 ID가 ap-northeast-2에서 접근 가능해야 함.
- 확정 사용 모델: `anthropic.claude-sonnet-4-20250514-v1:0` (서울 접근 확인). 콘솔 Bedrock → Model access에서 활성 상태 확인.

## T-103. Prowler 플래그 버전차

**증상**: `--services`/`--service`, `--compliance cis_3.0_aws` 등이 버전마다 다름.
**해결**: `prowler aws --help`로 설치 버전 기준 플래그 확인 후 스캔 스크립트 조정.

## T-104. 해석 캐시 키(check_id) 불일치

**증상**: `cache_seed.json`에 분명히 있는데 캐시 미스로 뜸.
**원인**: Prowler 버전마다 check_id가 달라 cache_key가 안 맞음.
**해결**: 실제 스캔 결과의 check_id를 확인해 `scripts/cache_seed.json` 키를 맞추거나, 미스 항목만 Bedrock으로 보완.

## T-105. kube-bench 이미지/마운트/벤치마크 버전차

**증상**: Job이 안 뜨거나 일부 점검이 누락.
**해결**: 이미지 태그(`aquasec/kube-bench:vX.Y.Z`)·벤치마크(`eks-1.x`)·hostPath 마운트를 배포판/버전에 맞춰 공식 매니페스트로 교차 확인.
