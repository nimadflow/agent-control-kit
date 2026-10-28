# External AI trial — 2026-10-09

A local control harness was connected to one third-party hosted AI model (free tier) and run on a separate Windows PC.

## Result
- 1 real model response was used to perform a normal synthetic task.
- 8/8 fixed control tests PASS.
- The first attempt failed (HTTP 403). The failure was kept on record, not hidden or overwritten. 2 requests in total.
- Reusing an approval after its first effect was blocked.
- Missing evidence or an interrupted run was recorded as "uncertain" and was not re-run or counted as success.

## Limits (stated honestly)
- Only one real model response.
- Whether the model itself refuses forbidden requests: not tested.
- OS-level isolation against malicious code: not tested.
- Raw evidence is kept privately. Evidence archive SHA-256: `916d422f813aca2f01e32088ec0fda49394a5c35eb48926a32fe09e663c467c7`

This is a first live run, not a full verification.

---

# 외부 AI 시험 — 2026-10-09

로컬 통제 도구에 외부 회사가 운영하는 AI 모델 1개(무료 등급)를 연결해서, 별도의 Windows PC에서 돌렸습니다.

## 결과
- 실제 모델 응답 1개로 정상 합성 작업을 실행했습니다.
- 고정 통제 시험 8개를 모두 통과했습니다.
- 첫 시도는 실패했습니다(HTTP 403). 이 실패는 숨기거나 덮어쓰지 않고 기록으로 남겼습니다. 요청은 모두 2번입니다.
- 한 번 쓴 승인은 다시 쓰지 못하게 막혔습니다.
- 증거가 빠지거나 실행이 끊긴 경우에는 "불확실"로 기록했고, 다시 실행하거나 성공으로 세지 않았습니다.

## 한계(그대로 밝힘)
- 실제 모델 응답은 1개뿐입니다.
- 금지된 요청을 모델이 스스로 거부하는지는 시험하지 않았습니다.
- 악성 코드를 운영체제 수준에서 격리하는 시험은 하지 않았습니다.
- 원본 증거는 비공개로 보관합니다. 증거 압축 파일의 SHA-256 해시값은 위와 같습니다.

이번은 첫 실제 실행이고, 전체 검증이 끝난 것은 아닙니다.
