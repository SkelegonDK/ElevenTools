# Changelog

All notable changes to ElevenTools will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.0] - 2025-11-15

### Added
- Comprehensive testing suite with unit tests and Playwright UI tests covering all major components
- Ollama integration for local language model processing for voice design enhancements
- OpenRouter model selection with fuzzy search and free model filtering for translation customization
- API response caching for model fetching and other API calls using Streamlit caching for performance
- Dynamic model capability detection - automatically detects which voice settings each ElevenLabs model supports, adapting UI controls and validation dynamically
- Session-based file organization for privacy and isolation between users in multi-user cloud deployments
- Automatic cleanup of old session directories (default: 24 hours)
- Bulk download functionality for session files as ZIP archive
- File Explorer page for browsing and downloading generated audio files
- Settings page for secure API key management and default model configuration
- Support for speed control in voice settings (for compatible models)
- Support for Audio Tags in v3 models for enhanced expressiveness

### Changed
- Migrated from shared output directories to session-based file storage
- Improved API key management with session-based storage for cloud deployment
- Enhanced error handling and user feedback
- Updated UI to dynamically show/hide controls based on model capabilities

### Security
- Implemented path traversal prevention for all file operations
- Added input validation for CSV files, text input, and filenames
- Enhanced XSS prevention with HTML escaping
- Added memory leak prevention with session state limits
- Improved API key security with session-based storage

### Documentation
- Added comprehensive README with installation and usage instructions
- Created SECURITY.md documenting security measures
- Added testing documentation in docs/testing-core-suite.md
- Created CONTRIBUTING.md with development guidelines
- Added CHANGELOG.md for version history

## [Unreleased]

### Planned
- Additional test coverage improvements
- Performance optimizations
- Enhanced error messages
- Additional language support

---

[0.3.0]: https://github.com/SkelegonDK/ElevenTools/releases/tag/v0.3.0

