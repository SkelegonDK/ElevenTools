## ADDED Requirements

### Requirement: Template File Download
The system SHALL provide a download button for the bulk generation CSV template file on the Bulk Generation page.

#### Scenario: Template download button availability
- **WHEN** user navigates to the Bulk Generation page
- **THEN** a download button for the template CSV file is displayed
- **AND** the button is positioned near the CSV upload instructions for easy discovery

#### Scenario: Template file download
- **WHEN** user clicks the template download button
- **THEN** the system provides the `bulk_template.csv` file for download
- **AND** the downloaded file contains example data demonstrating proper CSV format with variables

#### Scenario: Template file format
- **WHEN** user downloads the template file
- **THEN** the file includes required columns (text, filename) and example variable columns
- **AND** the file demonstrates proper variable placeholder syntax ({variable_name}) in text content

