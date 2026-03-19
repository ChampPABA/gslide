## Purpose

Provides the `gslide` command-line interface with `auth` and `gen` command groups, argument parsing, and consistent exit codes.

## Requirements

### Requirement: CLI entry point with auth and gen command groups
The system SHALL provide a `gslide` CLI with two command groups: `auth` and `gen`.

#### Scenario: Help output
- **WHEN** user runs `gslide --help`
- **THEN** system shows available command groups: `auth`, `gen`

#### Scenario: Auth commands
- **WHEN** user runs `gslide auth --help`
- **THEN** system shows subcommands: `login`, `status`, `logout`

#### Scenario: Gen commands
- **WHEN** user runs `gslide gen --help`
- **THEN** system shows subcommands: `slide`, `infographic`, `image`, `batch`

### Requirement: Gen commands accept presentation and prompt arguments
The system SHALL accept `--presentation` (required) and `--prompt` (required) for single gen commands.

#### Scenario: Gen infographic with arguments
- **WHEN** user runs `gslide gen infographic --presentation ID --prompt "text"`
- **THEN** system passes presentation ID and prompt to the gen-slide module

#### Scenario: Gen image with extra arguments
- **WHEN** user runs `gslide gen image --presentation ID --prompt "text" --slide-index 3 --insert-as background`
- **THEN** system passes all arguments including slide-index and insert-as to the gen module

#### Scenario: Missing required argument
- **WHEN** user runs `gslide gen infographic` without --presentation
- **THEN** system prints error "Missing option '--presentation'" and exits with code 2

### Requirement: Gen batch accepts file argument
The system SHALL accept `--file` (required) for batch generation.

#### Scenario: Batch with file
- **WHEN** user runs `gslide gen batch --file prompts.json`
- **THEN** system loads and validates the file then starts batch generation

#### Scenario: Batch with optional flags
- **WHEN** user runs `gslide gen batch --file p.json --continue-on-error --dry-run`
- **THEN** system respects both flags

### Requirement: Timeout configuration
The system SHALL accept `--timeout` flag (default 120 seconds) for gen commands.

#### Scenario: Custom timeout
- **WHEN** user runs `gslide gen infographic --presentation ID --prompt "..." --timeout 120`
- **THEN** system waits up to 120 seconds for generation to complete

### Requirement: Exit codes
The system SHALL use consistent exit codes.

#### Scenario: Success
- **WHEN** command completes successfully
- **THEN** exit code is 0

#### Scenario: User error
- **WHEN** command fails due to invalid arguments or missing auth
- **THEN** exit code is 1

#### Scenario: Generation error
- **WHEN** command fails due to generation timeout or browser error
- **THEN** exit code is 2
