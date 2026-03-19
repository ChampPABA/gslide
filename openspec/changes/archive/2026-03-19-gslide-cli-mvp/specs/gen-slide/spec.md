## ADDED Requirements

### Requirement: Navigate to presentation and open panel
The system SHALL load the target presentation in a headless browser using saved storage state, navigate to the last slide, and open the "Help me visualize" panel.

#### Scenario: Successful navigation
- **WHEN** system receives a valid presentation ID and valid storage state
- **THEN** system navigates to `https://docs.google.com/presentation/d/{id}/edit`
- **THEN** system waits for Google Slides UI to load (filmstrip or canvas visible)
- **THEN** system presses End key to navigate to last slide
- **THEN** system clicks "Help me visualize" button
- **THEN** panel opens with tab selection and text input visible

#### Scenario: Session expired during navigation
- **WHEN** system loads presentation URL but gets redirected to login page
- **THEN** system exits with error "Session expired. Run: gslide auth login"

#### Scenario: Presentation not found
- **WHEN** presentation ID is invalid or user has no access
- **THEN** system exits with error "Cannot access presentation"

### Requirement: Generate via Infographic tab
The system SHALL select the Infographic tab, type the prompt, click Create, wait for generation, and insert as a new slide.

#### Scenario: Successful infographic generation
- **WHEN** user runs `gslide gen infographic --presentation ID --prompt "..."`
- **THEN** system selects "Infographic" tab in the panel
- **THEN** system types prompt into the text input
- **THEN** system clicks "Create" button
- **THEN** system waits for generation to complete (up to 120s default)
- **THEN** system clicks preview image to open insert overlay
- **THEN** system clicks "Insert on new slide" button
- **THEN** system waits for new slide to appear in filmstrip

#### Scenario: Generation timeout
- **WHEN** generation does not complete within timeout period
- **THEN** system exits with error "Generation timed out after {timeout}s"

### Requirement: Generate via Slide tab
The system SHALL select the Slide tab, type the prompt, click Create, wait for generation, and insert as a new slide via the dropdown.

#### Scenario: Successful slide generation
- **WHEN** user runs `gslide gen slide --presentation ID --prompt "..."`
- **THEN** system selects "Slide" tab in the panel
- **THEN** system types prompt into the text input
- **THEN** system clicks "Create" button
- **THEN** system waits for generation to complete
- **THEN** system clicks preview image to open insert overlay
- **THEN** system clicks "Insert on new slide" button
- **THEN** system waits for new slide to appear

### Requirement: Generate via Image tab
The system SHALL select the Image tab, type the prompt, click Create, wait for generation, select a preview, and insert onto the target slide.

#### Scenario: Successful image generation and insert
- **WHEN** user runs `gslide gen image --presentation ID --prompt "..." --slide-index N`
- **THEN** system navigates to slide at index N
- **THEN** system selects "Image" tab in the panel
- **THEN** system types prompt and clicks Create
- **THEN** system waits for preview thumbnails to appear (4-8 images)
- **THEN** system clicks preview image to open insert overlay
- **THEN** system clicks "Insert on new slide" button (with fallback to "Insert as image" or "Insert as background" if `--insert-as background`)

### Requirement: URL safety check
The system SHALL verify the browser URL matches the target presentation throughout the generation process.

#### Scenario: URL drift detected
- **WHEN** browser URL no longer contains the target presentation ID during any step
- **THEN** system aborts immediately with error "Browser navigated away from target presentation"
