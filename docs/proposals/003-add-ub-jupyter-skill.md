---
title: Add UB Jupyter Skill
description: Jupyter notebook을 스키마 기반으로 다루고 프로젝트 환경을 uv 중심으로 파악한 뒤 명시적 요청 시 실행하는 ub-jupyter 스킬을 추가한다.
author:
  - Hyounggyu Kim <code@hyounggyu.com>
  - Codex
status: implemented
created_at: 2026-06-28T19:29:58+09:00
updated_at: 2026-06-28T20:46:52+09:00
---

# Add UB Jupyter Skill

## 목적

`ub-jupyter`를 추가해 에이전트가 연구와 엔지니어링 프로젝트의 Jupyter
notebook을 안전하게 읽고, 편집하고, 검증하도록 안내한다. 첫 버전은 local
filesystem의 `.ipynb` 작업을 대상으로 하며, live JupyterLab이나 remote Jupyter
Server 제어는 다루지 않는다.

이 스킬은 `.ipynb`를 일반 JSON 텍스트가 아니라 `nbformat` 스키마 문서로 취급한다.
Notebook 실행은 해당 notebook이 놓인 프로젝트의 개발 환경을 먼저 파악한 뒤,
`ub-dev-env`와 `ub-uv` 원칙에 따라 `uv` 중심으로 수행한다.

## 핵심 판단

- `ub-jupyter`는 notebook 조사, 셀 단위 편집, 명시적 실행, 렌더링 검증, Git 리뷰
  보조를 다룬다.
- 기본 동작은 read-only다. 파일 쓰기, 셀 실행, notebook 실행, 네트워크 접근,
  output 삭제는 사용자의 요청이나 프로젝트 workflow가 명확할 때만 수행한다.
- `.ipynb` 파일은 `nbformat` API로 읽고 쓰며, 직접 문자열 치환으로 수정하지 않는다.
- 편집 시 cell `id`, `metadata`, `attachments`, `outputs`, execution count를
  보존한다. 출력 정리나 재실행으로 값이 바뀌는 경우에는 변경 의도를 설명한다.
- Notebook 실행은 `ub-dev-env`로 프로젝트 setup source를 먼저 읽고, `ub-uv`로
  Python 실행 경로를 정한 뒤 수행한다.
- 실행은 notebook이 있는 프로젝트 공간에서 `uv run`을 우선 사용하며, 필요하면
  `nbclient`, `jupyter execute`, Papermill 같은 notebook-aware 도구를 그 환경 안에서
  호출한다.
- 원본 notebook 덮어쓰기는 기본값이 아니다. 검증이나 실험 실행은 가능한 경우
  `*-executed.ipynb` 같은 별도 산출물로 남긴다.
- Git 리뷰 가능성을 높이기 위해 프로젝트가 Jupytext paired notebook을 쓰면 paired
  text 파일을 우선 검토하고, `.ipynb` diff에는 `nbdime` 계열 도구를 선호한다.

## 작업 모드

### Notebook 조사

- `nbformat.read(..., as_version=4)`로 notebook을 로드한다.
- kernel metadata, language info, cell count, markdown heading, code imports,
  outputs 존재 여부, widgets 또는 large embedded data 여부를 요약한다.
- 실행 결과가 오래됐거나 재현성이 의심될 때는 바로 실행하지 않고, 필요한 kernel과
  dependency를 먼저 보고한다.

### 프로젝트 환경 조사

- Notebook 실행 요청이 있으면 먼저 `README*`, `CONTRIBUTING*`, `docs/`,
  `pyproject.toml`, `uv.lock`, `requirements*.txt`, `environment*.yml`, Docker files,
  CI config, kernelspec metadata를 확인한다.
- Notebook 파일 위치, 프로젝트 루트, 데이터 파일 위치, 상대 경로 사용 방식을 함께
  파악한다.
- Python project가 `pyproject.toml`, `uv.lock`, 또는 기존 uv 사용을 포함하면
  `ub-uv` 원칙에 따라 `uv run`을 기본 실행 entrypoint로 사용한다.
- Project dependency를 durable하게 바꾸는 `uv add`, lockfile 갱신, environment sync,
  shell 설정 변경은 사용자의 명시적 요청이 있을 때만 수행한다.
- One-off helper dependency가 필요하면 project dependency로 추가하기 전에
  `uv run --with ...` 또는 PEP 723 script 사용이 충분한지 판단한다.

### Notebook 편집

- 셀 단위로 변경하고 `nbformat.validate`로 저장 전후 구조를 확인한다.
- code cell과 markdown cell을 추가할 때는 `nbformat.v4.new_code_cell`과
  `new_markdown_cell` 같은 생성 API를 사용한다.
- 기존 output을 삭제하지 않는다. 출력 제거가 목적이면 변경 범위를 명확히 설명하고
  프로젝트의 `nbstripout`, pre-commit, 또는 review 정책을 확인한다.
- notebook이 Jupytext paired format을 사용하면 pairing metadata를 확인하고,
  프로젝트 정책에 따라 paired source와 `.ipynb`의 sync 상태를 맞춘다.

### Notebook 실행

- 실행 요청이 있으면 kernel name, 실행 cwd, timeout, project environment, data path,
  network 필요 여부를 먼저 확인한다.
- 실행 cwd는 프로젝트 설정과 notebook 상대 경로 사용을 함께 보고 정한다. 선택한 cwd와
  이유를 실행 결과에 남긴다.
- `uv run` 안에서 `nbclient.NotebookClient` 또는 동등한 notebook-aware runner를
  사용하고, 실행 실패 시 traceback과 partially executed output이 남을 수 있음을
  보고한다.
- notebook parameterization이 핵심이면 Papermill 사용을 고려한다.
- 실행 후 `nbformat.validate`와 필요한 smoke assertion을 수행한다.

## 스킬 문서 구성

- `SKILL.md`는 trigger, 안전 기본값, notebook 조사/편집/실행의 짧은 workflow를
  담는다.
- `references/notebook-format.md`에는 `nbformat` 구조, cell 보존 규칙, output과
  metadata 취급을 둔다.
- `references/project-execution.md`에는 `ub-dev-env`/`ub-uv` handoff, `uv run`,
  `nbclient`, `jupyter execute`, Papermill, timeout, cwd, kernel, dependency 확인
  절차를 둔다.
- `references/review.md`에는 Jupytext, nbdime, nbstripout, Git diff hygiene를 둔다.
- Python helper script를 추가한다면 PEP 723 metadata를 사용하고
  `uv run --script`로 실행되게 한다.

## 구현 단계

1. `skills/ub-jupyter/SKILL.md`와 `agents/openai.yaml`을 추가한다.
2. 필요한 세부 지침을 `references/`로 분리한다.
3. 반복적이고 오류가 나기 쉬운 notebook inspection 또는 validation은 작은 Python
   script로 제공할지 결정한다.
4. `README.md`, `CHANGELOG.md`, `tests/smoke/check_structure.py`를 갱신한다.
5. `npm run smoke`와 필요한 Python formatting/check 명령을 실행한다.

## 비목표

- Live JupyterLab, remote Jupyter Server, MCP server, kernel gateway, notebook
  renderer 제어는 첫 버전에서 다루지 않는다.
- 모든 notebook을 자동으로 재실행하거나 output을 제거하지 않는다.
- 사용자의 명시적 요청 없이 kernel을 시작하거나, notebook cell을 실행하거나,
  remote service에 연결하지 않는다.
- `.ipynb`를 Python script나 Markdown으로 강제 변환하지 않는다.
- 과거 notebook의 재현성 문제를 자동으로 해결하지 않는다. Dependency, data, kernel
  문제는 진단하고 보고한다.
- notebook 내부의 과학적 결론을 검증 대상으로 삼지 않는다. 스킬은 실행 가능성,
  구조, 변경 안전성, reviewability를 우선한다.

## 성공 기준

- "notebook을 요약해줘" 요청은 실행 없이 구조, kernel, 주요 셀, output 상태를
  설명한다.
- "이 셀을 고쳐줘" 요청은 `nbformat` 기반으로 셀을 수정하고 cell metadata와 output
  보존 여부를 명확히 한다.
- "notebook을 실행해줘" 요청은 프로젝트 setup source를 먼저 읽고, notebook 위치와
  프로젝트 루트, kernel, cwd, timeout, dependency를 확인한 뒤 실행한다.
- Python project가 uv를 사용하면 notebook 실행도 `uv run` 경로를 따른다.
- 실행 실패 시 실패 셀, 예외, 남은 output 상태, 재시도 조건을 보고한다.
- 프로젝트가 Jupytext를 쓰면 paired source와 `.ipynb` sync 상태를 확인한다.
- output stripping은 사용자의 요청이나 프로젝트 정책이 있을 때만 수행한다.
- 다음 검증 명령이 통과한다.

```sh
uv run --script skills/ub-proposals/scripts/check_proposal_frontmatter.py docs/proposals
npm run smoke
git diff --check
```

## 열린 결정

현재 이 제안서의 수용을 막는 열린 결정은 없다. 첫 구현은 deterministic helper
script 없이 `SKILL.md`와 `references/` 중심으로 추가한다. 기본 실행 산출물은
`*-executed.ipynb` 형태를 권장하되, 프로젝트 정책이나 사용자 요청이 있으면
그쪽을 따른다. Temporary dependency 예시는 `references/project-execution.md`와
`references/review.md`에 제한적으로 둔다.

## 참고 자료

- [nbformat: The Jupyter Notebook Format](https://nbformat.readthedocs.io/en/latest/format_description.html)
- [nbformat Python API](https://nbformat.readthedocs.io/en/latest/api.html)
- [nbclient: Executing notebooks](https://nbclient.readthedocs.io/en/latest/client.html)
- [Jupytext](https://github.com/mwouts/jupytext)
- [nbdime](https://nbdime.readthedocs.io/en/latest/)
- [nbstripout](https://github.com/kynan/nbstripout)
