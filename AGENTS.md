# Copilot Repository Instructions

This library is used to run a sequence of processes that run pure functions to modify a given state.

## Core Practices

1. Practice test-driven design.
- Write or update tests first to describe expected behavior.
- Implement the smallest code change needed to make tests pass.
- Refactor only after tests are green.

2. Always run linting and formatting checks after making changes.
- Run the project lint/format workflow after each change set.
- Resolve all actionable lint and formatting issues before finalizing work.

3. Always update documentation after changes.
- Update relevant docs (README, feature docs, developer notes, or inline docs) when behavior, interfaces, or workflows change.
- Keep examples and usage instructions aligned with current code.
- Ensure each file has a docstring describing its purpose and contents.
- Ensure each function/method has a docstring describing its purpose. If there are non standard parameters, describe them in the docstring. If the function returns a value, describe it in the docstring.

4. Always update the changelog with a structured list of changes.
- Add an entry for every completed change set.
- Use structured sections to improve readability and traceability.

## Changelog Entry Template

Use this structure whenever adding a changelog update:

- Date: YYYY-MM-DD
- Summary: One-line description
- Added:
  - ...
- Changed:
  - ...
- Fixed:
  - ...
- Docs:
  - ...
- Tests:
  - ...
- Lint/Format:
  - ...

## Definition of Done

A change is complete only when all are true:
- Tests are added/updated and passing.
- Linting and formatting checks are passing.
- Documentation is updated.
- Changelog includes a structured entry for the change.


## Required Workflow

1. Follow test-driven design for all behavior changes.
2. Write the code using the linting rules and formatting rules defined in the project.
3. Run linting and formatting checks after making changes.
4. Update relevant documentation after making changes.
5. Update the changelog using a structured list of changes.
6. Add the credits used for the request to the changelog entry.
7. Use best practices for the project domain
8. Use best practices for the programming language and framework used in the project.

## Enforcement Expectation

Treat work as incomplete until all of the following are done:
- Tests are added/updated and passing.
- Linting and formatting are passing.
- Documentation is updated.
- Changelog entry is added with structured sections.
- Check that best practice has been followed for the project domain and programming language/framework.

When responding, explicitly confirm completion of each requirement.

## Testing

- Use `.venv/bin/python -m pytest` for running all tests in the project.
