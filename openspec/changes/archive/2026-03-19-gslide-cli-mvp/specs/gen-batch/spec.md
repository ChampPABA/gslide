## ADDED Requirements

### Requirement: Load and validate prompts.json
The system SHALL load a prompts.json file and validate its structure before starting generation.

#### Scenario: Valid prompts file
- **WHEN** user provides a valid prompts.json with `presentation_id` and `slides` array
- **THEN** system validates all required fields exist (each slide has `tab` and `prompt`)
- **THEN** system validates `tab` values are one of: "slide", "infographic", "image"
- **THEN** system validates `images[]` entries have `target_slide`, `prompt`, and `insert_as` fields (if images array exists)

#### Scenario: Invalid prompts file
- **WHEN** prompts.json is missing required fields or has invalid tab values
- **THEN** system prints validation errors and exits with code 1 without launching browser

#### Scenario: Dry run validation
- **WHEN** user runs `gslide gen batch --file prompts.json --dry-run`
- **THEN** system validates the file and prints summary (slide count, tabs used) without generating

### Requirement: Batch slide generation with single browser session
The system SHALL generate all slides from prompts.json in a single browser session, keeping the panel open between generations.

#### Scenario: Full batch success
- **WHEN** prompts.json contains 6 slides and all generate successfully
- **THEN** system opens browser once, navigates to presentation
- **THEN** system opens "Help me visualize" panel once
- **THEN** for each slide: selects tab, types prompt, creates, waits, inserts
- **THEN** panel stays open between generations (no re-open needed)
- **THEN** after each insert, presses End key to return to last slide
- **THEN** prints progress for each slide: "[N/total] tab: prompt..." and "[N/total] done (Xs)"

#### Scenario: Batch with mixed tabs
- **WHEN** prompts.json contains slides with different tab values
- **THEN** system switches tabs as needed (only clicks tab when switching)

### Requirement: Batch image insertion after slides
The system SHALL process `images[]` array after all `slides[]` are generated, navigating to specific slides to insert images.

#### Scenario: Images inserted on target slides
- **WHEN** prompts.json has both `slides` and `images` arrays
- **THEN** system first generates all slides from `slides[]`
- **THEN** system processes `images[]`, navigating to each `target_slide` index
- **THEN** system generates and inserts each image on its target slide

### Requirement: Error recovery in batch
The system SHALL handle individual slide generation failures without aborting the entire batch.

#### Scenario: Partial failure with continue-on-error
- **WHEN** one slide fails to generate and `--continue-on-error` flag is set
- **THEN** system logs the error for that slide
- **THEN** system continues to next slide
- **THEN** final summary shows success/failure count and lists failed slides

#### Scenario: Failure without continue-on-error
- **WHEN** one slide fails to generate and `--continue-on-error` is NOT set
- **THEN** system aborts batch and prints progress so far plus the error

### Requirement: Batch completion summary
The system SHALL print a summary after batch completion.

#### Scenario: All slides generated
- **WHEN** batch completes (all or partial)
- **THEN** system prints: total slides generated, total time, failed slides (if any), and presentation URL
