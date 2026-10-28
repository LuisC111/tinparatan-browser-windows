# Tinparatan on Windows

Tinparatan is a personal build of [Helium](https://github.com/imputnet/helium).
This repository is the Windows packager. It stays a thin layer on
[imputnet/helium-windows](https://github.com/imputnet/helium-windows) so
`git merge upstream/main` stays small.

Upstream files are edited only where the build has to call into Tinparatan.
Those hooks are marked `Tinparatan (TINPARATAN.md)` in `build.py`. Everything
else lives in:

| Path | What it is |
| --- | --- |
| `helium-chromium` | Submodule. [LuisC111/tinparatan-browser](https://github.com/LuisC111/tinparatan-browser), not imputnet/helium. |
| `patches/tinparatan/windows/rebrand.patch` | Follow-up to Helium's `patches/helium/windows/change-branding.patch`. Appended at the end of `patches/series`. |
| `tinparatan/packaging.py` | Installer and zip file names, NSIS product defines, Authenticode description. |
| `.github/bump-hook.sh` | Stops the submodule bump if Tinparatan is not on the core repo's `main`. |

Helium's `patches/helium/windows/change-branding.patch` is not rewritten.
`resources/generate_resources.txt` still builds an intermediate ico from
Helium's `raw.png`. The copy below runs later and overwrites
`chrome/app/theme/chromium/win/chromium.ico`.

## Submodule

`.gitmodules` points `helium-chromium` at
`https://github.com/LuisC111/tinparatan-browser.git` and sets `branch = main`.

The recorded commit is `e2a3207226d9aa4e544f637d0f1256aebc18958f`, the head of
[PR #1](https://github.com/LuisC111/tinparatan-browser/pull/1)
(`cursor/tinparatan-rebrand-76c1`). That commit's parent is the fork's `main`
at the time of the PR (`58261a24341935be831fa3b97d31c46232c81b59`), so the PR
is a fast-forward of `main`.

`branch = main` is what `git submodule update --remote` and the bump workflow
follow. The pin is a specific commit so a clone today contains the rebrand
before the PR is merged. The temporary PR branch name is not stored. Deleting
`cursor/tinparatan-rebrand-76c1` after the merge does not change the submodule
URL.

After the PR lands:

- A merge commit or a rebase-merge keeps `e2a3207` in `main`'s history. Clones
  keep working. The next bump moves the pin forward along `main`.
- A squash merge creates a new commit with the same tree. GitHub still serves
  the old pull-request commit, so an existing pin still clones, but it is no
  longer on `main`. Move the pin to the squash commit (the commands in the
  sync section). The bump workflow refuses a `main` that does not contain
  `tinparatan/substitute_product_name.py`, so running it before the PR lands
  does not drop the rebrand.

## What the Windows patch changes

`patches/tinparatan/windows/rebrand.patch` applies after Helium's branding
patch and the updater glue. It sets:

- Install and profile directory `imput\Tinparatan` (`kCompanyPathName` stays
  `imput`, `kProductPathName` becomes `Tinparatan`)
- Shortcut and AppUserModelID `Tinparatan`
- ProgIDs `TinparatanHTM` / `TinparatanPDF` and their document descriptions
- A new app GUID `{38C54E82-5F4F-4AC4-A1DF-565207FF57D7}`, a separate Active
  Setup GUID, and new toast and elevator CLSIDs
- A new AppContainer SID prefix, so the sandbox does not share Helium's
- Policy registry key `SOFTWARE\Policies\Tinparatan` and the policy-template
  display name, so a Helium policy does not drive this browser
- Installer log `tinparatan_installer.log`
- WinSparkle's registry identity `imput` / `Tinparatan`, so "skip this version"
  is not shared with Helium

`installer/helium.nsi` still defaults to Helium. `package.py` passes
`-DPRODUCT_NAME=Tinparatan` and the new GUID, so the wizard, the version
resource, and the "Launch" path use `imput\Tinparatan`. The binary inside the
install is still `chrome.exe`.

Produced files:

```text
tinparatan_<version>_<arch>-installer.exe
tinparatan_<version>_<arch>-mini-installer.exe
tinparatan_<version>_<arch>-windows.zip
```

`<version>` is still Helium's version (`helium_version.py` plus
`revision.txt`). `<arch>` is `x64` or `arm64`.

## Left as Helium

These keep working only if the names stay the ones Helium's services expect.
The core repo's `TINPARATAN.md` lists the same set.

| Leave alone | Why |
| --- | --- |
| `direct_launch_url_scheme = "helium"` | Must match the `helium://` scheme registered in the core repo. `chrome://` is already rewritten to `helium://`. |
| `kSafeBrowsingName = "helium"` | Service id. Safe browsing is off. |
| `helium.7z`, `helium.packed.7z`, `Helium-bin`, archive prefix `helium` | Installer internals. The UI does not show them. Renaming one without the others breaks the mini installer. |
| `helium::GetBrowserUpdateURL` and the WinSparkle EdDSA key | The appcast host stays `updates.helium.computer`. Only the local WinSparkle registry name changes. |
| `https://services.helium.imput.net` and `helium.services.*` prefs | Not touched by this repo. The core patches leave the hosts alone. |
| `chrome.exe` and `helium_update_helper.exe` | Renaming the binaries is a separate packaging change. |
| Elevated tracing CLSID | Helium left Chromium's value. It is also referenced outside this header. A new value only in the follow-up patch can disagree with that IDL, so it is unchanged. Helium already shares it with Chromium. The install directory, shortcuts, progids, GUIDs, toast and elevator classes, and the sandbox SID are distinct, which is what lets the two browsers install next to each other. |

## Syncing with upstream

Do the core repo first, then this one. The Windows patches apply on top of a
Chromium tree that the core repo's patches have already rewritten. Bumping
this submodule onto a core `main` that does not yet contain Tinparatan drops
the product name and the icons.

### 1. Core repo (`LuisC111/tinparatan-browser`)

```sh
git remote add upstream https://github.com/imputnet/helium.git   # once
git fetch upstream
git merge upstream/main
```

Expect a conflict only in `patches/series`, and only when upstream appends
patches. Keep every `tinparatan/` line at the bottom. Details are in that
repo's `TINPARATAN.md`. Push the result to this fork's `main`. Until
[PR #1](https://github.com/LuisC111/tinparatan-browser/pull/1) is merged, that
`main` does not contain the rebrand; merge the PR (a merge commit or
rebase-merge keeps the pinned commit reachable) before the next step.

### 2. This repo (`LuisC111/tinparatan-browser-windows`)

```sh
git remote add upstream https://github.com/imputnet/helium-windows.git   # once
git fetch upstream
git merge upstream/main
```

Keep our submodule URL and `branch = main`. Keep
`patches/tinparatan/windows/rebrand.patch` and its line at the bottom of
`patches/series`. Keep the `Tinparatan (TINPARATAN.md)` calls in `build.py`.
Likely conflicts: `.gitmodules`, `build.py`, `package.py`, `signing.py`,
`installer/helium.nsi`, `patches/series`, `README.md`, and the workflow files
under `.github/`.

Then move the submodule to the core fork's `main` (the line that now has both
upstream Helium and Tinparatan):

```sh
git -C helium-chromium fetch origin main
git -C helium-chromium checkout origin/main
test -f helium-chromium/tinparatan/substitute_product_name.py
git add helium-chromium
```

If the Chromium version moved, refresh this repo's patches. The manual quilt
steps are in the upstream README under "Updating patches and pruning list".
The dispatch workflow **Bump helium-chromium submodule to latest version**
does the same thing: it checks out the submodule's `origin/main` (this fork,
because `.gitmodules` says so), refreshes patches, and opens a PR. It uses
`GITHUB_TOKEN` unless a `GHPAT` secret is set. It stops immediately when
`tinparatan/substitute_product_name.py` is missing on that `main`.
`.github/bump-hook.sh` checks again before the commit. The bump action still
comes from `imputnet/helium-chromium` and commits as `helium-bot@imput.net`.
That is upstream's script; this fork only guards it.

Refresh `patches/tinparatan/windows/rebrand.patch` on its own if it fails.
Do not edit `patches/helium/` to make it apply.

## Building locally

A Tinparatan build is a Chromium build. Budget for it:

- Windows 10 22H2 or Windows 11, 64-bit, on the architecture you want
  (`x64`, or an ARM64 machine for the ARM64 build). Cross-compiling ARM64
  from x64 is what `python build.py --arm` does, and it clones Chromium
  instead of using the prepared x64 tarball, so it needs more disk.
- Visual Studio 2022 with the workload and Windows SDK from the
  [Chromium Windows build instructions](https://chromium.googlesource.com/chromium/src/+/refs/heads/main/docs/windows_build_instructions.md#visual-studio).
  The CI workflow installs Windows SDK 10.0.28000.0; it does not install
  Visual Studio.
- 32 GB of RAM is a comfortable floor. 16 GB meets Chromium's stated minimum
  and will spend a lot of the build swapping. The CI script allows about
  3 GB of RAM per compile job.
- 150 GB of free SSD for the source tree plus `out/Default`. A component
  build (`build.py --dev`) needs more.
- 8 cores or more. On a 4-core machine a release build takes long enough that
  a GitHub-hosted job will hit the 6 hour limit and have to resume.
- 7-Zip, Git, and Python 3.11 or newer with `requests` and `Pillow`.
- Windows Developer Mode (symlinks) and long paths enabled. The upstream
  README explains the Python alias and `MAX_PATH` steps. Do those.

In a **Developer Command Prompt for VS**, as administrator:

```bat
git clone --recurse-submodules https://github.com/LuisC111/tinparatan-browser-windows.git
cd tinparatan-browser-windows
python -m pip install requests Pillow
python build.py
python package.py
```

`build.py` downloads the Chromium tarball, applies Helium's patches, applies
this repo's patches (including `patches/tinparatan/windows/rebrand.patch`),
runs Helium's name substitution and translations, then:

1. `helium-chromium/tinparatan/substitute_product_name.py --sub -t build\src`
2. After `helium_resources.txt` is copied,
   `helium-chromium/resources/tinparatan/generate.py` and a copy of
   `tinparatan_resources.txt`, which replaces `chromium.ico`.

Packages land in `build\`. `python build.py --dev` skips the name and
translation passes, including the Tinparatan substitution, and waits for you
to apply patches with quilt. The resource copy still runs.

If a download fails, delete `build\download_cache` and run `build.py` again.
If it fails later, delete everything under `build` except `download_cache`.

## GitHub Actions

**Check patch series correctness** (`.github/workflows/lint.yml`) runs on
every push and pull request, on `ubuntu-latest`. It does not compile
Chromium. That is the workflow this fork can run unattended.

**Build and release binaries** is `workflow_dispatch` only.

| Input | Default | Meaning |
| --- | --- | --- |
| `runner` | `windows-2025` | Runner label. Change this to a self-hosted Windows runner. |
| `arch` | `x86_64` | `x86_64`, `arm64`, or `both`. |
| `sign` | off | Authenticode via Azure Trusted Signing. |
| `do-release` | off | Publish a prerelease after the build. |

Signing is off because this fork does not have imputnet's `AZURE_*` secrets.
With `sign` off, the package step runs `python package.py` and uploads
unsigned `tinparatan_*` artifacts. Turn `sign` on only after you add
`AZURE_TENANT_ID`, `AZURE_CLIENT_ID`, `AZURE_CLIENT_SECRET`,
`AZURE_SIGNING_ENDPOINT`, `AZURE_SIGNING_ACCOUNT`, and
`AZURE_SIGNING_CERTIFICATE_NAME`. `WINSPARKLE_ED_KEY` and
`WINSPARKLE_AUTHENTICODE_ORG` are repository variables. Without them the
browser builds, and the in-product updater stays disabled, which is the same
rule Helium uses.

`windows-2025` is GitHub's hosted image: 4 cores, 16 GB of RAM, and a 6 hour
job cap. The workflow chains up to 15 jobs so a slow machine can resume, which
is how Helium fits a build into hosted limits, but Helium's own builds run on
Depot runners this fork does not have. A hosted `windows-2025` job is likely
to run out of disk or time. Point `runner` at a self-hosted machine that
already has Visual Studio, 7-Zip, Git, and the hardware above, and register
the Actions runner with that label. The workflow copies the tree to
`C:\helium-windows`, installs Python and the Windows SDK, and builds there.

`do-release` publishes with the built-in `GITHUB_TOKEN`. It downloads
whichever of `tinparatan-x86_64` and `tinparatan-arm64` the build uploaded, so
a one-architecture run can still publish. The release is a prerelease. There
are no tags on this fork yet; the first release's notes say so instead of
calling `git describe`.

Depot, imputnet's Azure signing certificate, and a `GHPAT` secret are not
available here. The bump workflow falls back to `GITHUB_TOKEN`.

## What was checked

Checked in this change, without a Chromium checkout large enough to compile:

- `patches/tinparatan/windows/rebrand.patch` applies with `patch --fuzz=0`
  on Chromium 156.0.8078.73 after Helium's `change-branding.patch`, and on
  the WinSparkle glue file Helium's updater patch adds. A second apply does
  not match. The result keeps `direct_launch_url_scheme = "helium"`,
  `kSafeBrowsingName = "helium"`, `helium.7z`, and `Helium-bin`, and it
  calls `helium::GetBrowserUpdateURL` unchanged.
- `helium-chromium/devutils/lint.py -t .` and
  `devutils/check_patch_files.sh` pass on this repo's patch series.
- `tinparatan/substitute_product_name.py` imports and its own replacement
  examples pass. It was not run on a Chromium tree: that script refuses a
  directory without `OWNERS`, and the GRIT fingerprint pass needs Chromium's
  `tools/grit`.
- `resources/tinparatan/generate.py` was run with Pillow. The committed
  multi-size `win/app.ico` is a real icon (16, 24, 32, 48, 64, 128, 256).
  Regenerating did not change the submodule.
- `python tinparatan/packaging.py` checks the artifact names and that the
  installer GUID is not Helium's. `package.py` and `signing.py` import that
  module. `makensis` was not run, and no installer was produced.
- Workflow YAML parses, `actionlint` is clean, and
  `node --check` accepts `.github/actions/stage/index.js`.

Not checked: a compiled `chrome.exe`, the taskbar icon in a running browser,
the NSIS wizard, side-by-side install next to Helium, Authenticode signing,
or a GitHub-hosted or self-hosted Actions build.
