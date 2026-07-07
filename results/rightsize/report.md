# IAM 최소권한 역산 리포트 — run `run-20260626-rightsize`

> CloudTrail 실사용 이력(lookup-events)으로 부여 권한을 역산. 모두 읽기 전용 분석이며, **제거·치환은 제안일 뿐 실제 변경은 사람이 검토 후 수행**한다.

> ⚠️ 조회창이 짧으면 저빈도 정당 권한이 '미관측'으로 보일 수 있다. 특히 read(Get/List/Describe), `iam:PassRole`(소비 서비스 이벤트에 묻힘), S3 데이터이벤트는 누락되기 쉬움.

## 요약

| 엔티티 | 실사용 액션 | 부여 패턴 | 사용 | 미관측(제거후보) | 관측 ARN |
|---|---|---|---|---|---|
| `role:aws-ec2-spot-fleet-tagging-role` | 3 | 10 | 3 | 6 | 0 |
| `role:lamdaaaa-role-3w4ttpc4` | 0 | 3 | 0 | 3 | 0 |
| `user:Admin_User` | 24 | 1 | 1 | 0 | 0 |
| `user:eks` | 2 | 1 | 1 | 0 | 0 |
| `user:infra` | 166 | 12 | 1 | 11 | 446 |
| `user:k8s` | 25 | 2 | 0 | 2 | 1 |
| `user:sec-scan` | 0 | 15 | 0 | 15 | 0 |

## `role:aws-ec2-spot-fleet-tagging-role`

| 정책 | 유형 | Sid | 부여 패턴 | 종류 | 상태 | 실관측 액션 |
|---|---|---|---|---|---|---|
| AmazonEC2SpotFleetTaggingRole | managed | (no-sid) | `ec2:DescribeImages` | 🔵read | ✅ 사용 | ec2:DescribeImages |
| AmazonEC2SpotFleetTaggingRole | managed | (no-sid) | `ec2:DescribeSubnets` | 🔵read | ✅ 사용 | ec2:DescribeSubnets |
| AmazonEC2SpotFleetTaggingRole | managed | (no-sid) | `ec2:RequestSpotInstances` | 🟠write | ⬜ 미관측 | — |
| AmazonEC2SpotFleetTaggingRole | managed | (no-sid) | `ec2:TerminateInstances` | 🟠write | ⬜ 미관측 | — |
| AmazonEC2SpotFleetTaggingRole | managed | (no-sid) | `ec2:DescribeInstanceStatus` | 🔵read | ✅ 사용 | ec2:DescribeInstanceStatus |
| AmazonEC2SpotFleetTaggingRole | managed | (no-sid) | `ec2:CreateTags` | 🟠write | ⬜ 미관측 | — |
| AmazonEC2SpotFleetTaggingRole | managed | (no-sid) | `ec2:RunInstances` | 🟠write | ⬜ 미관측 | — |
| AmazonEC2SpotFleetTaggingRole | managed | (no-sid) | `iam:PassRole` | 🟣blind | 🟣 미관측·보존 | — |
| AmazonEC2SpotFleetTaggingRole | managed | (no-sid) | `elasticloadbalancing:RegisterInstancesWithLoadBalancer` | 🟠write | ⬜ 미관측 | — |
| AmazonEC2SpotFleetTaggingRole | managed | (no-sid) | `elasticloadbalancing:RegisterTargets` | 🟠write | ⬜ 미관측 | — |

**제안 최소권한 정책**: ✅만 남기고 와일드카드 `Resource:*`는 관측 ARN으로 좁힌 `role-aws-ec2-spot-fleet-tagging-role-rightsized-policy.json` 참조.

## `role:lamdaaaa-role-3w4ttpc4`

| 정책 | 유형 | Sid | 부여 패턴 | 종류 | 상태 | 실관측 액션 |
|---|---|---|---|---|---|---|
| AWSLambdaBasicExecutionRole-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx | managed | (no-sid) | `logs:CreateLogGroup` | 🟠write | ⬜ 미관측 | — |
| AWSLambdaBasicExecutionRole-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx | managed | (no-sid) | `logs:CreateLogStream` | 🟠write | ⬜ 미관측 | — |
| AWSLambdaBasicExecutionRole-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx | managed | (no-sid) | `logs:PutLogEvents` | 🟠write | ⬜ 미관측 | — |

**제안 최소권한 정책**: ✅만 남기고 와일드카드 `Resource:*`는 관측 ARN으로 좁힌 `role-lamdaaaa-role-3w4ttpc4-rightsized-policy.json` 참조.

## `user:Admin_User`

| 정책 | 유형 | Sid | 부여 패턴 | 종류 | 상태 | 실관측 액션 |
|---|---|---|---|---|---|---|
| AdministratorAccess | managed | (no-sid) | `*` | 🟠write | ✅ 사용 | autoscaling:DescribeAutoScalingGroups, cloudwatch:DescribeAlarms, ec2:DescribeAccountAttributes, ec2:DescribeAddresses, ec2:DescribeAvailabilityZones, ec2:DescribeCapacityReservations, ec2:DescribeHosts, ec2:DescribeInstanceStatus, ec2:DescribeInstances, ec2:DescribeKeyPairs, ec2:DescribeLaunchTemplates, ec2:DescribeManagedPrefixLists, ec2:DescribePlacementGroups, ec2:DescribeRegions, ec2:DescribeSecurityGroups, ec2:DescribeSnapshots, ec2:DescribeTags, ec2:DescribeVolumeStatus, ec2:DescribeVolumes, ec2:DescribeVpcs, elasticloadbalancing:DescribeLoadBalancers, notifications:ListNotificationHubs, signin:CheckMfa, signin:ConsoleLogin |

**제안 최소권한 정책**: ✅만 남기고 와일드카드 `Resource:*`는 관측 ARN으로 좁힌 `user-Admin_User-rightsized-policy.json` 참조.

## `user:eks`

| 정책 | 유형 | Sid | 부여 패턴 | 종류 | 상태 | 실관측 액션 |
|---|---|---|---|---|---|---|
| AdministratorAccess | managed | (no-sid) | `*` | 🟠write | ✅ 사용 | eks:DescribeCluster, sts:GetCallerIdentity |

**제안 최소권한 정책**: ✅만 남기고 와일드카드 `Resource:*`는 관측 ARN으로 좁힌 `user-eks-rightsized-policy.json` 참조.

## `user:infra`

| 정책 | 유형 | Sid | 부여 패턴 | 종류 | 상태 | 실관측 액션 |
|---|---|---|---|---|---|---|
| IAMFullAccess | managed | (no-sid) | `iam:*` | 🟠write | ⬜ 미관측 | — |
| IAMFullAccess | managed | (no-sid) | `organizations:DescribeAccount` | 🔵read | ⬜ 미관측 | — |
| IAMFullAccess | managed | (no-sid) | `organizations:DescribeOrganization` | 🔵read | ⬜ 미관측 | — |
| IAMFullAccess | managed | (no-sid) | `organizations:DescribeOrganizationalUnit` | 🔵read | ⬜ 미관측 | — |
| IAMFullAccess | managed | (no-sid) | `organizations:DescribePolicy` | 🔵read | ⬜ 미관측 | — |
| IAMFullAccess | managed | (no-sid) | `organizations:ListChildren` | 🔵read | ⬜ 미관측 | — |
| IAMFullAccess | managed | (no-sid) | `organizations:ListParents` | 🔵read | ⬜ 미관측 | — |
| IAMFullAccess | managed | (no-sid) | `organizations:ListPoliciesForTarget` | 🔵read | ⬜ 미관측 | — |
| IAMFullAccess | managed | (no-sid) | `organizations:ListRoots` | 🔵read | ⬜ 미관측 | — |
| IAMFullAccess | managed | (no-sid) | `organizations:ListPolicies` | 🔵read | ⬜ 미관측 | — |
| IAMFullAccess | managed | (no-sid) | `organizations:ListTargetsForPolicy` | 🔵read | ⬜ 미관측 | — |
| AWSCloudShellFullAccess | managed | (no-sid) | `cloudshell:*` | 🟠write | ✅ 사용 | cloudshell:CreateEnvironment, cloudshell:CreateSession, cloudshell:DeleteSession, cloudshell:DescribeEnvironments, cloudshell:GetEnvironmentStatus, cloudshell:PutCredentials, cloudshell:RedeemCode, cloudshell:SendHeartBeat, cloudshell:StartEnvironment |

**제안 최소권한 정책**: ✅만 남기고 와일드카드 `Resource:*`는 관측 ARN으로 좁힌 `user-infra-rightsized-policy.json` 참조.

관측 리소스 ARN:

- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group-rule/sgr-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group/sg-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group/sg-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group/sg-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group/sg-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group/sg-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group/sg-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group/sg-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group/sg-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group/sg-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group/sg-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group/sg-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group/sg-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group/sg-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group/sg-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group/sg-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group/sg-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group/sg-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group/sg-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group/sg-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group/sg-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group/sg-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group/sg-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group/sg-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group/sg-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group/sg-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group/sg-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group/sg-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group/sg-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group/sg-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group/sg-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group/sg-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group/sg-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group/sg-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group/sg-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group/sg-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group/sg-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group/sg-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group/sg-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group/sg-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group/sg-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group/sg-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group/sg-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group/sg-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group/sg-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group/sg-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group/sg-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group/sg-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group/sg-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group/sg-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:security-group/sg-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:subnet/subnet-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:subnet/subnet-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:subnet/subnet-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:subnet/subnet-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:subnet/subnet-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:subnet/subnet-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:subnet/subnet-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:subnet/subnet-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:subnet/subnet-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:subnet/subnet-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:subnet/subnet-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:subnet/subnet-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:subnet/subnet-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:subnet/subnet-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:subnet/subnet-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:subnet/subnet-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:subnet/subnet-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:subnet/subnet-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:subnet/subnet-xxxxxxxxxxxxxxxxx`
- `arn:aws:ec2:ap-northeast-2:111122223333:subnet/subnet-xxxxxxxxxxxxxxxxx`
- `arn:aws:ecr:ap-northeast-2:111122223333:repository/app-api`
- `arn:aws:ecr:ap-northeast-2:111122223333:repository/app-frontend`
- `arn:aws:ecr:ap-northeast-2:111122223333:repository/app-inventory`
- `arn:aws:ecr:ap-northeast-2:111122223333:repository/app-order`
- `arn:aws:ecr:ap-northeast-2:111122223333:repository/app-payment`
- `arn:aws:ecr:ap-northeast-2:111122223333:repository/app-product`
- `arn:aws:ecr:ap-northeast-2:111122223333:repository/app-user`
- `arn:aws:ecs:ap-northeast-2:111122223333:cluster/app-db-migration`
- `arn:aws:ecs:ap-northeast-2:111122223333:container/app-db-migration/xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
- `arn:aws:ecs:ap-northeast-2:111122223333:task-definition/app-db-migration:1`
- `arn:aws:ecs:ap-northeast-2:111122223333:task-definition/app-db-migration:2`
- `arn:aws:ecs:ap-northeast-2:111122223333:task-definition/app-db-migration:3`
- `arn:aws:ecs:ap-northeast-2:111122223333:task-definition/app-db-migration:4`
- `arn:aws:ecs:ap-northeast-2:111122223333:task-definition/app-db-migration:5`
- `arn:aws:ecs:ap-northeast-2:111122223333:task-definition/app-db-migration:6`
- `arn:aws:ecs:ap-northeast-2:111122223333:task-definition/app-db-migration:7`
- `arn:aws:ecs:ap-northeast-2:111122223333:task-definition/app-db-migration:8`
- `arn:aws:ecs:ap-northeast-2:111122223333:task-definition/app-db-migration:9`
- `arn:aws:ecs:ap-northeast-2:111122223333:task/app-db-migration/xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`
- `arn:aws:eks::aws:cluster-access-policy/AmazonEKSAdminPolicy`
- `arn:aws:eks::aws:cluster-access-policy/AmazonEKSClusterAdminPolicy`
- `arn:aws:eks::aws:cluster-access-policy/AmazonEKSEditPolicy`
- `arn:aws:eks:ap-northeast-2:111122223333:access-entry/app-eks/role/111122223333/app-eks-karpenter-node/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
- `arn:aws:eks:ap-northeast-2:111122223333:access-entry/app-eks/role/111122223333/app-eks-karpenter-node/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
- `arn:aws:eks:ap-northeast-2:111122223333:access-entry/app-eks/role/111122223333/app-eks-karpenter-node/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
- `arn:aws:eks:ap-northeast-2:111122223333:access-entry/app-eks/role/111122223333/app-eks-karpenter-node/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
- `arn:aws:eks:ap-northeast-2:111122223333:access-entry/app-eks/role/111122223333/app-eks-karpenter-node/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
- `arn:aws:eks:ap-northeast-2:111122223333:access-entry/app-eks/role/111122223333/app-eks-karpenter-node/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
- `arn:aws:eks:ap-northeast-2:111122223333:access-entry/app-eks/role/111122223333/app-eks-karpenter-node/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
- `arn:aws:eks:ap-northeast-2:111122223333:access-entry/app-eks/role/111122223333/app-eks-karpenter-node/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
- `arn:aws:eks:ap-northeast-2:111122223333:access-entry/app-eks/role/111122223333/argocd-role/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
- `arn:aws:eks:ap-northeast-2:111122223333:access-entry/app-eks/role/111122223333/argocd-role/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
- `arn:aws:eks:ap-northeast-2:111122223333:access-entry/app-eks/role/111122223333/argocd-role/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
- `arn:aws:eks:ap-northeast-2:111122223333:access-entry/app-eks/role/111122223333/argocd-role/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
- `arn:aws:eks:ap-northeast-2:111122223333:access-entry/app-eks/role/111122223333/argocd-role/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
- `arn:aws:eks:ap-northeast-2:111122223333:access-entry/app-eks/role/111122223333/argocd-role/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
- `arn:aws:eks:ap-northeast-2:111122223333:access-entry/app-eks/role/111122223333/argocd-role/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
- `arn:aws:eks:ap-northeast-2:111122223333:access-entry/app-eks/role/111122223333/argocd-role/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
- `arn:aws:eks:ap-northeast-2:111122223333:access-entry/app-eks/role/111122223333/argocd-role/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
- `arn:aws:eks:ap-northeast-2:111122223333:access-entry/app-eks/user/111122223333/cicd/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
- `arn:aws:eks:ap-northeast-2:111122223333:access-entry/app-eks/user/111122223333/k8s/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
- `arn:aws:eks:ap-northeast-2:111122223333:access-entry/app-eks/user/444455556666/cicd/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
- `arn:aws:eks:ap-northeast-2:111122223333:access-entry/app-eks/user/444455556666/cicd/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
- `arn:aws:eks:ap-northeast-2:111122223333:access-entry/app-eks/user/444455556666/cicd/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
- `arn:aws:eks:ap-northeast-2:111122223333:access-entry/app-eks/user/444455556666/cicd/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
- `arn:aws:eks:ap-northeast-2:111122223333:access-entry/app-eks/user/444455556666/cicd/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
- `arn:aws:eks:ap-northeast-2:111122223333:access-entry/app-eks/user/444455556666/cicd/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
- `arn:aws:eks:ap-northeast-2:111122223333:access-entry/app-eks/user/444455556666/cicd/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
- `arn:aws:eks:ap-northeast-2:111122223333:access-entry/app-eks/user/444455556666/cicd/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
- `arn:aws:eks:ap-northeast-2:111122223333:access-entry/app-eks/user/444455556666/cicd/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
- `arn:aws:eks:ap-northeast-2:111122223333:access-entry/app-eks/user/444455556666/k8s/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
- `arn:aws:eks:ap-northeast-2:111122223333:access-entry/app-eks/user/444455556666/k8s/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
- `arn:aws:eks:ap-northeast-2:111122223333:access-entry/app-eks/user/444455556666/k8s/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
- `arn:aws:eks:ap-northeast-2:111122223333:access-entry/app-eks/user/444455556666/k8s/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
- `arn:aws:eks:ap-northeast-2:111122223333:access-entry/app-eks/user/444455556666/k8s/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
- `arn:aws:eks:ap-northeast-2:111122223333:access-entry/app-eks/user/444455556666/k8s/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
- `arn:aws:eks:ap-northeast-2:111122223333:access-entry/app-eks/user/444455556666/k8s/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
- `arn:aws:eks:ap-northeast-2:111122223333:access-entry/app-eks/user/444455556666/k8s/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
- `arn:aws:eks:ap-northeast-2:111122223333:access-entry/app-eks/user/444455556666/k8s/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
- `arn:aws:eks:ap-northeast-2:111122223333:addon/app-eks/coredns/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
- `arn:aws:eks:ap-northeast-2:111122223333:addon/app-eks/coredns/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
- `arn:aws:eks:ap-northeast-2:111122223333:addon/app-eks/coredns/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
- `arn:aws:eks:ap-northeast-2:111122223333:addon/app-eks/coredns/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
- `arn:aws:eks:ap-northeast-2:111122223333:addon/app-eks/coredns/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
- `arn:aws:eks:ap-northeast-2:111122223333:addon/app-eks/coredns/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
- `arn:aws:eks:ap-northeast-2:111122223333:addon/app-eks/coredns/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
- `arn:aws:eks:ap-northeast-2:111122223333:addon/app-eks/kube-proxy/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
- `arn:aws:eks:ap-northeast-2:111122223333:addon/app-eks/kube-proxy/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
- `arn:aws:eks:ap-northeast-2:111122223333:addon/app-eks/kube-proxy/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
- `arn:aws:eks:ap-northeast-2:111122223333:addon/app-eks/kube-proxy/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
- `arn:aws:eks:ap-northeast-2:111122223333:addon/app-eks/kube-proxy/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
- `arn:aws:eks:ap-northeast-2:111122223333:addon/app-eks/kube-proxy/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
- `arn:aws:eks:ap-northeast-2:111122223333:addon/app-eks/kube-proxy/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
- `arn:aws:eks:ap-northeast-2:111122223333:addon/app-eks/metrics-server/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
- `arn:aws:eks:ap-northeast-2:111122223333:addon/app-eks/metrics-server/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
- `arn:aws:eks:ap-northeast-2:111122223333:addon/app-eks/metrics-server/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
- `arn:aws:eks:ap-northeast-2:111122223333:addon/app-eks/metrics-server/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
- `arn:aws:eks:ap-northeast-2:111122223333:addon/app-eks/metrics-server/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
- `arn:aws:eks:ap-northeast-2:111122223333:addon/app-eks/metrics-server/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
- `arn:aws:eks:ap-northeast-2:111122223333:addon/app-eks/metrics-server/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
- `arn:aws:eks:ap-northeast-2:111122223333:addon/app-eks/vpc-cni/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
- `arn:aws:eks:ap-northeast-2:111122223333:addon/app-eks/vpc-cni/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
- `arn:aws:eks:ap-northeast-2:111122223333:addon/app-eks/vpc-cni/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
- `arn:aws:eks:ap-northeast-2:111122223333:addon/app-eks/vpc-cni/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
- `arn:aws:eks:ap-northeast-2:111122223333:addon/app-eks/vpc-cni/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
- `arn:aws:eks:ap-northeast-2:111122223333:addon/app-eks/vpc-cni/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
- `arn:aws:eks:ap-northeast-2:111122223333:addon/app-eks/vpc-cni/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
- `arn:aws:eks:ap-northeast-2:111122223333:addon/app-eks/vpc-cni/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
- `arn:aws:eks:ap-northeast-2:111122223333:addon/app-eks/vpc-cni/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
- `arn:aws:eks:ap-northeast-2:111122223333:cluster/app-eks`
- `arn:aws:eks:ap-northeast-2:111122223333:nodegroup/app-eks/api-node-group/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
- `arn:aws:eks:ap-northeast-2:111122223333:nodegroup/app-eks/api-node-group/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
- `arn:aws:eks:ap-northeast-2:111122223333:nodegroup/app-eks/api-node-group/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
- `arn:aws:eks:ap-northeast-2:111122223333:nodegroup/app-eks/api-node-group/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
- `arn:aws:eks:ap-northeast-2:111122223333:nodegroup/app-eks/api-node-group/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
- `arn:aws:eks:ap-northeast-2:111122223333:nodegroup/app-eks/api-node-group/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
- `arn:aws:eks:ap-northeast-2:111122223333:nodegroup/app-eks/api-node-group/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
- `arn:aws:eks:ap-northeast-2:111122223333:nodegroup/app-eks/ops-node-group/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
- `arn:aws:eks:ap-northeast-2:111122223333:nodegroup/app-eks/ops-node-group/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
- `arn:aws:eks:ap-northeast-2:111122223333:nodegroup/app-eks/ops-node-group/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
- `arn:aws:eks:ap-northeast-2:111122223333:nodegroup/app-eks/ops-node-group/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
- `arn:aws:eks:ap-northeast-2:111122223333:nodegroup/app-eks/ops-node-group/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
- `arn:aws:eks:ap-northeast-2:111122223333:nodegroup/app-eks/ops-node-group/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
- `arn:aws:eks:ap-northeast-2:111122223333:nodegroup/app-eks/ops-node-group/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
- `arn:aws:eks:ap-northeast-2:111122223333:nodegroup/app-eks/service-node-group/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
- `arn:aws:eks:ap-northeast-2:111122223333:nodegroup/app-eks/service-node-group/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
- `arn:aws:eks:ap-northeast-2:111122223333:nodegroup/app-eks/service-node-group/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
- `arn:aws:eks:ap-northeast-2:111122223333:nodegroup/app-eks/service-node-group/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
- `arn:aws:eks:ap-northeast-2:111122223333:nodegroup/app-eks/service-node-group/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
- `arn:aws:eks:ap-northeast-2:111122223333:nodegroup/app-eks/service-node-group/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
- `arn:aws:eks:ap-northeast-2:111122223333:nodegroup/app-eks/service-node-group/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
- `arn:aws:iam::111122223333:role/app-db-migration-execution-role`
- `arn:aws:iam::111122223333:role/app-eks-cluster-role`
- `arn:aws:iam::111122223333:role/app-eks-karpenter-node`
- `arn:aws:iam::111122223333:role/app-eks-worker-role`
- `arn:aws:iam::111122223333:role/argocd-role`
- `arn:aws:iam::111122223333:user/cicd`
- `arn:aws:iam::111122223333:user/infra`
- `arn:aws:iam::111122223333:user/k8s`
- `arn:aws:iam::444455556666:user/cicd`
- `arn:aws:iam::444455556666:user/k8s`
- `arn:aws:rds:ap-northeast-2:111122223333:db:postgre`
- `arn:aws:rds:ap-northeast-2:111122223333:pg:app-postgres-parameter`
- `arn:aws:rds:ap-northeast-2:111122223333:subgrp:app-db-subnet-group`
- `arn:aws:sts::111122223333:assumed-role/argocd-role/{{SessionName}}`

## `user:k8s`

| 정책 | 유형 | Sid | 부여 패턴 | 종류 | 상태 | 실관측 액션 |
|---|---|---|---|---|---|---|
| IAMUserChangePassword | managed | (no-sid) | `iam:ChangePassword` | 🟠write | ⬜ 미관측 | — |
| IAMUserChangePassword | managed | (no-sid) | `iam:GetAccountPasswordPolicy` | 🔵read | ⬜ 미관측 | — |

**제안 최소권한 정책**: ✅만 남기고 와일드카드 `Resource:*`는 관측 ARN으로 좁힌 `user-k8s-rightsized-policy.json` 참조.

관측 리소스 ARN:

- `arn:aws:ecr:ap-northeast-2:111122223333:repository/app-frontend`

## `user:sec-scan`

| 정책 | 유형 | Sid | 부여 패턴 | 종류 | 상태 | 실관측 액션 |
|---|---|---|---|---|---|---|
| SecScanReadOnly | managed | IamReadInventory | `iam:ListUsers` | 🔵read | ⬜ 미관측 | — |
| SecScanReadOnly | managed | IamReadInventory | `iam:ListRoles` | 🔵read | ⬜ 미관측 | — |
| SecScanReadOnly | managed | IamReadInventory | `iam:ListUserPolicies` | 🔵read | ⬜ 미관측 | — |
| SecScanReadOnly | managed | IamReadInventory | `iam:GetUserPolicy` | 🔵read | ⬜ 미관측 | — |
| SecScanReadOnly | managed | IamReadInventory | `iam:ListAttachedUserPolicies` | 🔵read | ⬜ 미관측 | — |
| SecScanReadOnly | managed | IamReadInventory | `iam:ListRolePolicies` | 🔵read | ⬜ 미관측 | — |
| SecScanReadOnly | managed | IamReadInventory | `iam:GetRolePolicy` | 🔵read | ⬜ 미관측 | — |
| SecScanReadOnly | managed | IamReadInventory | `iam:ListAttachedRolePolicies` | 🔵read | ⬜ 미관측 | — |
| SecScanReadOnly | managed | IamReadInventory | `iam:GetPolicy` | 🔵read | ⬜ 미관측 | — |
| SecScanReadOnly | managed | IamReadInventory | `iam:GetPolicyVersion` | 🔵read | ⬜ 미관측 | — |
| SecScanReadOnly | managed | IamReadInventory | `iam:ListEntitiesForPolicy` | 🔵read | ⬜ 미관측 | — |
| SecScanReadOnly | managed | IamReadInventory | `iam:GenerateCredentialReport` | 🟠write | ⬜ 미관측 | — |
| SecScanReadOnly | managed | IamReadInventory | `iam:GetCredentialReport` | 🔵read | ⬜ 미관측 | — |
| SecScanReadOnly | managed | CloudTrailLookup | `cloudtrail:LookupEvents` | 🔵read | ⬜ 미관측 | — |
| SecScanReadOnly | managed | WhoAmI | `sts:GetCallerIdentity` | 🔵read | ⬜ 미관측 | — |

**제안 최소권한 정책**: ✅만 남기고 와일드카드 `Resource:*`는 관측 ARN으로 좁힌 `user-sec-scan-rightsized-policy.json` 참조.
