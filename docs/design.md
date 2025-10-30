# ElevenTools Design Document

## Overview

ElevenTools is a comprehensive interface for ElevenLabs' text-to-speech API, designed to streamline the process of generating high-quality voice content. It provides both single and bulk generation capabilities, with advanced features for customization and reproducibility.

## Core Principles

1. User-Friendly: Intuitive interface for both novice and experienced users.
2. Flexibility: Support for various use cases, from single audio clips to large-scale batch processing.
3. Reproducibility: Consistent results through standardized voice settings and text processing.
4. Extensibility: Modular design to easily incorporate new features and integrations.
5. Cloud-Ready: Designed to run seamlessly in cloud environments with secure API key management.

## Architecture

### Frontend

- Streamlit-based web application with multi-page structure:
  * Main page (app.py): Advanced text-to-speech interface
  * Voice Design page: Voice creation and customization
  * Bulk Generation page: Batch processing of audio files
  * Translation page: Script translation capabilities
  * API Management page: Secure API key management
- Responsive design with sidebar for global settings
- Session state management for consistent user experience and secure API key storage

### Backend

- Python-based core logic
- Modular function structure for easy maintenance and extension
- API integration with ElevenLabs and OpenRouter
- Session-based API key management for secure cloud deployment

### Data Flow

1. User input (text, settings) → 
2. Processing (variable replacement, phonetic conversion) → 
3. API requests (ElevenLabs for TTS, OpenRouter for translations and phonetics) → 
4. Audio generation → 
5. Result presentation and storage

## Key Components

1. Voice and Model Selection
   - Dynamic fetching of available voices and models from ElevenLabs API
   - Voice generation from text descriptions
   - Voice preview system with instant playback
   - Voice ID management with copy functionality
   - Caching mechanism to reduce API calls

2. Text Processing
   - Variable replacement system for personalized content
   - Integration with OpenRouter for translations and phonetic conversions
   - Prompt enhancement for voice descriptions

3. Audio Generation
   - Single generation with immediate playback
   - Bulk generation from CSV files
   - Voice preview system with multiple voices

4. Settings Management
   - Voice settings (stability, similarity, style, speaker boost)
   - Global settings stored in session state for consistency across pages

5. Bulk Processing
   - CSV parsing and processing
   - Parallel generation of multiple audio files
   - Result aggregation and presentation

## Feature Details

1. Single Audio Generation (Main Page)
   - Text input with variable support
   - Real-time variable replacement
   - Phonetic conversion option
   - Immediate audio playback

2. Bulk Audio Generation (Bulk Generation Page)
   - CSV file upload for batch processing
   - Support for text variables in CSV
   - Bulk playback and optional download of generated audio

3. Voice Design Studio (Voice Design Page)
   - Interactive voice description input
   - AI-powered prompt enhancement
   - Predefined voice suggestions
   - Multi-column voice preview system
   - Voice ID copy functionality
   - Instant voice preview generation
   - Session state management for descriptions

4. Script Translation (Translation Page)
   - Multi-language support
   - Integration with OpenRouter for translations
   - Direct text input and output

5. Voice Customization
   - Adjustable parameters: stability, similarity, style
   - Speaker boost option
   - Voice generation from text descriptions
   - Voice preview system

## Technical Considerations

1. API Management
   - Secure handling of API keys through session state
   - Per-user API key storage for cloud deployment
   - Rate limiting and error handling for API requests
   - Integration with multiple APIs (ElevenLabs, OpenRouter)

2. Performance Optimization
   - Caching of frequently used data (models, voices)
   - Efficient handling of large CSV files for bulk processing
   - Optimized voice preview generation

3. Error Handling
   - Comprehensive error checking and user-friendly error messages
   - Logging for debugging and issue tracking

4. Scalability
   - Design considerations for handling increased load and larger datasets
   - Efficient voice generation and preview system

5. Testing
   - OpenRouter integration is fully tested, with all tests passing as of 2025-05-26 (see tests/test_api/test_openrouter_functions.py)

## Future Vision

1. Enhanced AI Integration
   - Deeper integration with language models for content generation and enhancement
   - Advanced voice generation from detailed descriptions
   - Multi-model support for different use cases

2. Advanced Audio Manipulation
   - Post-processing options for generated audio
   - Support for background music and sound effects
   - Voice style transfer and modification

3. Collaborative Features
   - Multi-user support with role-based access
   - Shared project spaces for team collaboration
   - Voice library sharing and management

4. Analytics and Insights
   - Usage statistics and performance metrics
   - AI-driven suggestions for optimal voice and settings selection
   - Voice quality assessment tools

5. Expanded Platform Support
   - Mobile app development
   - API endpoints for integration with other services
   - Cross-platform voice generation capabilities

## Voice Generation Features

1. Text-Based Voice Creation
   - Natural language description to voice generation
   - Multiple preview options for each description
   - Fine-tuning capabilities for generated voices

2. Voice Preview System
   - Real-time preview generation
   - Multiple voice variations from single description
   - Interactive preview comparison tools
   - Voice ID management and copying functionality

3. Voice Management
   - Voice library organization
   - Version control for voice iterations
   - Export and sharing capabilities

4. Voice Customization
   - Detailed voice characteristic controls
   - Style transfer between voices
   - Accent and dialect management

## File Explorer for Generated Audio

To improve usability and transparency, ElevenTools provides a built-in File Explorer for all generated audio files:

- **Output Organization:**
  - All generated audio (single and bulk) is consolidated in a single `outputs` folder.
  - **Bulk outputs** are grouped by the source CSV file used for generation. Each group is named after the CSV file.
  - **Single outputs** are stored in a separate folder within `outputs`, with filenames in the format `LANGUAGE_VOICE_NAME_DATE_ID` for easy identification.

- **File Explorer UI:**
  - Accessible from within the app, allowing users to browse, review, and manage all generated audio files.
  - **Bulk outputs** are displayed inside Streamlit expanders, each expander labeled with the CSV file name. Inside each expander, audio files are shown as rows with audio players and metadata (language, voice, date, ID, source CSV).
  - **Single outputs** are displayed as stacked rows (no expanders), each row showing an audio player and all relevant metadata.
  - All generation details are visible for each file, supporting transparency and reproducibility.
  - The UI is designed to be intuitive and responsive, supporting both novice and advanced users.

## Conclusion
ElevenTools aims to be the go-to solution for professional-grade text-to-speech generation, offering a perfect balance of simplicity and advanced features. By continually evolving based on user feedback and technological advancements, ElevenTools strives to remain at the forefront of voice synthesis technology.
