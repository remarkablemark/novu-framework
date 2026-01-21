# Contributing

Pull requests are welcome! By participating in this project, you agree to abide by our [code of conduct](https://github.com/remarkablemark/.github/blob/master/CODE_OF_CONDUCT.md).

## Fork

[Fork](https://github.com/remarkablemark/novu-framework/fork) and then clone the repository:

```sh
# replace <USER> with your username
git clone git@github.com:<USER>/novu-framework.git
```

```sh
cd novu-framework
```

## Install

Install [Python](https://www.python.org/):

```sh
brew install python
```

Create the virtual environment:

```sh
python3 -m venv .venv
```

Activate the virtual environment:

```sh
source .venv/bin/activate
```

Install the dependencies:

```sh
pip install -e '.[lint]'
```

Install pre-commit into your git hooks:

```sh
pre-commit install
```

## Develop

Make your changes, add tests/documentation, and ensure [tests](#test) pass.

Write a commit message that follows the [Conventional Commits](https://www.conventionalcommits.org/) specification:

- **feat**: A new feature
- **fix**: A bug fix
- **perf**: A code change that improves performance
- **refactor**: A code change that neither fixes a bug nor adds a feature
- **test**: Add missing tests or correct existing tests
- **build**: Changes that affect the build system or external dependencies
- **ci**: Updates configuration files and scripts for continuous integration
- **docs**: Documentation only changes

Push to your fork and create a [pull request](https://github.com/remarkablemark/novu-framework/compare/).

At this point, wait for us to review your pull request. We'll try to review pull requests within 1-3 business days. We may suggest changes, improvements, and/or alternatives.

Things that will improve the chance that your pull request will be accepted:

- [ ] Write tests that pass [CI](https://github.com/remarkablemark/novu-framework/actions/workflows/test.yml).
- [ ] Write solid documentation.
- [ ] Write a good [commit message](https://github.com/angular/angular/blob/main/CONTRIBUTING.md#commit).

## Spec-Driven Development

Using slash commands with your [AI agent](https://windsurf.com/):

1. `/speckit.constitution` - Establish project principles
2. `/speckit.specify` - Create baseline specification
3. `/speckit.plan` - Create implementation plan
4. `/speckit.tasks` - Generate actionable tasks
5. `/speckit.implement` - Execute implementation

Optional commands that you can use for your specs (_improve quality & confidence_):

- `/speckit.clarify` (_optional_) - Ask structured questions to de-risk ambiguous areas before planning (run before `/speckit.plan` if used)
- `/speckit.analyze` (_optional_) - Cross-artifact consistency & alignment report (after `/speckit.tasks`, before `/speckit.implement`)
- `/speckit.checklist` (_optional_) - Generate quality checklists to validate requirements completeness, clarity, and consistency (after `/speckit.plan`)

## Test

Install the dependencies:

```sh
pip install -e '.[test]'
```

Run the tests:

```sh
pytest
```

Run the tests with [coverage](https://coverage.readthedocs.io/):

```sh
coverage run -m pytest
```

Generate a coverage report:

```sh
coverage report
```

```sh
coverage html
```

## Lint

Install the dependencies:

```sh
pip install -e '.[lint]'
```

Update pre-commit hooks to the latest version:

```sh
pre-commit autoupdate
```

Run all pre-commit hooks:

```sh
pre-commit run --all-files
```

Lint all files in the current directory:

```sh
ruff check
```

Format all files in the current directory:

```sh
ruff format
```

## Build

Install the dependencies:

```sh
pip install -e '.[build]'
```

Generate distribution packages:

```sh
python3 -m build
```

Upload all of the archives under `dist`:

```sh
twine upload --repository testpypi dist/*
```

Install the package:

```sh
pip install --index-url https://test.pypi.org/simple/ --no-deps novu-framework
```

## Docs

Install the dependencies:

```sh
pip install -e '.[docs]'
```

Generate the docs with [pdoc](https://pdoc.dev/):

```sh
pdoc src/novu_framework/
```

## Release

Release and publish are automated with [Release Please](https://github.com/googleapis/release-please).

[Add a new pending publisher to PyPI.](https://pypi.org/manage/account/publishing/)
