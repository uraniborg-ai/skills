---
title: Limit UB Writing To Project Technical Documentation
description: ub-writing의 적용 범위를 프로젝트 기술 문서와 Git commit message로 제한하고 문서 라우팅, proposal handoff, 생성 문서, agent 지침 source-of-truth를 정리한다.
author:
  - Hyounggyu Kim <code@hyounggyu.com>
status: implemented
created_at: 2026-06-28T00:00:00+09:00
updated_at: 2026-06-28T10:57:30+09:00
---

# Limit UB Writing To Project Technical Documentation

## 목적

`ub-writing`을 범용 글쓰기 스킬이 아니라 프로젝트 기술 문서와
contributor-facing operating docs를 정리하는 스킬로 제한한다. 특정 문서의 존재를
강제하지 않고, 남겨야 할 내용이 생겼을 때 어디에 둘지와 어떻게 쓸지를 안내한다.

## 핵심 판단

- `ub-writing`은 문학, 블로그, 마케팅, 개인 노트, 발표 원고, 프롬프트 실험을
  기본 대상으로 삼지 않는다.
- `README.md`, `AGENTS.md`, `CHANGELOG.md`, `CONTRIBUTING.md`, `docs/**/*.md`는
  적용 가능 위치일 뿐 필수 문서가 아니다.
- 새 문서를 만들기 전에 기존 문서에 짧게 추가할 수 있는지 먼저 확인한다.
- 문서 추가는 새 source of truth가 필요한지, 반복적으로 참조될 판단인지, 변경 시
  함께 갱신할 소유 경계가 있는지를 기준으로 판단한다.
- `CHANGELOG.md`는 존재할 때 shipped history를 기록하는 곳이며, 릴리스 절차 문서
  생성을 강제하지 않는다.
- Proposal, RFC, ADR, decision record 작업은 `$ub-proposals`와 함께 다룬다.
- 생성된 reference Markdown은 직접 편집하지 않고 생성 원천이나 generator 쪽으로
  변경을 라우팅한다.
- `ub-writing`은 Git commit message 작성을 지원한다. 로컬 규칙이 없으면
  Conventional Commits v1.0.0을 기본값으로 쓰고, 기본 언어는 영어로 한다.

## 문서 라우팅

- 프로젝트 소개, 빠른 시작, 대표 명령, 현재 상태는 기존 `README.md`나 가까운
  소개 문서에 둔다.
- 에이전트가 작업 전에 반드시 알아야 할 실행, 검증, 안전, source-of-truth 포인터는
  `AGENTS.md`에 짧게 둘 수 있다. `AGENTS.md` 생성은 강제하지 않는다.
- 상세한 agent-specific 설명, 긴 legacy Claude 내용, 모델별 운영 메모는
  `AGENTS.md`에 밀어 넣지 않고 적절한 `docs/` 문서로 분리하도록 안내한다.
- 개발 환경, 로컬 루프, 검증 명령, done criteria는 기존 개발 문서가 있으면 거기에
  둔다. 없으면 새 `docs/development.md`를 제안할 수 있다.
- 시스템 경계, ownership, data/runtime/API/source-of-truth 판단은 기존 아키텍처
  문서가 있으면 거기에 둔다. 없으면 새 `docs/architecture.md`를 제안할 수 있다.
- 제품/기술 판단 기준은 기존 철학/원칙 문서가 있으면 거기에 둔다. 없으면 반복적으로
  참조될 때만 새 문서를 제안한다.
- 현재 초점, proposal/release 연결, maintainer planning index는 기존 roadmap
  문서가 있을 때 갱신한다. 없으면 짧은 README 섹션이나 issue/milestone이 충분한지
  먼저 판단한다.
- 복잡한 배포, version bump, artifact publish 절차가 있을 때만 release runbook을
  제안한다.

## Proposal Handoff

`ub-writing`은 proposal lifecycle 규칙을 소유하지 않는다. 작업 대상이
`docs/proposals/`, proposal, RFC, ADR, decision record, proposal status,
frontmatter, non-goals, acceptance scenarios, proposal lifecycle이면 먼저
`$ub-proposals` 사용 가능 여부를 확인한다.

- `$ub-proposals`가 있으면 `$ub-writing`과 함께 사용한다.
- `$ub-proposals`가 없으면 proposal 작성이나 수정 전에 설치를 제안한다.
- 사용자가 설치를 거절하거나 환경상 설치할 수 없으면 local proposal convention
  기반 fallback으로 진행하되, fallback임을 밝히고 열린 가정을 남긴다.
- 설치 자체는 사용자의 명시적 승인 없이는 실행하지 않는다.

## Commit Message Writing

`ub-writing`은 Git commit message 작성과 리뷰를 지원한다. Commit message는 짧은
불변 개발 기록이므로 일반 문서보다 더 좁은 규칙을 적용한다.

- 먼저 로컬 규칙을 찾는다: `AGENTS.md`, `CONTRIBUTING.md`,
  `docs/commit-conventions.md`, release docs, 가까운 maintainer docs.
- 로컬 규칙이 있으면 그 규칙을 우선한다.
- 로컬 규칙이 없으면 [Conventional Commits v1.0.0] 형식을 기본값으로 쓴다.
- 기본 언어는 영어다.
- subject는 imperative mood, lowercase description, trailing period 없음으로 쓴다.
- staged changes가 있으면 `git diff --cached` 기준으로 작성한다.
- staged changes가 없으면 unstaged diff 기준 후보를 만들 수 있지만, 아직 staged
  기준 메시지가 아님을 밝힌다.
- unrelated changes가 섞여 있으면 하나의 메시지로 뭉개지 않고 commit split을
  제안한다.
- breaking change가 있으면 `!` 또는 `BREAKING CHANGE:` footer를 사용한다.
- `ub-writing`은 메시지를 제안하거나 리뷰할 뿐, 사용자의 명시적 요청 없이
  `git commit`을 실행하지 않는다.

기본 형식:

```text
<type>[optional scope][!]: <description>
```

[Conventional Commits v1.0.0]: https://www.conventionalcommits.org/en/v1.0.0/

## 작성 방식

- 문서 작업 시작 시 audience/job을 `user-facing`, `contributor-facing`,
  `maintainer-facing`, `generated`, `proposal` 중 하나로 분류한다.
- Diataxis는 파일명 강제가 아니라 판단 기준으로 사용한다. How-to, reference,
  explanation, tutorial 성격을 먼저 보고 기존 문서 구조에 맞춘다.
- 유용한 문장을 먼저 두고, 한 문장에는 하나의 판단만 둔다.
- 요구사항에는 `must`, 능력에는 `can`, 의도적 지침에는 `should`를 사용한다.
- 반복 설명, 모호한 actor, 과장된 제품 claim, user-facing 문서의 내부 구현 디테일을
  줄인다.
- 생성 문서의 문구 문제가 있으면 source comments/docstrings, generator,
  template/config, wrapper README, regenerate command 수정으로 라우팅한다.

## 스킬 문서 개편

- `SKILL.md` description에서 `product copy` 등 넓은 범위를 제거한다.
- `Scope` 섹션은 필수 파일 목록이 아니라 in-scope content type과 out-of-scope
  writing type을 설명한다.
- 자세한 문서 라우팅 지침은 `references/project-doc-structure.md`로 분리한다.
- `agents/openai.yaml`의 `short_description`은 project technical docs 중심으로
  좁힌다.
- README의 `ub-writing` 설명과 `CHANGELOG.md`의 `Unreleased` 항목을 갱신한다.
- Commit message 작성 지침은 `SKILL.md`에는 핵심 trigger만 두고,
  `references/project-doc-structure.md`에 세부 규칙을 둔다.

## 비목표

- 모든 프로젝트에 `README.md`, `AGENTS.md`, `CHANGELOG.md`, `CONTRIBUTING.md`,
  `docs/architecture.md`, `docs/development.md`, `docs/roadmap.md`, 또는
  `docs/release.md` 생성을 강제하지 않는다.
- 기존 프로젝트 문서나 생성 경로를 자동 rename하지 않는다.
- `AGENTS.md`와 `CLAUDE.md`의 symlink 생성을 강제하지 않는다.
- 생성된 reference Markdown을 직접 편집 대상으로 삼지 않는다.
- PR title, PR body, release note 작성 규칙은 이번 범위에서 다루지 않는다.
- `docs/development.md`에 카탈로그 전체 문서 표준을 추가하지 않는다.

## 성공 기준

- `ub-writing`은 프로젝트 기술 문서와 contributor-facing operating docs 요청에
  집중한다.
- "개발 명령을 문서화해줘" 요청은 기존 개발 문서나 README 섹션으로 라우팅된다.
- "아키텍처 경계를 정리해줘" 요청은 기존 architecture 문서가 있으면 갱신하고,
  없으면 필요성을 설명한 뒤 새 문서를 제안한다.
- "AGENTS.md 만들어줘" 요청이 없으면 `AGENTS.md` 생성을 기본 제안하지 않는다.
- Proposal 작성 요청은 `$ub-proposals` 확인과 handoff 규칙을 따른다.
- "커밋 메시지 작성해줘" 요청은 로컬 규칙을 먼저 확인하고, 없으면 영어
  Conventional Commits 형식으로 제안한다.
- staged changes가 있으면 staged diff 기준 메시지를 작성하고, unrelated changes가
  섞여 있으면 commit split을 제안한다.
- 시, 에세이, 블로그 초안 작성 요청은 기본적으로 `ub-writing` 적용 대상이 아니다.
- 생성된 reference Markdown 문구 문제는 직접 수정 대신 generator/source update로
  안내한다.
- 다음 검증 명령이 통과한다.

```sh
uv run --script skills/ub-proposals/scripts/check_proposal_frontmatter.py docs/proposals
npm run smoke
git diff --check
```

## 열린 결정

현재 이 제안서의 수용을 막는 열린 결정은 없다.
