# my-codex-skills

Personal Codex skills managed from one private GitHub repository.

The repository is the source of truth. Each directory in `skills/` is linked into
`~/.codex/skills/`, which is the local Codex skills directory used by this
environment. Codex built-in and plugin-provided skills are intentionally not
managed here.

## Daily workflow

Treat this repository like ordinary code:

1. Create a feature branch and edit the relevant `SKILL.md` or bundled resource.
2. Run `bin/skills doctor` locally.
3. Open a pull request. GitHub Actions validates the manifest and every skill's front matter.
4. Merge to `main`.
5. On another machine, run `bin/skills update`.

The existing local links immediately read the pulled skill files. Restart Codex only if a changed skill is not rediscovered.

## Layout

```
skills/<skill-name>/SKILL.md  # A managed Codex skill
bin/install                   # Link skills into the local Codex directory
bin/update                    # Fast-forward the repository and refresh links
bin/uninstall                 # Remove managed links only
bin/skills                    # Command-line entry point
scripts/validate-skills.sh    # Manifest and SKILL.md validation
manifest.json                 # Repository version and managed skill registry
```

## Use

Clone the private repository with SSH, then install every skill:

```bash
git clone git@github.com:Harang-Dev/my-codex-skills.git \
  "$HOME/.local/share/my-codex-skills"
"$HOME/.local/share/my-codex-skills/bin/skills" install
```

Install only selected skills by name:

```bash
"$HOME/.local/share/my-codex-skills/bin/skills" install hw-pr-review hw-write-pr
```

Update the checkout and refresh all managed links:

```bash
"$HOME/.local/share/my-codex-skills/bin/skills" update
```

Remove managed links without deleting the repository:

```bash
"$HOME/.local/share/my-codex-skills/bin/skills" remove hw-pr-review
```

`bin/install` never overwrites an existing real directory in the target skills
directory. Move, rename, or remove that directory deliberately before retrying.

Inspect the repository and local links at any time:

```bash
"$HOME/.local/share/my-codex-skills/bin/skills" doctor
"$HOME/.local/share/my-codex-skills/bin/skills" list
"$HOME/.local/share/my-codex-skills/bin/skills" version
```
