## MODIFIED Requirements

### Requirement: Error recovery in batch
The system SHALL handle individual slide generation failures without aborting the entire batch, detect mid-batch session expiry, and support resuming a partially completed batch.

#### Scenario: Session expiry detected mid-batch
- **WHEN** the Google session expires during a batch (page redirects to `accounts.google.com`)
- **THEN** system detects the redirect at the start of the next slide iteration
- **THEN** system aborts with a clear "session expired" error and prints a resume hint including `--start-from <N>`

#### Scenario: Resume from a given slide
- **WHEN** user runs `gslide gen batch --file prompts.json --start-from N`
- **THEN** system skips slides with index less than N (already inserted in the presentation)
- **THEN** system generates from slide N onward

#### Scenario: Partial failure with continue-on-error
- **WHEN** one slide fails to generate and `--continue-on-error` flag is set
- **THEN** system logs the error for that slide and saves a per-slide debug screenshot
- **THEN** system continues to next slide
- **THEN** final summary shows success/failure count and lists failed slides

#### Scenario: Failure without continue-on-error
- **WHEN** one slide fails to generate and `--continue-on-error` is NOT set
- **THEN** system aborts batch and prints progress so far, the error, and a resume hint with `--start-from <N>`
