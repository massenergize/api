# Massenergize Contributing Guide

Hi! We're thrilled that you'd like to contribute to this project. Your help is essential for keeping it great.
Before submitting your contribution though, please make sure to take a moment and read through the following guidelines.

## Table of Contents

- [Committing Changes](#committing-changes)
- [Commonly used NPM scripts](#commonly-used-npm-scripts)
- [Code of Conduct](#code-of-conduct)
- [Testing](https://github.com/massenergize/api/blob/master/README.md#testing)
- [Project Conventions](#project-convention)
- [Code Style](#code-style)
- [Pull Request Guidelines](#pull-request-guidelines)
- [Development Setup](#development-setup)
- [Project Structure](https://github.com/massenergize/api/blob/master/README.md/README.MD#project-structure)

### Pull Request Guidelines

- The `master` branch is basically just a snapshot of the latest stable release. All development should be done in
  dedicated branches. **DO NOT submit PRs against the `master` branch.**

- Checkout a topic branch from the relevant branch, e.g. `development`, and merge back against that branch.

- Work in the `src` folder and **DO NOT** check in virtual environment directories like `venv` in the commits.

- It's OK to have multiple small commits as you work on the PR - we will let GitHub automatically squash it before
  merging.

- Make sure ```bash make test``` passes. (
  see [https://github.com/massenergize/api/blob/master/README.md#development-setup](#development-setup))

- If adding new feature:
    - Add accompanying test cases.
    - Provide a convincing reason to add this feature. Ideally, you should open a suggestion issue first and have it
      _"green-lighted"_ before working on it.

- If fixing a bug:
    - If you are resolving a special issue, add `(fix #xxxx[,#xxx])` (#xxxx is the issue id) in your PR title for a
      better release log, e.g. `update entities encoding/decoding (fix #3899)`.
    - Provide a detailed description of the bug in the PR. Live demo preferred.
    - Add appropriate test coverage if applicable.

### Development Setup

Read the development setup section of the [README](

### Committing Changes

Commit messages should follow
the [commit message convention](https://github.com/Obsidian-Achernar/money-transfer-fr/blob/main/.github/COMMIT_CONVENTION.md)
so
that changelogs can be automatically generated. Commit messages will be automatically validated upon commit. If you are
not familiar with the commit message convention, you can use `npm run commit` instead of `git commit`, which provides an
interactive CLI for generating proper commit messages. You have to have husky installed to lint your commit messages.

### Commonly used make commands

``` bash
make test # runs all tests
make start # starts the development server
make celery # starts the celery worker
make migrate # runs remote migrations
make migrate-local # runs local migrations
```

Other commands can be found in the `Makefile` in the `src/` directory.

### What's in the project?

- **`.husky`**: contains [husky](https://typicode.github.io/husky/#/) configuration for git hooks.
- **`.github`**: contains GitHub related files, such as issue templates, PR templates, and contributing guidelines (this
  file) and workflows (AKA Github actions).
- **`docker-compose.yml`**: contains the configuration for the project's docker containers.
- **`Dockerfile.yml`**: contains the configuration for the project's docker containers.
- **`Makefile`**: contains commonly used commands for the project.
- **`src`**: contains the source code, obviously. The codebase is written in Python and uses the Django framework.
- **`requirements.txt`**: contains the dependencies for the project.
- **`api_version_canary`**: contains the API version canary for the project.
- **`api_version_dev`**: contains the API version canary for the project.
- **`api_version_prod`**: contains the API version canary for the project.



### Project Conventions



### Code Style

For the sake of consistency, We like to keep our code style uniform following the conventions outline in PEP 8.

- **Use the right casing for names**: Use:

+ **snake_case** for file names
+ **PascalCase** for classes
+ **UPPER_SNAKE_CASE** for constants, enums, config objects, config keys.
+ **snake_case** for variables, functions, methods, and modules.

- **Use the right spacing**:

+ Use 2 spaces for indentation. This is the standard in the JavaScript community.
+ Use 1 space before the opening bracket of an inline element.
+ Use 1 space before the opening bracket of function definitions.
+ Leave no space before the opening bracket of a function call.
+ Use 1 space after the colon in an object property.
+ Use 1 space before and after the arrow in an arrow function. This is for readability and consistency with the rest of
  the codebase.
+ Use 1 space before and after the equal sign in an assignment statement. This is for readability and consistency with
  the rest of the codebase.
+ Use reasonable vertical spacing to separate blocks and groups of code. This is to improve readability and avoid
  unnecessary scrolling.

- **Use descriptive identifiers (names of variables, functions classes etc.)**: This is to make the code more readable
  and
  understandable. This is especially important for variables that are used in complex expressions. For example, instead
  of using `a` and `b` for variables in a complex expression, use `total` and `discount` instead.

- **Importing modules**: We use the following convention for importing modules:
  Import modules in the following order:




### Code of Conduct

Please maintain a safe and respectful environment for all contributors and participants. We expect all contributors and
participants to abide by
our [Code of Conduct](https://github.com/massenergize/api/blob/master/.github/CODE_OF_CONDUCT.md)
