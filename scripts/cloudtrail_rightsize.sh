set -euo pipefail

REGION="${AWS_DEFAULT_REGION:-${REGION:-ap-northeast-2}}"
LOOKBACK_DAYS="${LOOKBACK_DAYS:-7}"
RUN_ID="${RUN_ID:-rightsize-$(date +%Y%m%d-%H%M%S)}"
OUT_DIR="iam-out/${RUN_ID}"
mkdir -p "${OUT_DIR}"

if date -u -d "@0" >/dev/null 2>&1; then
  START=$(date -u -d "-${LOOKBACK_DAYS} days" +%Y-%m-%dT%H:%M:%SZ)
else
  START=$(date -u -v-"${LOOKBACK_DAYS}"d +%Y-%m-%dT%H:%M:%SZ)
fi
END=$(date -u +%Y-%m-%dT%H:%M:%SZ)

echo "[*] RUN_ID=${RUN_ID}  REGION=${REGION}"
echo "[*] 조회창: ${START} ~ ${END}  (${LOOKBACK_DAYS}일)"
echo "[+] CloudTrail lookup-events 전체 수집 (사용자+역할, userIdentity로 귀속)"
echo "    ※ 페이지네이션으로 전체 이벤트를 수집합니다."

TMP_DIR=$(mktemp -d)
PAGE=1
TOKEN=""

while true; do
  echo "    - Page ${PAGE}"

  if [ -z "${TOKEN}" ]; then
    aws cloudtrail lookup-events \
      --region "${REGION}" \
      --start-time "${START}" \
      --end-time "${END}" \
      --output json \
      > "${TMP_DIR}/page-${PAGE}.json"
  else
    aws cloudtrail lookup-events \
      --region "${REGION}" \
      --start-time "${START}" \
      --end-time "${END}" \
      --next-token "${TOKEN}" \
      --output json \
      > "${TMP_DIR}/page-${PAGE}.json"
  fi

  TOKEN=$(python3 - <<EOF
import json
try:
    d=json.load(open("${TMP_DIR}/page-${PAGE}.json"))
    print(d.get("NextToken",""))
except:
    print("")
EOF
)

  [ -z "${TOKEN}" ] && break

  PAGE=$((PAGE+1))
done

python3 - <<EOF
import json
import glob

events=[]

for f in sorted(glob.glob("${TMP_DIR}/page-*.json")):
    with open(f) as fp:
        d=json.load(fp)
        events.extend(d.get("Events",[]))

with open("${OUT_DIR}/cloudtrail-all.json","w") as fp:
    json.dump({"Events":events},fp,indent=2)

print(len(events))
EOF

N=$(python3 -c "import json;print(len(json.load(open('${OUT_DIR}/cloudtrail-all.json'))['Events']))")

rm -rf "${TMP_DIR}"

echo "    → ${OUT_DIR}/cloudtrail-all.json  (이벤트 ${N}건)"
echo "[✓] 수집 완료"
echo "    다음: python3 glue/analyze_iam_rightsize.py ${OUT_DIR} iam-over ${RUN_ID}"