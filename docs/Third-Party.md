# Third-party software and content

Everything this project uses but did not write, with its license. **Nothing listed here is
redistributed in this repo**: each piece is installed or downloaded separately. The IPS files in
`patches/` hold only patch bytes (28 and 511 bytes written), not the game.

Licenses were taken from each upstream's license file at the version this project uses (checked
2026-11-20), or from the installed package's metadata or copyright file for system and indirect
packages.

## The game (you supply it)

| What | Rights | Notes |
|---|---|---|
| *Beyond Castle Wolfenstein* (Muse Software, 1984) | Copyrighted; belongs to its rights holders | Not in the repo. The patches target the [4am crack](https://archive.org/details/Passport4am) (SHA-256 `5898ae8f...`). |
| Screenshots in `reference/` and `tools/refs/` | Frames from the game | Included to document the room and drive the emulator menus; not covered by this repo's MIT license. |

## Used to run the tools

| Software | Version used | License | Used for |
|---|---|---|---|
| [Python](https://www.python.org/) | 3.12 | [PSF-2.0](https://docs.python.org/3/license.html) | Patchers, `ips_apply.py`, `cp2_check.py`, tests |
| [Node.js](https://nodejs.org/) | 24 (22+ supported) | [MIT](https://github.com/nodejs/node/blob/main/LICENSE) | Bridge and control scripts, Node tests |
| [Apple2TS](https://github.com/ct6502/apple2ts) by Chris Torrence and contributors | web build 3.7.0 | [MIT](https://github.com/ct6502/apple2ts/blob/v3.7.0/LICENSE) | The emulator, run headless |
| [Apple2TS desktop app](https://github.com/ct6502/apple2ts-app) | 1.6.9 | [MIT](https://github.com/ct6502/apple2ts-app/blob/v1.6.9/LICENSE) | Source of the web build; playing by hand |
| [Chromium](https://www.chromium.org/) | distribution package | [BSD-3-Clause](https://chromium.googlesource.com/chromium/src/+/main/LICENSE) plus bundled components | Runs the Apple2TS web build headless |
| [CiderPress II](https://github.com/fadden/CiderPress2) by Andy McFadden (optional) | 1.2.0 | [Apache-2.0](https://github.com/fadden/CiderPress2/blob/v1.2.0/LICENSE) (images and docs CC BY-SA 4.0) | DOS 3.3 filesystem check in `tools/verify.sh` |

## Development and CI tools

| Software | Version | License | Used for |
|---|---|---|---|
| [ruff](https://github.com/astral-sh/ruff) | 0.17.5 | MIT | Python lint and format |
| [pip-audit](https://github.com/pypa/pip-audit) | 2.10.1 | Apache-2.0 | Python dependency audit |
| [ESLint](https://eslint.org/) (`eslint`, `@eslint/js`) | 10.15.0, 10.0.1 | MIT | JavaScript lint |
| [globals](https://github.com/sindresorhus/globals) | 17.14.0 | MIT | ESLint environment definitions |
| [Prettier](https://prettier.io/) | 3.10.1 | MIT | JavaScript format |
| [ShellCheck](https://www.shellcheck.net/) | 0.9.0 | GPL-3.0-or-later | Shell lint (run as a separate program; no code is copied) |
| [gitleaks](https://github.com/gitleaks/gitleaks) | 8.16 (distribution package) | MIT | Secret scan in the pre-commit hook |
| [actions/checkout](https://github.com/actions/checkout), [actions/setup-python](https://github.com/actions/setup-python), [actions/setup-node](https://github.com/actions/setup-node) | pinned SHAs in `.github/workflows/ci.yml` | MIT | CI |
| [CodeQL](https://codeql.github.com/) | GitHub default setup | [GitHub CodeQL Terms](https://github.com/github/codeql-cli-binaries/blob/main/LICENSE.md) (free for open-source code hosted on GitHub) | Code scanning |

The dev tools also pull in indirect dependencies (pinned in `package-lock.json` and
`requirements-dev.txt`). All are permissive (MIT, ISC, BSD, Apache-2.0, PSF, BlueOak-1.0.0) except
certifi, which is MPL-2.0 and used unmodified. None of them is shipped.

When you add a dependency or tool, add it here.
