# Changelog

## 2026-11-03

- Date: 2026-11-03
- Summary: Add node search controls to the process network web view.
- Added:
  - An accessible node search panel with a live count of visible nodes.
- Changed:
  - The web view hides nonmatching nodes and links connected to hidden nodes.
- Fixed:
  - None.
- Docs:
  - Documented how to run the web view and use its node filter.
- Tests:
  - Verified case-insensitive name matching, ID matching, edge filtering, and clearing the search in the browser.
  - Project tests passed: 116 passed, 7 skipped.
- Lint/Format:
  - Ruff checks and formatting checks passed for the related Python modules.
- Credits: Copilot SDK in VS Code.

## 2026-11-03

- Date: 2026-11-03
- Summary: Restructure the README as user-focused Python library documentation.
- Added:
  - A feature overview, installation instructions, and an end-to-end quick start.
  - Guidance on process inputs, outputs, state updates, API entry points, and development.
- Changed:
  - Reorganized the README into standard library documentation sections and replaced the
    outdated runner example.
- Fixed:
  - None.
- Docs:
  - Updated README.md to align examples and package requirements with the current API.
- Tests:
  - Not applicable; documentation-only change.
- Lint/Format:
  - Ruff checks run; not applicable to Markdown formatting.
- Credits: Copilot SDK in VS Code.

## 2026-11-02

- Date: 2026-11-02
- Summary: Require CI to pass before publishing tagged releases to PyPI.
- Added:
  - A reusable CI workflow dependency for the PyPI publishing job.
- Changed:
  - Updated release instructions to describe the CI gate.
- Fixed:
  - None.
- Docs:
  - Documented that failed CI prevents release publication.
- Tests:
  - Validated the publishing and CI workflow configuration.
- Lint/Format:
  - Not applicable to workflow and documentation files.
- Credits: Copilot SDK in VS Code.

## 2026-11-02

- Date: 2026-11-02
- Summary: Publish the package to PyPI when a version tag is pushed.
- Added:
  - A GitHub Actions workflow to build and publish distributions for version tags.
- Changed:
  - Replaced the manual distribution-build instructions with the automated release process.
- Fixed:
  - None.
- Docs:
  - Documented PyPI trusted-publisher configuration.
- Tests:
  - Validated the workflow configuration.
- Lint/Format:
  - Not applicable to workflow and documentation files.
- Credits: Copilot SDK in VS Code.
