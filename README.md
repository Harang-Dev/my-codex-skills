# my-codex-skills

개인 Codex 스킬을 GitHub으로 관리하는 저장소입니다. `skills/` 아래의 각 스킬은 로컬 Codex 경로(`~/.codex/skills`)에 심볼릭 링크로 연결됩니다. 따라서 이 저장소의 변경을 받아오면 Codex가 바로 최신 스킬 파일을 사용합니다.

Codex 내장 스킬과 플러그인이 제공하는 스킬은 이 저장소에서 관리하지 않습니다.

## 처음 한 번: 설치하기

새 컴퓨터에서는 저장소를 clone한 뒤 모든 스킬을 설치합니다.

```bash
git clone git@github.com:Harang-Dev/my-codex-skills.git \
  "$HOME/.local/share/my-codex-skills"

"$HOME/.local/share/my-codex-skills/bin/hw-skills" install
```

매번 전체 경로를 쓰지 않도록 현재 터미널에서 별칭을 만들 수 있습니다.

```bash
alias hw-skills="$HOME/.local/share/my-codex-skills/bin/hw-skills"
```

이후 아래 예시에서는 이 별칭이 설정되어 있다고 가정합니다. 영구적으로 쓰려면 같은 `alias` 줄을 `~/.zshrc`에 추가하세요.

## 평소 작업 흐름

스킬도 일반 코드처럼 관리합니다.

```text
feature/fix 브랜치 생성 → 수정 → hw-skills doctor → PR → main 병합 → 다른 기기에서 hw-skills update
```

PR에서는 GitHub Actions가 `manifest.json`, 모든 `SKILL.md`의 YAML front matter, 그리고 스킬 경로를 자동으로 검증합니다.

## 1. 새 스킬을 만들고 올릴 때

먼저 최신 `main`에서 작업 브랜치를 만듭니다.

```bash
cd ~/.local/share/my-codex-skills
git switch main
git pull --ff-only
git switch -c feat/my-new-skill

mkdir -p skills/my-new-skill
```

`skills/my-new-skill/SKILL.md`를 만들고 최소 형식을 작성합니다.

```md
---
name: my-new-skill
description: Use when the user asks to ...
---

# My New Skill
```

그다음 `manifest.json`의 `skills`에 새 항목을 추가합니다.

```json
"my-new-skill": { "path": "skills/my-new-skill" }
```

검증하고 PR용 브랜치를 push합니다.

```bash
hw-skills doctor
git add skills/my-new-skill manifest.json
git commit -m "feat: add my new skill"
git push -u origin feat/my-new-skill
```

GitHub에서 PR을 만든 뒤 `main`에 병합합니다.

## 2. 기존 스킬을 수정할 때

```bash
cd ~/.local/share/my-codex-skills
git switch main
git pull --ff-only
git switch -c fix/improve-pr-review

# skills/hw-pr-review/SKILL.md 또는 해당 스킬의 리소스를 수정
hw-skills doctor

git add skills/hw-pr-review
git commit -m "fix: improve PR review guidance"
git push -u origin fix/improve-pr-review
```

수정도 새 스킬과 마찬가지로 PR을 만들고 병합합니다. 스킬 파일만 수정했다면 `manifest.json` 변경은 필요 없습니다.

## 3. 현재 기기에서 최신 스킬을 받을 때

```bash
hw-skills update
```

이 명령은 현재 브랜치를 `git pull --ff-only`으로 업데이트하고, 모든 스킬 심볼릭 링크를 확인합니다. 새 스킬이 추가된 경우에도 자동으로 설치됩니다.

## 4. 다른 곳에서 기존 스킬을 수정할 때

다른 컴퓨터도 동일합니다. 작업 전에 반드시 최신 `main`을 받아서 브랜치를 만드세요.

```bash
cd ~/.local/share/my-codex-skills
git switch main
git pull --ff-only
git switch -c fix/improve-pr-review
```

수정·검증·PR 과정은 2번과 같습니다. 같은 스킬을 동시에 수정했다면 PR 전에 최신 `main`을 반영하고 Git 충돌을 해결한 후 push하세요.

## 5. 다른 곳에서 새 스킬을 만들 때

처음 사용하는 컴퓨터라면 1회만 설치합니다.

```bash
git clone git@github.com:Harang-Dev/my-codex-skills.git \
  "$HOME/.local/share/my-codex-skills"
"$HOME/.local/share/my-codex-skills/bin/hw-skills" install
```

그 뒤 새 스킬 작성·manifest 등록·검증·PR은 1번과 동일합니다.

## 6. 다른 곳에서 최신 스킬을 받을 때

이미 설치한 컴퓨터에서는 한 줄이면 됩니다.

```bash
hw-skills update
```

변경된 스킬을 Codex가 바로 인식하지 않으면 Codex를 재시작하세요.

## 7. 자주 쓰는 명령과 주의점

```bash
hw-skills list                 # 스킬별 installed / conflict / not installed 상태 확인
hw-skills doctor               # repository, manifest, SKILL.md, 링크 상태 점검
hw-skills version              # manifest에 기록된 현재 버전 출력
hw-skills install hw-pr-review # 특정 스킬만 설치
hw-skills remove hw-pr-review  # 로컬 링크만 제거; 저장소 파일은 유지
```

- `main`에서 직접 수정하지 말고 `feat/...` 또는 `fix/...` 브랜치와 PR을 사용합니다.
- 새 스킬은 `skills/<이름>/SKILL.md`와 `manifest.json` 항목을 함께 추가합니다.
- PR 전에는 항상 `hw-skills doctor`를 실행합니다.
- `list`에서 `conflict`가 보이면 같은 이름의 실제 디렉터리 또는 다른 저장소의 링크가 이미 존재한다는 뜻입니다. 설치기는 이를 덮어쓰지 않으므로, 대상의 소유자를 확인한 뒤 직접 정리해야 합니다.
- `manifest.json`의 `version`은 기능 추가 시 minor(예: `1.0.0` → `1.1.0`), 작은 수정 시 patch(예: `1.0.0` → `1.0.1`)로 올리면 변경 이력을 파악하기 편합니다.

## 구성

```text
skills/<skill-name>/SKILL.md  관리하는 Codex 스킬
bin/hw-skills                 CLI 진입점
bin/install                   설치 구현
bin/update                    Git 업데이트 및 링크 갱신
bin/uninstall                 관리 중인 링크 제거
scripts/validate-skills.sh    manifest와 스킬 형식 검증
manifest.json                 버전과 스킬 목록
```
