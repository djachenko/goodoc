# CHANGELOG

<!-- version list -->

## v1.4.1 (2026-07-21)

### Bug Fixes

- Install from PyPI with --force instead of git URL
  ([`c235975`](https://github.com/djachenko/goodoc/commit/c2359758d40c021b9ec1909e290a5b09326a488c))

- Reinstall on update by passing --force to pipx, remove outdated Quick Action path
  ([`ce35dee`](https://github.com/djachenko/goodoc/commit/ce35dee797b9d6b1f054bcefa76e1ba9583ef669))

- Show message instead of aborting when run without TTY
  ([`a252fff`](https://github.com/djachenko/goodoc/commit/a252fff3b8b619b4d28d4771b833ec51da3511a0))

- Workflow metadata and input type for Finder compatibility
  ([`8993c7d`](https://github.com/djachenko/goodoc/commit/8993c7db6f5e11d9b3d5db9b09c63332d8ccb400))

### Documentation

- Add status badges to README
  ([`9cf5164`](https://github.com/djachenko/goodoc/commit/9cf5164eb4ad276a9a91f56a881762fceb7327d1))


## v1.4.0 (2026-07-20)

### Code Style

- Extract filename constants, format long signatures
  ([`198449c`](https://github.com/djachenko/goodoc/commit/198449c51fdaa6ff47eab945c8227838174b7d0d))

- Extract method-level locals for repeated values
  ([`ff4b24e`](https://github.com/djachenko/goodoc/commit/ff4b24ea683d7df9a4baa95240f3ad470663c433))

- Inline filenames, remove module-level constants
  ([`ea606cb`](https://github.com/djachenko/goodoc/commit/ea606cb57ca6248124b976bd6e23ff45b99967b6))

- Multiline dict for all create_files calls
  ([`733d84c`](https://github.com/djachenko/goodoc/commit/733d84ca4082d9ed5acc913d280edbf4b90a0553))

- Vertical spacing and elif in create_files
  ([`d0369b1`](https://github.com/djachenko/goodoc/commit/d0369b16d3e4c5cd2170721231b7705740b9cc73))

### Features

- Validate file format before OAuth
  ([`e465c4b`](https://github.com/djachenko/goodoc/commit/e465c4b30e80876c7ad16f826077bb27d4277c45))

### Refactoring

- Extract validate() and add unit tests
  ([`9f084cf`](https://github.com/djachenko/goodoc/commit/9f084cf192e1f8ad24c909666aad2791de1f19bf))

- Extract validate_file() and add unit tests
  ([`fd83f03`](https://github.com/djachenko/goodoc/commit/fd83f039c9395ada18e4c970f236ce89f86589a2))

- Use create_files fixture for file setup in tests
  ([`0cef640`](https://github.com/djachenko/goodoc/commit/0cef64076d9d0a1d6a5d9172aeba86c4350edd66))


## v1.3.2 (2026-07-19)

### Bug Fixes

- Validate file existence before OAuth
  ([`c9ec411`](https://github.com/djachenko/goodoc/commit/c9ec4114eccbbc2e8a29b72504b6f56451f59f9a))


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
