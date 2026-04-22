# CHANGELOG


## v0.5.3 (2026-04-22)

### Bug Fixes

- **docs**: Update docs based on latest updates
  ([`90fd43f`](https://github.com/justmatias/fauth/commit/90fd43f0ffef6ddb0f296ba13936a84acda89149))


## v0.5.2 (2026-04-22)

### Bug Fixes

- Export create_password_reset_token in package init
  ([#42](https://github.com/justmatias/fauth/pull/42),
  [`ee20e8a`](https://github.com/justmatias/fauth/commit/ee20e8a1fdd708bd59b0ff1ace2d36a84c2324f5))


## v0.5.1 (2026-04-22)

### Bug Fixes

- Abstract token verification into a reusable method
  ([#41](https://github.com/justmatias/fauth/pull/41),
  [`b9850d8`](https://github.com/justmatias/fauth/commit/b9850d84d8f17ef8cc3af33287077436808fc187))


## v0.5.0 (2026-04-21)

### Features

- Add password reset token support and improve JWT validation with type enforcement
  ([#40](https://github.com/justmatias/fauth/pull/40),
  [`b688ea1`](https://github.com/justmatias/fauth/commit/b688ea1ff2eab66183665048fb2c42256cd793c7))


## v0.4.2 (2026-04-18)

### Bug Fixes

- Update require_roles to support singular role fields and enum types with regression tests
  ([#39](https://github.com/justmatias/fauth/pull/39),
  [`0d2c646`](https://github.com/justmatias/fauth/commit/0d2c646729fcfffe9e10b047e117636b97530620))


## v0.4.1 (2026-04-18)

### Bug Fixes

- **ci**: Prevent shell injection in GitHub Actions workflow
  ([#37](https://github.com/justmatias/fauth/pull/37),
  [`11835f1`](https://github.com/justmatias/fauth/commit/11835f16cedd3f064c9ffe2df26f02a53f9b81f9))

Fix potential shell injection vulnerability in CI/CD workflow by avoiding GitHub expression
  interpolation.

## Changes - Removed `env:` block that used `${{ github.head_ref || github.ref_name }}`
  interpolation - Changed git push command to use GitHub's built-in environment variables
  (`GITHUB_HEAD_REF` and `GITHUB_REF_NAME`) directly in the shell - Properly quoted the variable to
  prevent word splitting

## Why Using `${{ }}` expression interpolation with `github.head_ref` in a workflow step can be
  exploited by attackers who create pull requests with maliciously crafted branch names. By using
  the shell environment variables `GITHUB_HEAD_REF` and `GITHUB_REF_NAME` (which GitHub Actions
  automatically provides), we avoid the expression interpolation while maintaining the same
  functionality. The shell handles these variables safely when properly quoted.

## Semgrep Finding Details Using variable interpolation `${{...}}` with `github` context data in a
  `run:` step could allow an attacker to inject their own code into the runner. This would allow
  them to steal secrets and code. `github` context data can have arbitrary user input and should be
  treated as untrusted. Instead, use an intermediate environment variable with `env:` to store the
  data and use the environment variable in the `run:` script. Be sure to use double-quotes the
  environment variable, like this: "$ENVVAR".

Semgrep Assistant generated this pull request to fix [a
  finding](https://semgrep.dev/orgs/justmatias/findings/756619268) from the detection rule
  [yaml.github-actions.security.run-shell-injection.run-shell-injection](https://semgrep.dev/r/yaml.github-actions.security.run-shell-injection.run-shell-injection).

Co-authored-by: Semgrep Autofix <autofix@semgrep.com>

### Chores

- Add Snyk and Semgrep security scanning workflows
  ([#35](https://github.com/justmatias/fauth/pull/35),
  [`768b38b`](https://github.com/justmatias/fauth/commit/768b38b2880b9a52cb8a7d8d3a5c6200dc456db9))

* ci: add Snyk and Semgrep security scanning workflows

* chore(config): update pre-commit hooks

* chore: update autotrigger

* chore: change semgrep metrics option from off to auto

* ci: fix shell injection vulnerability in cicd workflow

---------

Co-authored-by: github-actions[bot] <github-actions[bot]@users.noreply.github.com>

- Remove pre-commit autoupdate workflow ([#36](https://github.com/justmatias/fauth/pull/36),
  [`7022909`](https://github.com/justmatias/fauth/commit/7022909b390658add76bb9bf767b0fdf9fcf4657))


## v0.4.0 (2026-04-15)

### Chores

- Add pragma no cover to auth middleware fallback paths
  ([`cd3c090`](https://github.com/justmatias/fauth/commit/cd3c09037e7459126c01310c34b09ea2e7f4ece0))

### Features

- Implement token refresh functionality in AuthProvider with associated tests
  ([`d597d8f`](https://github.com/justmatias/fauth/commit/d597d8ff96a240c502755e4fc80e7ef316121713))


## v0.3.1 (2026-04-15)

### Bug Fixes

- Add py.typed marker to enable type checking support
  ([`1787519`](https://github.com/justmatias/fauth/commit/1787519027c7dfd6e57e1fddad45b7cdffe97e48))


## v0.3.0 (2026-04-15)

### Bug Fixes

- Correct typo in pylint disable directive within auth middleware
  ([`bc06572`](https://github.com/justmatias/fauth/commit/bc0657237d634e604eaa6be046fbc68fa86a8396))

### Chores

- Disable pylint complexity checks for auth middleware dispatch method
  ([`7c335aa`](https://github.com/justmatias/fauth/commit/7c335aa3165bd5de2234084b6df6a9361f815922))

- **config**: Update pre-commit hooks
  ([`34ca640`](https://github.com/justmatias/fauth/commit/34ca64099763b3d5faca1c1a2b56673584c4c321))

- **config**: Update pre-commit hooks
  ([`e6225f9`](https://github.com/justmatias/fauth/commit/e6225f946ef5a3f89c6a15cd490656bdb57f3425))

- **deps**: Bump cryptography from 46.0.6 to 46.0.7
  ([`c57f70f`](https://github.com/justmatias/fauth/commit/c57f70f21998cb49b83673cc7c47e8c3826dc65c))

Bumps [cryptography](https://github.com/pyca/cryptography) from 46.0.6 to 46.0.7. -
  [Changelog](https://github.com/pyca/cryptography/blob/main/CHANGELOG.rst) -
  [Commits](https://github.com/pyca/cryptography/compare/46.0.6...46.0.7)

--- updated-dependencies: - dependency-name: cryptography dependency-version: 46.0.7

dependency-type: indirect ...

Signed-off-by: dependabot[bot] <support@github.com>

- **deps**: Bump pygments from 2.19.2 to 2.20.0
  ([`c022333`](https://github.com/justmatias/fauth/commit/c022333b5f61003c07242810126fec443bd93a91))

Bumps [pygments](https://github.com/pygments/pygments) from 2.19.2 to 2.20.0. - [Release
  notes](https://github.com/pygments/pygments/releases) -
  [Changelog](https://github.com/pygments/pygments/blob/master/CHANGES) -
  [Commits](https://github.com/pygments/pygments/compare/2.19.2...2.20.0)

--- updated-dependencies: - dependency-name: pygments dependency-version: 2.20.0

dependency-type: indirect ...

Signed-off-by: dependabot[bot] <support@github.com>

- **deps**: Bump pyjwt from 2.11.0 to 2.12.0
  ([`0c443a9`](https://github.com/justmatias/fauth/commit/0c443a92b921cea23f1ac71ba837fc335fed183f))

Bumps [pyjwt](https://github.com/jpadilla/pyjwt) from 2.11.0 to 2.12.0. - [Release
  notes](https://github.com/jpadilla/pyjwt/releases) -
  [Changelog](https://github.com/jpadilla/pyjwt/blob/master/CHANGELOG.rst) -
  [Commits](https://github.com/jpadilla/pyjwt/compare/2.11.0...2.12.0)

--- updated-dependencies: - dependency-name: pyjwt dependency-version: 2.12.0

dependency-type: indirect ...

Signed-off-by: dependabot[bot] <support@github.com>

- **deps-dev**: Bump pytest from 9.0.2 to 9.0.3
  ([`f1372ad`](https://github.com/justmatias/fauth/commit/f1372addbf826fe305623d713cb492ee51e6ced8))

Bumps [pytest](https://github.com/pytest-dev/pytest) from 9.0.2 to 9.0.3. - [Release
  notes](https://github.com/pytest-dev/pytest/releases) -
  [Changelog](https://github.com/pytest-dev/pytest/blob/main/CHANGELOG.rst) -
  [Commits](https://github.com/pytest-dev/pytest/compare/9.0.2...9.0.3)

--- updated-dependencies: - dependency-name: pytest dependency-version: 9.0.3

dependency-type: direct:development ...

Signed-off-by: dependabot[bot] <support@github.com>

### Features

- Implement AuthMiddleware for JWT-based request authentication and user loading
  ([`0527038`](https://github.com/justmatias/fauth/commit/0527038d3f5e897fc77258820a26c062d3fc075e))


## v0.2.2 (2026-04-04)

### Bug Fixes

- Add badge for dependabot
  ([`22f4719`](https://github.com/justmatias/fauth/commit/22f47195a489fbd9a63f5772c1081b887a2b0ea1))

### Chores

- Add python version matrix to CI/CD workflow
  ([`9576512`](https://github.com/justmatias/fauth/commit/9576512733ed709c9bce62a97101d397a010ace8))

- Fix cicd for dependabot prs
  ([`befb729`](https://github.com/justmatias/fauth/commit/befb729fca3e37ba23c5158b29659f712455f6ac))

- Implement setup env action and remove legacy requirements.txt
  ([`781a552`](https://github.com/justmatias/fauth/commit/781a552e29c3d658247762c5cf13bb66042976fb))

- Remove extract curly brace
  ([`2661dd3`](https://github.com/justmatias/fauth/commit/2661dd3f94da79909fa900d6d6dc341e199f5bb4))

- Restore checkout step in jobs
  ([`ad4e33d`](https://github.com/justmatias/fauth/commit/ad4e33d1b2575f368b7cb256c1bf9d34b52855dd))

- Set python version to min supported
  ([`8c981a4`](https://github.com/justmatias/fauth/commit/8c981a40939df8230ba1f776cf1dc6f57090ebad))

- **config**: Update pre-commit hooks
  ([`ab09f61`](https://github.com/justmatias/fauth/commit/ab09f6185058cece84ddf5ef371b268b7fb75429))

- **config**: Update pre-commit hooks
  ([`6ec7a6d`](https://github.com/justmatias/fauth/commit/6ec7a6de9c618d1d5bf8b0f157d52888346f49a1))

- **config**: Update requirements.txt
  ([`862978f`](https://github.com/justmatias/fauth/commit/862978f8073c065086b3080dafc45e3b604b98ce))

- **deps**: Bump cryptography from 46.0.5 to 46.0.6
  ([`a61129d`](https://github.com/justmatias/fauth/commit/a61129df6777736ecff5df4c1a878a70b378025d))

Bumps [cryptography](https://github.com/pyca/cryptography) from 46.0.5 to 46.0.6. -
  [Changelog](https://github.com/pyca/cryptography/blob/main/CHANGELOG.rst) -
  [Commits](https://github.com/pyca/cryptography/compare/46.0.5...46.0.6)

--- updated-dependencies: - dependency-name: cryptography dependency-version: 46.0.6

dependency-type: indirect ...

Signed-off-by: dependabot[bot] <support@github.com>


## v0.2.1 (2026-04-03)

### Bug Fixes

- Implement AuthProvider for FastAPI authentication and add testing utilities
  ([`f19f7ad`](https://github.com/justmatias/fauth/commit/f19f7ad32a8a79368d50862ffa3f4446dcc2cc70))

### Chores

- **config**: Merge with main
  ([`d8caae2`](https://github.com/justmatias/fauth/commit/d8caae2b3e357fcc2b3bc5f78c2929c1d0b12427))


## v0.2.0 (2026-04-02)

### Bug Fixes

- **config**: Add logs and update docs
  ([`9d9e733`](https://github.com/justmatias/fauth/commit/9d9e7333dc8c541c41d5a80c3bf7bde52ad1f159))

### Chores

- **config**: Update pre-commit hooks
  ([`f4098cd`](https://github.com/justmatias/fauth/commit/f4098cda011496566cc751305ac7952f4469df03))

- **config**: Update requirements.txt
  ([`1bef7cc`](https://github.com/justmatias/fauth/commit/1bef7cc6aa3ee9026165ad5bb3e48fc526b853ab))

- **docs**: Clarify structlog configuration requirements
  ([`9f685cb`](https://github.com/justmatias/fauth/commit/9f685cb8b0190c0b7c9b8ca665b25f4e5816af36))

- **docs**: Update project dependencies in pyproject.toml
  ([`d49cdbf`](https://github.com/justmatias/fauth/commit/d49cdbf979d63a6b2fbe895c43984c96ae4b721d))

### Features

- **config**: Implement structured logging utility using structlog
  ([`d87f777`](https://github.com/justmatias/fauth/commit/d87f777795f85e3f2856ad937728f594bc4cc3c1))


## v0.1.2 (2026-04-01)

### Bug Fixes

- **config**: Add authenticate method to AuthProvider with IdentityLoader support
  ([`f905766`](https://github.com/justmatias/fauth/commit/f905766afa02394a28f97b319e52134576c4c614))

- **config**: Add openapi security scheme support to AuthProvider and router dependencies
  ([`72d7754`](https://github.com/justmatias/fauth/commit/72d7754fb0519be979b6b00b5f253b245770698c))

### Chores

- **docs**: Update readme
  ([`892ea31`](https://github.com/justmatias/fauth/commit/892ea31dcae32aabd7f3d935a2579a1809ed12e4))


## v0.1.1 (2026-04-01)

### Bug Fixes

- **config**: Simplify dependency injection by using direct method references
  ([`4438d9e`](https://github.com/justmatias/fauth/commit/4438d9eed561f98e08bc702be0a6a9c132cb5b6b))

### Chores

- **config**: Update pre-commit hooks
  ([`8f9c9d8`](https://github.com/justmatias/fauth/commit/8f9c9d854a83913b0860b0e9dc2f12ed6f386ef7))


## v0.1.0 (2026-03-29)

### Bug Fixes

- Add tests for core and api modules
  ([`cb6ed8a`](https://github.com/justmatias/fauth/commit/cb6ed8aabca0e4de41054cfd1857e1f41973d55c))

- Add tests for create_access_token
  ([`eae2201`](https://github.com/justmatias/fauth/commit/eae22013a94a56e931fbd2ba21f1800b90a4fd29))

- Add tests for jwt utilities and password utilities.
  ([`23f6345`](https://github.com/justmatias/fauth/commit/23f6345412be42eb6377f3bd008e4c0700b29ccb))

- Add unit tests and fixtures for the authentication provider.
  ([`e81e447`](https://github.com/justmatias/fauth/commit/e81e447391307df431a419439b30c46ab6f3f0cd))

### Chores

- Add polyfactory as new development dependencies.
  ([`e36e895`](https://github.com/justmatias/fauth/commit/e36e895fff0843218efcf425c75bb6ed66e29ad6))

- Add pypi publishing job
  ([`e8f5ba0`](https://github.com/justmatias/fauth/commit/e8f5ba07326dd058ed7df1f3881a7831ba563392))

- Fix lint issues
  ([`8e18b2f`](https://github.com/justmatias/fauth/commit/8e18b2f4d093a05f897033c97241158dab727100))

- Improve type hints, update dependencies, and apply minor stylistic adjustments across several
  modules
  ([`1d55d31`](https://github.com/justmatias/fauth/commit/1d55d31cb7bd143dc353a44628c6f3575e571420))

- Restructure main package
  ([`f0d7236`](https://github.com/justmatias/fauth/commit/f0d723698da27d74cb7db9c7ca3a0ef2b1e129a2))

- **config**: Merge with main
  ([`c66d1eb`](https://github.com/justmatias/fauth/commit/c66d1eb612a2caebe790d20ce4a7f162ee49b6a4))

- **config**: Update pre-commit hooks
  ([`6d4ad4f`](https://github.com/justmatias/fauth/commit/6d4ad4f14f337adb73681226353829b19137c451))

- **config**: Update pre-commit hooks
  ([`77a8f95`](https://github.com/justmatias/fauth/commit/77a8f95d330ea0570a04ca8bd5bbccc72554e5e4))

- **config**: Update requirements.txt
  ([`13b718a`](https://github.com/justmatias/fauth/commit/13b718aae048d817191fe26a96b6fd964f59e82a))

- **config**: Update requirements.txt
  ([`08fed86`](https://github.com/justmatias/fauth/commit/08fed86e03f8bd6e3ec902dfc1d13225406be4a6))

- **config**: Update requirements.txt
  ([`ec11b90`](https://github.com/justmatias/fauth/commit/ec11b90eb30ab24a5b384c5b9662077fea46d903))

### Features

- Implement core authentication logic, transports, and testing utilities
  ([`7abbd34`](https://github.com/justmatias/fauth/commit/7abbd343405c93fc86de1c454b51c94a25b04774))


## v0.0.0 (2026-03-10)

### Chores

- Add initial project readme and detailed design plan
  ([`161b2e0`](https://github.com/justmatias/fauth/commit/161b2e0fa87b5b1d04d83496e50076362e9874f6))

- Introduce package and document new testing utilities including fakes and factories.
  ([`52f3299`](https://github.com/justmatias/fauth/commit/52f32998d9095d825d7a1059be535dd7121814e6))

- Update readme
  ([`1e50ee3`](https://github.com/justmatias/fauth/commit/1e50ee3d59747f19d9c54a85858c786d4a95cfbe))

- **config**: Initialize new fauth project with core structure, dependency management, CI/CD, and
  code quality tooling
  ([`0fe70cf`](https://github.com/justmatias/fauth/commit/0fe70cf7e453e404db44b64828ce5dc5bc440f73))
