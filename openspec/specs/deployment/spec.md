# deployment Specification

## Purpose
TBD - created by archiving change remove-ci-streamlit-cloud-only. Update Purpose after archive.
## Requirements
### Requirement: Deployment Platform Support

The system SHALL support deployment exclusively on Streamlit Cloud for production use. Docker-based deployment SHALL remain available for local development, testing, and alternative hosting scenarios. The system SHALL NOT require continuous integration (CI) pipelines for Streamlit Cloud deployments, as Streamlit Cloud handles builds automatically.

#### Scenario: Streamlit Cloud deployment
- **WHEN** repository is connected to Streamlit Cloud
- **THEN** Streamlit Cloud automatically detects and deploys the application
- **AND** no CI/CD pipeline is required for deployment

#### Scenario: Local Docker development
- **WHEN** developer builds and runs the application using Docker
- **THEN** application starts successfully using `docker build` and `docker run` or `docker-compose up`
- **AND** application is accessible on configured port (default 8501)
- **AND** volume mounts work correctly for persistent data (outputs directory)

#### Scenario: Docker health checks
- **WHEN** application runs in Docker container
- **THEN** health check endpoint (`/_stcore/health`) is accessible
- **AND** Docker health check configuration functions correctly

