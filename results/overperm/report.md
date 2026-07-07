# 보안 점검 리포트 — run `run-20260626-rightsize-overperm`

> 모든 점검은 읽기 전용. 조치는 추천이며 실제 변경은 사람이 수행한다.

## 요약

- 전체 항목: 11  |  FAIL: 11  |  PASS: 0  |  WARN: 0
- FAIL 심각도: 🔴 CRITICAL 2, 🟠 HIGH 6, 🟡 MEDIUM 3, 🟢 LOW 0
- VPC(환경)별 FAIL: `iam` 11

## finding별 위험도·조치 (FAIL)

| 심각도 | check_id | 항목 | 대상 | VPC | 위험 이유 | 조치 | 오탐 |
|---|---|---|---|---|---|---|---|
| 🔴 CRITICAL | `iamx:full_admin` | 전체 관리자급 정책 (*:* ) | `user:Admin_User` | `iam` | 이 정책은 Action과 Resource가 모두 와일드카드(*)라 사실상 모든 권한을 허용한다(=AdministratorAccess급). 해당 주체나 자격증명이 유출되면 계정 전체가 장악된다. 최소권한 원칙에 정면으로 위배된다. | 1) 이 정책이 실제로 필요한 동작 식별(Access Advisor 참고) 2) 직무 기반 최소권한 정책으로 재설계 3) 영향 범위 확인 후 교체 4) 변경 후 동작 재점검. (영향 범위 확인 후 적용) | low |
| 🔴 CRITICAL | `iamx:full_admin` | 전체 관리자급 정책 (*:* ) | `user:eks` | `iam` | 이 정책은 Action과 Resource가 모두 와일드카드(*)라 사실상 모든 권한을 허용한다(=AdministratorAccess급). 해당 주체나 자격증명이 유출되면 계정 전체가 장악된다. 최소권한 원칙에 정면으로 위배된다. | 1) 이 정책이 실제로 필요한 동작 식별(Access Advisor 참고) 2) 직무 기반 최소권한 정책으로 재설계 3) 영향 범위 확인 후 교체 4) 변경 후 동작 재점검. (영향 범위 확인 후 적용) | low |
| 🟠 HIGH | `iamx:privilege_escalation` | 권한 상승 가능 정책 | `user:infra` | `iam` | 이 정책에는 자기 권한을 키울 수 있는 IAM 액션(예: AttachUserPolicy/PutRolePolicy/CreatePolicyVersion/CreateAccessKey/UpdateAssumeRolePolicy 또는 iam:*)이 들어 있다. 낮은 권한 주체라도 이런 액션으로 스스로를 관리자급으로 끌어올릴 수 있어 위험하다. | 1) 해당 IAM 변경 액션이 꼭 필요한지 검토 2) 필요한 경우 Resource/Condition으로 대상 제한(권한 경계 적용) 3) 사용자/앱 주체에서는 제거 4) 변경 후 확인. (영향 범위 확인 후 적용) | medium |
| 🟠 HIGH | `iamx:risky_passrole` | 광범위 PassRole/AssumeRole | `role:aws-ec2-spot-fleet-tagging-role` | `iam` | iam:PassRole 또는 sts:AssumeRole이 Resource 제한 없이(또는 *) 허용돼 있다. PassRole이 넓으면 더 높은 권한의 역할을 컴퓨트(EC2/Lambda 등)에 붙여 권한을 상승시킬 수 있다. | 1) PassRole/AssumeRole 대상 역할을 구체 ARN으로 한정 2) iam:PassedToService 등 Condition 추가 3) 불필요하면 제거 4) 변경 후 확인. (영향 범위 확인 후 적용) | medium |
| 🟠 HIGH | `iamx:admin_attached` | AdministratorAccess 직접 부여 | `user:eks` | `iam` | 사용자/역할/그룹에 AWS 관리형 AdministratorAccess가 직접 붙어 있어 무제한 권한을 가진다. 해당 자격증명 유출 시 계정 전체가 위험하다. 직무에 필요한 범위만 부여해야 한다. | 1) Access Advisor로 실제 사용 서비스 확인 2) 최소권한 정책 설계 3) 영향 범위 확인 후 Admin 분리·교체 4) 변경 후 재점검. (영향 범위 확인 후 적용) | low |
| 🟠 HIGH | `iamx:admin_attached` | AdministratorAccess 직접 부여 | `user:Admin_User` | `iam` | 사용자/역할/그룹에 AWS 관리형 AdministratorAccess가 직접 붙어 있어 무제한 권한을 가진다. 해당 자격증명 유출 시 계정 전체가 위험하다. 직무에 필요한 범위만 부여해야 한다. | 1) Access Advisor로 실제 사용 서비스 확인 2) 최소권한 정책 설계 3) 영향 범위 확인 후 Admin 분리·교체 4) 변경 후 재점검. (영향 범위 확인 후 적용) | low |
| 🟠 HIGH | `iamx:user_mfa_disabled` | 콘솔 사용자 MFA 미설정 | `user:infra` | `iam` | 콘솔 로그인이 가능한 IAM 사용자에 MFA가 없어 비밀번호 유출 시 침입이 가능하다. 권한이 큰 사용자일수록 피해가 크다. | 1) 대상 사용자 식별 2) MFA 등록 강제 정책 적용 3) 미설정자 콘솔 접근 임시 제한 4) 등록 확인. (영향 범위 확인 후 적용) | low |
| 🟠 HIGH | `iamx:user_mfa_disabled` | 콘솔 사용자 MFA 미설정 | `user:k8s` | `iam` | 콘솔 로그인이 가능한 IAM 사용자에 MFA가 없어 비밀번호 유출 시 침입이 가능하다. 권한이 큰 사용자일수록 피해가 크다. | 1) 대상 사용자 식별 2) MFA 등록 강제 정책 적용 3) 미설정자 콘솔 접근 임시 제한 4) 등록 확인. (영향 범위 확인 후 적용) | low |
| 🟡 MEDIUM | `iamx:wildcard_action` | 와일드카드 Action 정책 | `user:infra` | `iam` | Action에 와일드카드(* 또는 svc:*)가 있어 의도보다 넓은 동작이 허용된다. 서비스 전체 권한이 부여되면 그 안의 위험한 동작까지 함께 열린다. | 1) 실제 필요한 개별 Action만 열거로 교체 2) 읽기 전용이면 Get/List/Describe로 한정 3) 변경 후 동작 확인. (영향 범위 확인 후 적용) | medium |
| 🟡 MEDIUM | `iamx:wildcard_resource` | 와일드카드 Resource 정책 | `user:k8s` | `iam` | Resource가 *로 열려 모든 리소스에 해당 동작이 적용된다. 특정 버킷/테이블/역할만 필요한데 전체로 열면 사고 시 피해 범위가 계정 전체로 번진다. | 1) Resource를 구체 ARN(버킷/테이블/역할 등)으로 한정 2) 네임/태그 조건 활용 3) 변경 후 확인. (영향 범위 확인 후 적용) | medium |
| 🟡 MEDIUM | `iamx:wildcard_resource` | 와일드카드 Resource 정책 | `user:sec-scan` | `iam` | Resource가 *로 열려 모든 리소스에 해당 동작이 적용된다. 특정 버킷/테이블/역할만 필요한데 전체로 열면 사고 시 피해 범위가 계정 전체로 번진다. | 1) Resource를 구체 ARN(버킷/테이블/역할 등)으로 한정 2) 네임/태그 조건 활용 3) 변경 후 확인. (영향 범위 확인 후 적용) | medium |
