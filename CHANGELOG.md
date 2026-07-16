# CHANGELOG

<!-- version list -->

## v1.3.1 (2026-07-16)

### Bug Fixes

- Remove unused imports flagged by ruff
  ([`e747301`](https://github.com/djachenko/goodoc/commit/e7473019ea2871e10e99c917b8d0f3c8c1157047))

### Chores

- Drop Python 3.10 support
  ([`2b92b9a`](https://github.com/djachenko/goodoc/commit/2b92b9ae5862d3573cdf274e223fcf6e876a0a42))

- Ignore _claude symlink and to_delete dir
  ([`62807fd`](https://github.com/djachenko/goodoc/commit/62807fdb26c60230cf76eb943140a452fb1b1658))

### Refactoring

- Extract Config into config module
  ([`8ad3524`](https://github.com/djachenko/goodoc/commit/8ad35245a0c9390746d34ed947dd9075d9c4157a))

### Testing

- Add auth tests
  ([`85ab2a7`](https://github.com/djachenko/goodoc/commit/85ab2a73d512a8160a2601b1142998d4d9c6098c))

- Add CLI tests
  ([`d82d68e`](https://github.com/djachenko/goodoc/commit/d82d68e7849ff72da4060f0a607244401e2cd286))

- Add Config tests
  ([`3804a41`](https://github.com/djachenko/goodoc/commit/3804a41546c211932cd8992dd96e4f8524ff39cb))

- Add drive upload tests
  ([`9725850`](https://github.com/djachenko/goodoc/commit/97258502fef52702ff5034df06961dd956792ffc))

- Add test fixtures
  ([`a740dbb`](https://github.com/djachenko/goodoc/commit/a740dbb6ca66000944a4a7cf74f8ac90ad8186ff))

- Move mock_drive_build to class-level usefixtures
  ([`7533d7a`](https://github.com/djachenko/goodoc/commit/7533d7a39e0a93cdcff3e85ce0afc8b3ba3699f7))

- Update Config imports and fix instantiation
  ([`14d484a`](https://github.com/djachenko/goodoc/commit/14d484a29c94932626cef7e6519920d2c843d65c))


## v1.3.0 (2026-07-15)

### Chores

- Disable major version bump on zero
  ([`0690bb2`](https://github.com/djachenko/goodoc/commit/0690bb24b10f1c3a283f2a6001edef677cf3074e))

- Ignore CLAUDE.local.md
  ([`955bc73`](https://github.com/djachenko/goodoc/commit/955bc73e02d7691a1cecc7e64d34955e609c2fdd))

- Remove cliff.toml from gitignore, fix blank line before raise
  ([`7ebab41`](https://github.com/djachenko/goodoc/commit/7ebab41a12aa913544a21b8292c2563893a2542e))

### Features

- Accept multiple files
  ([`abd3382`](https://github.com/djachenko/goodoc/commit/abd3382e6a1a0c2fea6d3a808e5cc6c11c86c584))

### Refactoring

- Adopt XDG dirs, ship workflow template, extract shell integration
  ([`f185c7f`](https://github.com/djachenko/goodoc/commit/f185c7f999815dd455d50170648b58b8110bf3d1))


## v1.2.1 (2026-07-03)


## v1.2.0 (2026-07-03)


## v1.1.0 (2026-06-09)

### Bug Fixes

- Include .pptm in help text
  ([`e17e034`](https://github.com/djachenko/goodoc/commit/e17e03440fb7ca89f6ec4c2771a2b0884297c5c5))

### Documentation

- Add .pptm to all format references
  ([`31e0c1b`](https://github.com/djachenko/goodoc/commit/31e0c1b6d1f4d6c3ade5b237d0b5eb9de57934b3))


## v1.0.0 (2026-06-09)

- Initial Release
