# mmangkad's TLJH Fork

This is [Mohammad Miadh Angkad](https://github.com/mmangkad)'s fork of
[The Littlest JupyterHub](https://github.com/jupyterhub/the-littlest-jupyterhub).

## Quick install

```bash
curl -L https://raw.githubusercontent.com/mmangkad/the-littlest-jupyterhub/main/bootstrap/bootstrap.py \
  | sudo -E python3 - --admin <admin-user-name>
```

To install a specific version:

```bash
curl -L https://raw.githubusercontent.com/mmangkad/the-littlest-jupyterhub/main/bootstrap/bootstrap.py \
  | sudo -E python3 - --admin <admin-user-name> --version 2.0.1
```

## What's different from upstream

This fork makes TLJH track the **latest** versions of everything rather than pinning
to specific major releases. The philosophy: run bleeding-edge, fix issues as they
come, rather than staying on known-good old versions.

### Changes at a glance

| Area | Upstream | This fork |
|---|---|---|
| Python dependencies | Pinned (`jupyterhub>=5.2.0,<6` etc.) | Unpinned — always latest |
| Traefik | Pinned to specific version | Bumped regularly (currently 3.7.5) |
| Miniforge | Pinned to specific version | Bumped regularly (currently 26.3.2-3) |
| Bootstrap URLs | `jupyterhub/...` | `mmangkad/...` |
| Docs build deps | Pinned sphinx<6, myst-parser>=0.19 | Unpinned — always latest |

### Files modified (relative to upstream)

- `bootstrap/bootstrap.py` — fork URLs, logo URL
- `tljh/traefik.py` — traefik version + checksums
- `tljh/installer.py` — miniforge version + checksums, jupyterhub version parsing fix
- `tljh/requirements-hub-env.txt` — unpinned deps
- `tljh/requirements-user-env-extras.txt` — unpinned deps
- `setup.py` — unpinned deps
- `docs/requirements.txt` — unpinned deps

## For developers

### Branch structure

```
main  ←  rebased on upstream/main + fork changes on top
```

The `main` branch is kept rebased on `upstream/main`. All fork-specific changes
live in a single commit on top.

### Adding the upstream remote

```bash
git remote add upstream https://github.com/jupyterhub/the-littlest-jupyterhub.git
```

### Rebasing onto latest upstream

```bash
# Fetch latest upstream
git fetch upstream

# Rebase main onto upstream/main
git rebase upstream/main main

# Force-push to this fork
git push --force-with-lease origin main
```

If the rebase has conflicts:
1. Resolve them in the affected files
2. `git add` the resolved files
3. `git rebase --continue`
4. Push as above

### Updating versions (traefik, miniforge)

**Traefik:**
```bash
# Check latest release
curl -sL https://api.github.com/repos/traefik/traefik/releases/latest | jq -r .tag_name

# Get checksums
curl -sL "https://github.com/traefik/traefik/releases/download/$(curl -sL https://api.github.com/repos/traefik/traefik/releases/latest | jq -r .tag_name)/traefik_$(curl -sL https://api.github.com/repos/traefik/traefik/releases/latest | jq -r .tag_name)_checksums.txt" | grep linux

# Then update tljh/traefik.py:
#   - traefik_version = "X.Y.Z"
#   - checksums dict with new sha256 values
```

**Miniforge:**
```bash
# Check latest release
curl -sL https://api.github.com/repos/conda-forge/miniforge/releases/latest | jq -r .tag_name

# Get checksums
curl -sL "https://github.com/conda-forge/miniforge/releases/download/$(curl -sL https://api.github.com/repos/conda-forge/miniforge/releases/latest | jq -r .tag_name)/Miniforge3-$(curl -sL https://api.github.com/repos/conda-forge/miniforge/releases/latest | jq -r .tag_name)-Linux-x86_64.sh.sha256"
curl -sL "https://github.com/conda-forge/miniforge/releases/download/$(curl -sL https://api.github.com/repos/conda-forge/miniforge/releases/latest | jq -r .tag_name)/Miniforge3-$(curl -sL https://api.github.com/repos/conda-forge/miniforge/releases/latest | jq -r .tag_name)-Linux-aarch64.sh.sha256"

# Then update tljh/installer.py:
#   - MINIFORGE_VERSION = "X.Y.Z-N"
#   - MINIFORGE_CHECKSUMS dict with new sha256 values
```

### Tagging a new release

The bootstrap script resolves `latest` by looking at semver git tags. After
pushing changes to `main`, you must also create a tag:

```bash
git tag -a 2.0.2 -m "2.0.2: description of changes"
git push origin 2.0.2
```

Without this, `curl ... | python3 - --admin <user>` will install the **oldest**
tagged release instead of your latest main.

### Commit message format

- Version bumps: `bump: traefik X→Y, miniforge X→Y`
- Rebase merges: `upd` or `sync: rebase onto upstream/main`
- Other: keep it descriptive but short

## Known issues & fixes

### 1. "No MAJOR.MINOR.PATCH git tags found" during install

**Cause:** The fork has no semver git tags. The bootstrap script does
`git ls-remote --tags` against the fork and needs at least one tag matching
`MAJOR.MINOR.PATCH` format.

**Fix:**
```bash
# Fetch tags from upstream
git fetch upstream --tags

# Push them to the fork
git push origin --tags

# Also tag your latest commit
git tag -a 2.0.1 -m "description"
git push origin 2.0.1
```

### 2. GitHub push rejected: "private email address"

**Cause:** The commit author email is set to a private GitHub email that isn't
public in your GitHub settings.

**Fix:**
```bash
# Check what email the commit uses
git log -1 --format='%an <%ae>'

# If it's your private email, set the correct one
git config user.email "176301910+mmangkad@users.noreply.github.com"

# Amend the commit
git commit --amend --reset-author --no-edit

# Push
git push --force-with-lease origin main
```

You can find your GitHub noreply email at https://github.com/settings/emails.

### 3. Bootstrap installs old versions despite updated main

**Cause:** The bootstrap script resolves `latest` to the newest semver git tag.
If `main` has new commits but no new tag, it still installs the old tagged release.

**Fix:** Tag your latest main commit (see "Tagging a new release" above).

### 4. Upstream has moved on — your fork is stale

**Fix:** Follow the rebase procedure in "For developers" above. Always create a
backup branch first:

```bash
git branch backup-main-$(date +%Y%m%d)
```
