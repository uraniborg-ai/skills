---
title: Refactor UB Presentation Project Structure
description: ub-presentation의 발표 자료 파일 역할, 산출물 디렉토리, 생성 파이프라인 경계를 재정의한다.
author:
  - Hyounggyu Kim <code@hyounggyu.com>
status: implemented
created_at: 2026-06-28T00:00:00+09:00
updated_at: 2026-06-28T11:05:37+09:00
---

# Refactor UB Presentation Project Structure

## 목적

`ub-presentation`의 발표 자료 디렉토리 구조와 데이터 계약을 정리한다. 파일
이름은 역할을 드러내고, frontmatter는 문서 상태만 기록하며, 생성 파이프라인의
중간 산출물과 사용자 검토 산출물을 분리한다.

## 핵심 판단

- `presentation.yaml`은 제거한다. 현재 스크립트가 읽지 않고, `draft.md`와
  `slides.md` frontmatter가 필요한 문서 상태를 충분히 담을 수 있다.
- `transcript.md`는 제거한다. `narration.json`이 실행 가능한 spoken script의
  source of truth이고, 읽기용 transcript는 필수 산출물이 아니다.
- `draft.md`와 `slides.md`는 파일명으로 역할을 드러낸다. 두 Markdown 파일은
  같은 최소 frontmatter 필드만 사용한다.
- `narration.json`은 voiceover와 render pipeline이 읽는 실행 입력으로 유지한다.
- `build/`는 중간 산출물 전용 디렉토리로 둔다.
- `images/`, `voiceover/`, `captions/`, `exports/`는 사용자가 검토하거나
  보존하는 산출물 디렉토리로 둔다.
- YouTube 자막은 루트 `youtube.srt`가 아니라 `captions/youtube.srt`에 생성한다.
- 세부 지침은 특정 발표 사례가 아니라 범용 원칙 중심으로 압축한다.

## 상태 값

제안서의 `status`는 다음 값만 사용한다.

- `draft`: 작성 및 조율 중
- `proposed`: 검토 가능한 상태
- `accepted`: 구현하기로 승인됨
- `implemented`: 구현 완료
- `superseded`: 다른 제안서로 대체됨
- `rejected`: 구현하지 않기로 결정됨

발표 Markdown 문서의 `status`는 다음 값만 사용한다.

- `draft`: 작성 중
- `active`: 현재 기준 문서
- `superseded`: 다른 문서나 버전으로 중심이 넘어감
- `archived`: 보존용

`draft.md`와 `slides.md` frontmatter는 다음 필드만 사용한다.

```yaml
---
title: Presentation Title
description: One-sentence presentation purpose or message.
author:
  - Hyounggyu Kim <code@hyounggyu.com>
status: draft
created_at: 2026-06-28T00:00:00+09:00
updated_at: 2026-06-28T00:00:00+09:00
---
```

## 대상 구조

```text
draft.md
slides.md
narration.json
images/
voiceover/
captions/
  youtube.srt
exports/
  final.mp4
build/
  voiceover/
  timeline.json
  render/
```

`draft.md`는 발표 전체의 아이디어, 배경, 논리, 예시를 발전시키는 문서다.
`slides.md`는 슬라이드 흐름과 메시지를 조율하는 작업 문서다. `narration.json`은
실행 가능한 voiceover 입력이다.

## 작업 워크플로우

1. `draft.md`에서 발표 아이디어와 논리를 정리한다.
2. 일정 단계 이후 `slides.md`를 중심으로 슬라이드 흐름, 메시지, 이미지 방향을
   확정한다.
3. `slides.md`의 합의된 흐름을 `narration.json`의 `slides[].segments[]`와
   `slides[].image`에 반영한다.
4. 이미지, 음성, 자막을 각각 `images/`, `voiceover/`, `captions/`에 생성하거나
   갱신한다.
5. timeline, render clip, concat list, 임시 영상 같은 계산 산출물은 `build/`에
   생성한다.
6. 최종 배포 영상은 `exports/final.mp4`에 생성한다.

## 데이터 계약

- `narration.json`은 pipeline의 유일한 실행 입력이다.
- `slides[].segments[]`는 TTS에 전달되는 spoken script 단위다.
- `slides[].image`는 발표 디렉토리 기준의 slide image 경로다.
- `draft.md`와 `slides.md` frontmatter는 문서 상태를 설명할 뿐 pipeline 동작을
  제어하지 않는다.
- `captions/youtube.srt`는 `narration.json`과 timeline에서 생성되는 자막
  산출물이다.
- `build/` 아래 파일은 삭제 가능한 중간 산출물로 취급한다.
- 기존 프로젝트의 루트 `youtube.srt`와 `transcript.md`는 자동 삭제하지 않는다.

## 스킬 문서 개편

- `SKILL.md`는 전체 작업 흐름과 주요 명령만 보여주는 첫 화면 문서로 유지한다.
- 세부 구조와 frontmatter 지침은 `references/project-workflow.md`로 분리한다.
- `references/input-schema.md`는 `narration.json` 계약만 설명하도록 좁힌다.
- `references/script-editing.md`는 spoken flow, terminology, source/generated
  artifact 경계를 범용 원칙으로 정리한다.
- `references/image-prompting.md`는 reference asset, pilot image, visual QA
  원칙을 범용화한다.
- 특정 발표 사례에서 나온 문장은 일반 발표 프로젝트에도 적용되는 기준으로
  바꾸거나 제거한다.

## 구현 단계

1. 이 제안서를 작성하고 검토한다.
2. `SKILL.md`와 references를 새 구조와 frontmatter 정책에 맞게 재구성한다.
3. path helper를 리팩토링해 중간 산출물은 `build/`로, 보존 산출물은
   `images/`, `voiceover/`, `captions/`, `exports/`로 분리한다.
4. `transcript.md` 생성을 제거하고, 자막 생성 위치를 `captions/youtube.srt`로
   변경한다.
5. dry-run 출력, tests, changelog를 새 계약에 맞게 갱신한다.

## 비목표

- 기존 발표 프로젝트의 루트 `youtube.srt`나 `transcript.md`를 자동 삭제하지 않는다.
- 기존 발표 프로젝트 전체를 자동 마이그레이션하는 도구는 이 제안서의 범위가 아니다.
- `draft.md`나 `slides.md` frontmatter로 pipeline 동작을 제어하지 않는다.
- 복잡한 stage, sync, dependency metadata를 Markdown frontmatter에 추가하지 않는다.
- ElevenLabs API 동작, ffmpeg 렌더링 방식, 자막 포맷 자체는 바꾸지 않는다.

## 성공 기준

- 새 프로젝트 dry-run이 `captions/youtube.srt`, `exports/final.mp4`, `build/...`
  경로를 출력한다.
- subtitle 생성은 `captions/youtube.srt`만 만들고, 루트 `youtube.srt`와
  `transcript.md`를 새로 만들지 않는다.
- `slides.md`에 frontmatter가 있어도 slide title parser가 `##` 제목을 안정적으로
  읽는다.
- `SKILL.md`는 전체 작업 흐름을 빠르게 파악할 수 있고, 세부 지침은 references로
  분리되어 있다.
- 다음 검증 명령이 통과한다.

```sh
npm run smoke
python3 -m unittest discover -s skills/ub-presentation/scripts -p 'test_*.py'
git diff --check
```

## 열린 결정

현재 이 제안서의 수용을 막는 열린 결정은 없다. 구현 중 새 호환성 문제가 발견되면
별도 후속 제안서나 이 제안서의 `updated_at` 갱신과 함께 다룬다.
