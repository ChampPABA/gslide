## ADDED Requirements

### Requirement: Skill file with frontmatter and CLI reference
The system SHALL provide a Claude Code skill file at `skills/gslide.md` with proper YAML frontmatter and complete CLI command reference.

#### Scenario: Skill file structure
- **WHEN** skill file is read by Claude Code
- **THEN** frontmatter contains name, description with trigger keywords
- **THEN** body contains all gslide CLI commands with usage examples
- **THEN** body contains workflow guidance for slide generation

### Requirement: Skill triggers on slide-related requests
The skill description SHALL trigger when users mention slide creation, presentation generation, or gslide-related keywords.

#### Scenario: Thai language trigger
- **WHEN** user says "ทำ slide", "สร้าง presentation", or "gen slide"
- **THEN** Claude activates gslide skill

#### Scenario: English trigger
- **WHEN** user says "make slides", "generate presentation", "create infographic"
- **THEN** Claude activates gslide skill

#### Scenario: Tool-specific trigger
- **WHEN** user mentions "gslide", "Help me visualize", or "Nano Banana"
- **THEN** Claude activates gslide skill

### Requirement: Pre-check for CLI installation
The skill SHALL instruct Claude to verify gslide is installed before attempting to use it.

#### Scenario: gslide not installed
- **WHEN** Claude checks and gslide CLI is not available
- **THEN** Claude tells user to run `npm install -g @ChampPABA/gslide`

#### Scenario: gslide installed but not logged in
- **WHEN** Claude checks and gslide is available but auth status fails
- **THEN** Claude tells user to run `gslide auth login`

### Requirement: skills.sh installer
The system SHALL provide a `skills.sh` script that installs both the npm package and copies the skill file.

#### Scenario: Full installation
- **WHEN** user runs `bash skills.sh`
- **THEN** script runs `npm install -g @ChampPABA/gslide`
- **THEN** script copies `skills/gslide.md` to `~/.claude/skills/gslide/SKILL.md`
- **THEN** script prints success message with next steps
