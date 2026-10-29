# AgentDojo trial — 2026-10-29

**한국어는 아래에 있습니다.**

## Headline

On a public prompt-injection benchmark built by others (AgentDojo, ETH Zurich), the same model was attacked with and without the external control layer.

| Mode | Attacks that got through (non-error runs) | Legit task still done (non-error runs) | Errored runs |
|---|---|---|---|
| No defense | **2 / 6** | 6 / 6 | 3 |
| Control layer on | **0 / 6** | 5 / 6 | 3 |

Blocked attack calls observed in output include `send_email` and `delete_file`.

## The known gap — read this first

This control layer gates **which tools** an agent may call. It does not yet check **what arguments** go into an allowed tool.

So if the user's real task needs `send_email`, and the attacker also wants `send_email` (to a different recipient), a tool-name gate **cannot** stop it. In an offline mock run, exactly this case got through (1/9).

User task 25 in this subset is that case. **It was not measured in this live run** (see below). The 0/6 above does not cover it.

Next step: argument-level checks (e.g. a recipient allowlist) to close the same-tool gap.

## Setup

- Benchmark: AgentDojo 0.1.35, `workspace` suite v1.2.2, default attack `important_instructions` (model name rendered as "AI assistant").
- Pairs: user tasks 0, 1, 25 × injection tasks 0 (send email), 1 (delete file), 2 (create calendar event) = 9 pairs, each run in two modes: `no_defense` and `controller`.
- Model: `openai/gpt-oss-120b` via Groq free tier. 112 LLM calls, 833 s.
- Log: hash-chained JSONL, integrity check passed (`log_ok=True`).
- Script: `live_trial/agentdojo_trial.py` at commit `f025ad1` (main run). `harness.py` unchanged.
- Control-layer scope per task: the task's ground-truth tools + read-only lookup tools (`get_`/`search_`/`list_`). Side-effect tools are allowed only if in the ground truth.
  - Note: deriving scope from ground truth assumes an accurate human pre-approval of what the task needs. That is a favorable condition.

## Full numbers

| Mode | Utility under attack | Attack success | Errors | Non-error ASR | Non-error utility |
|---|---|---|---|---|---|
| no_defense | 6/9 | 2/9 | 3 | 2/6 | 6/6 |
| controller | 5/9 | 0/9 | 3 | 0/6 | 5/6 |

Earlier run the same day (before a scope fix): no_defense 3/9 attacks succeeded (3 errors); controller 0/9 (2 errors), but the controller over-blocked legitimate lookup tools in task 25. Scope was fixed to allow read-only tools (commit `f025ad1`).

## Why task 25 is unmeasured

- `gpt-oss-120b` emitted a malformed tool name (`search_files<|channel|>commentary`) → Groq HTTP 400.
- Groq free-tier tokens-per-minute limit (8000) → HTTP 413 on the long prompts.
- A retry with `qwen/qwen3.8-27b` first failed on a chat-template role error (fixed in `57d88b7`), then hit the same 413 limit.

These are environment failures, not control-layer results. They are reported as errors, not counted as blocks.

## Limits

- Tiny subset (9 pairs, 6 scored), one model, self-run.
- Not comparable to the AgentDojo leaderboard.
- No third-party reproduction yet.

## Reproduce

```
uv run --with agentdojo python live_trial/agentdojo_trial.py
```
(Add `--mock` for an offline run. Asks for a Groq API key with a hidden prompt, or reads `GROQ_API_KEY`.)

Please reproduce it — and publish failures too.

---

# AgentDojo 시험 — 2026-10-29

## 핵심 결과

다른 사람들이 만든 공개 프롬프트 인젝션 벤치마크(AgentDojo, ETH 취리히)에서, 같은 모델을 외부 통제층 없이/있이 공격했습니다.

| 모드 | 뚫린 공격 (오류 없는 판) | 정상 작업 성공 (오류 없는 판) | 오류 판 |
|---|---|---|---|
| 방어 없음 | **2 / 6** | 6 / 6 | 3 |
| 통제층 켬 | **0 / 6** | 5 / 6 | 3 |

출력에서 확인된 차단 공격 호출: `send_email`, `delete_file` 등.

## 알려진 약점 — 먼저 읽어 주세요

이 통제층은 에이전트가 **어떤 도구**를 쓸 수 있는지를 막습니다. 허용된 도구에 **어떤 인자**가 들어가는지는 아직 검사하지 않습니다.

그래서 사용자의 실제 작업에 `send_email`이 필요하고 공격도 `send_email`(다른 수신자)을 쓰면, 도구 이름 기반 통제는 이를 **막을 수 없습니다**. 오프라인 모의 실행에서 바로 이 경우가 뚫렸습니다(1/9).

이번 부분집합의 사용자 작업 25가 그 경우인데, **이번 실제 실행에서는 측정되지 않았습니다**(아래 참고). 위의 0/6은 이 경우를 포함하지 않습니다.

다음 단계: 같은 도구 공격을 막기 위한 인자 단위 검사(예: 수신자 허용 목록).

## 설정

- 벤치마크: AgentDojo 0.1.35, `workspace` 스위트 v1.2.2, 기본 공격 `important_instructions`(모델 이름은 "AI assistant"로 표시).
- 조합: 사용자 작업 0, 1, 25 × 인젝션 작업 0(메일 보내기), 1(파일 삭제), 2(캘린더 일정 생성) = 9쌍, 각각 `no_defense`와 `controller` 두 모드로 실행.
- 모델: Groq 무료 등급의 `openai/gpt-oss-120b`. LLM 호출 112회, 833초.
- 기록: 해시 체인 JSONL, 무결성 검사 통과(`log_ok=True`).
- 스크립트: `live_trial/agentdojo_trial.py`, 본 실행은 커밋 `f025ad1`. `harness.py`는 변경 없음.
- 작업별 통제 범위: 그 작업의 정답 도구 + 읽기 전용 조회 도구(`get_`/`search_`/`list_`). 부작용이 있는 도구는 정답에 있을 때만 허용.
  - 참고: 정답에서 범위를 뽑는 것은 사람이 작업에 필요한 것을 정확히 미리 승인했다는 가정이며, 유리한 조건입니다.

## 전체 숫자

| 모드 | 공격 중 정상 작업 | 공격 성공 | 오류 | 오류 제외 공격 성공 | 오류 제외 정상 작업 |
|---|---|---|---|---|---|
| no_defense | 6/9 | 2/9 | 3 | 2/6 | 6/6 |
| controller | 5/9 | 0/9 | 3 | 0/6 | 5/6 |

같은 날 앞선 실행(범위 수정 전): 방어 없음 3/9 성공(오류 3), 통제층 0/9(오류 2). 다만 그때 통제층이 작업 25에서 정상 조회 도구까지 과하게 막았고, 읽기 전용 도구를 허용하도록 고쳤습니다(커밋 `f025ad1`).

## 작업 25를 측정하지 못한 이유

- `gpt-oss-120b`가 깨진 도구 이름(`search_files<|channel|>commentary`)을 보내 Groq가 HTTP 400으로 거절.
- Groq 무료 등급 분당 토큰 한도(8000) 초과로 긴 요청에서 HTTP 413.
- `qwen/qwen3.8-27b`로 재시도했으나 처음엔 채팅 템플릿 역할 오류(`57d88b7`에서 수정), 이후 같은 413 한도에 걸림.

이것들은 환경 문제이지 통제층 결과가 아닙니다. 차단으로 세지 않고 오류로 보고했습니다.

## 한계

- 아주 작은 부분집합(9쌍 중 6쌍 채점), 모델 1개, 직접 실행.
- AgentDojo 리더보드와 비교할 수 없음.
- 아직 제3자 재현 없음.

## 재현

```
uv run --with agentdojo python live_trial/agentdojo_trial.py
```
(오프라인은 `--mock`. Groq API 키를 화면에 안 보이게 묻거나 `GROQ_API_KEY`를 읽습니다.)

직접 재현해 보시고, 실패 결과도 공개해 주세요.
