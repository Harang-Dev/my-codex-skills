# my-codex-skills

Personal Codex skills managed from one private GitHub repository.

The repository is the source of truth. Each directory in `skills/` is linked into
`~/.codex/skills/`, which is the local Codex skills directory used by this
environment. Codex built-in and plugin-provided skills are intentionally not
managed here.

## Layout

```
skills/<skill-name>/SKILL.md  # A managed Codex skill
bin/install                   # Link skills into the local Codex directory
bin/update                    # Fast-forward the repository and refresh links
bin/uninstall                 # Remove managed links only
```

## Use

Clone the private repository with SSH, then install every skill:

```bash
git clone git@github.com:Harang-Dev/my-codex-skills.git \
  "$HOME/.local/share/my-codex-skills"
"$HOME/.local/share/my-codex-skills/bin/install"
```

Install only selected skills by name:

```bash
"$HOME/.local/share/my-codex-skills/bin/install" hw-pr-review hw-write-pr
```

Update the checkout and refresh all managed links:

```bash
"$HOME/.local/share/my-codex-skills/bin/update"
```

Remove managed links without deleting the repository:

```bash
"$HOME/.local/share/my-codex-skills/bin/uninstall" hw-pr-review
```

`bin/install` never overwrites an existing real directory in the target skills
directory. Move, rename, or remove that directory deliberately before retrying.

After pulling an update, restart Codex if the changed skill is not discovered.
