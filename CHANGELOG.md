# CHANGELOG


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
