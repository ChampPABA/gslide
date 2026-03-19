## Purpose
The system provides CI/CD automation via GitHub Actions to publish the npm package on version tag pushes with proper version synchronization.

## Requirements

### Requirement: GitHub Actions release workflow
The system SHALL provide a GitHub Actions workflow that publishes to npm on version tag push.

#### Scenario: Tag push triggers publish
- **WHEN** developer pushes tag matching `v*` pattern (e.g., `v0.2.0`)
- **THEN** GitHub Actions runs release workflow
- **THEN** workflow publishes package to npm as `@champpaba/gslide`

#### Scenario: Version sync between package.json and pyproject.toml
- **WHEN** release workflow runs
- **THEN** version in package.json matches the git tag
- **THEN** version in pyproject.toml matches the git tag

### Requirement: npm publish configuration
The system SHALL include proper npm publish configuration including scope and registry.

#### Scenario: Scoped package publish
- **WHEN** npm publish runs
- **THEN** package publishes to npmjs.com under @ChampPABA scope
- **THEN** package includes only necessary files (bin/, scripts/, src/, pyproject.toml)
