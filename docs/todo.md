# TODO List for Eleven Tools

## Active Tasks (Structured)

- [ ] [T1] Enhance UI/UX [Complexity: 6/10] [Priority: High] [Status: Pending]
  - Context: Improve user experience and interface consistency across the app.
  - Acceptance criteria: Progress bars for audio generation, improved error messaging, better navigation, and breadcrumb navigation are implemented.
  - Dependencies: []
  - Subtasks:
    - [ ] [T1.1] Implement progress bars for audio generation [Complexity: 2/10]
    - [ ] [T1.2] Improve error messaging and user feedback [Complexity: 1/10]
    - [ ] [T1.3] Improve navigation system [Complexity: 1/10]
    - [ ] [T1.4] Add breadcrumb navigation [Complexity: 1/10]
    - [ ] [T1.5] Implement consistent navigation patterns [Complexity: 1/10]
  - Estimated time: 2-3 days

- [ ] [T2] Optimize performance [Complexity: 5/10] [Priority: High] [Status: Pending]
  - Context: Improve speed and efficiency for key workflows, especially bulk and preview generation.
  - Acceptance criteria: Caching, optimized bulk generation, and faster voice preview generation are implemented.
  - Dependencies: []
  - Subtasks:
    - [ ] [T2.1] Implement caching for frequently used data [Complexity: 2/10]
    - [ ] [T2.2] Optimize bulk generation for large datasets [Complexity: 2/10]
    - [ ] [T2.3] Improve voice preview generation speed [Complexity: 1/10]
  - Estimated time: 2 days

- [ ] [T3] Voice Generation Features [Complexity: 7/10] [Priority: Medium] [Status: Pending]
  - Context: Expand and improve voice generation capabilities and management.
  - Acceptance criteria: Library management, version control, sharing, and prompt enhancements are available.
  - Dependencies: []
  - Subtasks:
    - [ ] [T3.1] Create voice library management system [Complexity: 2/10]
    - [ ] [T3.2] Add voice version control [Complexity: 1/10]
    - [ ] [T3.3] Implement voice sharing capabilities [Complexity: 1/10]
    - [ ] [T3.4] Enhance prompts for voice design [Complexity: 1/10]
    - [ ] [T3.5] Add context-aware prompt suggestions [Complexity: 1/10]
    - [ ] [T3.6] Implement prompt templates system [Complexity: 1/10]
  - Estimated time: 3 days

- [ ] [T4] Expand features [Complexity: 5/10] [Priority: Medium] [Status: Pending]
  - Context: Add new capabilities to broaden the app's usefulness.
  - Acceptance criteria: Voice style transfer, accent/dialect management, and quality assessment tools are implemented.
  - Dependencies: []
  - Subtasks:
    - [ ] [T4.1] Implement voice style transfer [Complexity: 2/10]
    - [ ] [T4.2] Add accent and dialect management [Complexity: 2/10]
    - [ ] [T4.3] Create voice quality assessment tools [Complexity: 1/10]
  - Estimated time: 2 days

- [ ] [T5] Documentation [Complexity: 4/10] [Priority: Medium] [Status: Pending]
  - Context: Ensure users and developers have clear, up-to-date documentation.
  - Acceptance criteria: API docs, user guide, voice generation, and customization guides are complete.
  - Dependencies: []
  - Subtasks:
    - [ ] [T5.1] Create comprehensive API documentation [Complexity: 1/10]
    - [ ] [T5.2] Develop a user guide with examples and best practices [Complexity: 1/10]
    - [ ] [T5.3] Add voice generation documentation [Complexity: 1/10]
    - [ ] [T5.4] Create voice customization guides [Complexity: 1/10]
  - Estimated time: 2 days

- [ ] [T6] Testing Enhancement [Complexity: 5/10] [Priority: Medium] [Status: Pending]
  - Context: Improve test coverage and reliability for new and existing features.
  - Acceptance criteria: End-to-end, integration, navigation, performance, and UI component tests are implemented.
  - Dependencies: []
  - Subtasks:
    - [ ] [T6.1] Add end-to-end tests for voice generation [Complexity: 1/10]
    - [ ] [T6.2] Implement integration tests for prompt enhancement [Complexity: 1/10]
    - [ ] [T6.3] Create test suite for navigation system [Complexity: 1/10]
    - [ ] [T6.4] Add performance benchmarking tests [Complexity: 1/10]
    - [ ] [T6.5] Implement UI component testing [Complexity: 1/10]
  - Estimated time: 2 days

- [ ] [T7] Voice Management System [Complexity: 5/10] [Priority: Low] [Status: Pending]
  - Context: Improve organization and export of voices.
  - Acceptance criteria: Categorization, tagging, comparison, and export features are available.
  - Dependencies: []
  - Subtasks:
    - [ ] [T7.1] Implement voice categorization [Complexity: 1/10]
    - [ ] [T7.2] Add voice tagging system [Complexity: 1/10]
    - [ ] [T7.3] Create voice comparison tools [Complexity: 2/10]
    - [ ] [T7.4] Add voice export functionality [Complexity: 1/10]
  - Estimated time: 2 days

- [ ] [T8] UI/UX Improvements [Complexity: 3/10] [Priority: Low] [Status: Pending]
  - Context: Add polish and accessibility to the interface.
  - Acceptance criteria: Dark mode and characteristic sliders are implemented.
  - Dependencies: []
  - Subtasks:
    - [ ] [T8.1] Implement a dark mode option [Complexity: 2/10]
    - [ ] [T8.2] Implement voice characteristic sliders [Complexity: 1/10]
  - Estimated time: 1 day

- [ ] [T9] Code Refactoring Plan [Complexity: 6/10] [Priority: Low] [Status: Pending]
  - Context: Improve maintainability and scalability of the codebase.
  - Acceptance criteria: Modularization, state management, API refactor, reusable components, and optimized data flow are complete.
  - Dependencies: []
  - Subtasks:
    - [ ] [T9.1] Modularize voice generation components [Complexity: 2/10]
    - [ ] [T9.2] Implement proper state management system [Complexity: 1/10]
    - [ ] [T9.3] Refactor API integration layer [Complexity: 1/10]
    - [ ] [T9.4] Create reusable UI components [Complexity: 1/10]
    - [ ] [T9.5] Optimize data flow architecture [Complexity: 1/10]
  - Estimated time: 3 days

- [ ] [T10] Integrate OpenRouter for external LLM support [Complexity: 6/10] [Priority: Medium] [Status: Pending]
  - Context: Enables ElevenTools to leverage external LLMs for advanced text processing and fallback scenarios.
  - Acceptance criteria: OpenRouter API can be called from within the app, and results are integrated into relevant workflows.
  - Dependencies: []
  - Subtasks:
    - [ ] [T10.1] Research OpenRouter API and authentication [Complexity: 2/10]
    - [ ] [T10.2] Implement integration layer [Complexity: 3/10]
    - [ ] [T10.3] Add usage examples and tests [Complexity: 1/10]
  - Estimated time: 1-2 days

- [ ] [T11] Centralize API management using st.secrets [Complexity: 5/10] [Priority: Medium] [Status: In-Progress]
  - Context: Secure and maintainable management of API keys and secrets, supporting future integrations.
  - Acceptance criteria: All API keys are managed via st.secrets, with documentation for rotation and environment support.
  - Dependencies: []
  - Estimated time: 1 day

- [ ] [T16] Implement Ollama onboarding and setup page [Complexity: 4/10] [Priority: High] [Status: Pending]
  - Context: New users are not informed about LLM (Ollama) choices or setup, leading to confusion and lack of control.
  - Acceptance criteria: 
      - A dedicated onboarding/setup page for Ollama is available as the first step for new users.
      - Users are informed about LLM choices and can select/configure their preferred model.
      - The app does not proceed to main features until setup is complete.
  - Dependencies: []
  - Estimated time: 1 day

- [ ] [T17] Create tests for Ollama onboarding [Complexity: 3/10] [Priority: High] [Status: Pending]
  - Context: Ensure the Ollama onboarding/setup flow is robust and user-friendly.
  - Acceptance criteria: Automated tests cover Ollama installation detection, model listing, error handling, and user selection.
  - Dependencies: [T16]
  - Estimated time: 0.5 day

- [ ] [T18] Add OpenRouter as an LLM provider [Complexity: 5/10] [Priority: High] [Status: Pending]
  - Context: Enable ElevenTools to use OpenRouter as an alternative LLM provider for greater flexibility and fallback scenarios.
  - Acceptance criteria: Users can select OpenRouter as an LLM provider, configure API keys, and use it in relevant workflows.
  - Dependencies: []
  - Estimated time: 1 day

- [ ] [T19] Consolidate OpenRouter and Ollama as LLM providers [Complexity: 6/10] [Priority: High] [Status: Pending]
  - Context: Provide a unified interface for managing and selecting LLM providers, improving user experience and maintainability.
  - Acceptance criteria: Users can choose between Ollama and OpenRouter in a single onboarding/setup flow, and the app uses the selected provider throughout.
  - Dependencies: [T16, T18]
  - Estimated time: 1 day

- [ ] [T20] Clean up Voice Design page [Complexity: 3/10] [Priority: Medium] [Status: Pending]
  - Context: Refactor and improve the Voice Design page for clarity, maintainability, and user experience.
  - Acceptance criteria: Code is organized, redundant logic is removed, and UI/UX is consistent with the rest of the app.
  - Dependencies: []
  - Estimated time: 0.5 day

- [ ] [T21] Prepare for merge with main branch after tests [Complexity: 2/10] [Priority: Medium] [Status: Pending]
  - Context: Ensure all features are tested and documentation is up to date before merging with the main branch.
  - Acceptance criteria: All tests pass, documentation is current, and code is reviewed for merge readiness.
  - Dependencies: [T17]
  - Estimated time: 0.5 day

- [ ] [T22] Update todo.md to reflect ElevenLabs and Ollama-only release [Complexity: 2/10] [Priority: High] [Status: Pending]
  - Context: Ensure the task management and documentation accurately reflect the removal of OpenAI and OpenRouter features for this release.
  - Acceptance criteria: All references to OpenAI and OpenRouter are removed from todo.md, and tasks are aligned with the current feature set.
  - Dependencies: []
  - Estimated time: 0.25 day

- [ ] [T23] Implement File Explorer for Generated Audio [Complexity: 7/10] [Priority: High] [Status: Complete]
  - Context: Users need an easy way to browse, review, and manage all generated audio files, with clear details about each generation. This will improve usability and transparency, especially as output volume grows.
  - Dependencies: []
  - Acceptance criteria:
    - [✅] Users can browse all generated audio files from within the app
    - [✅] Generation details (language, voice, date, ID, seed, source CSV if bulk) are visible for each file
    - [✅] Single and bulk outputs are consolidated in a single 'outputs' folder
    - [✅] Bulk outputs are named after the CSV file used
    - [✅] Single outputs are stored in a separate folder with the format LANGUAGE_VOICE_NAME_DATE_ID_SEED
    - [✅] Bulk generation outputs are displayed inside Streamlit expanders, with rows of audio players and their metadata underneath
    - [✅] Single outputs are stacked as rows without expanders
    - [✅] UI is intuitive and responsive
  - Subtasks:
    - [✅] [T23.1] Consolidate single and bulk outputs into a single 'outputs' folder [Complexity: 2/10]
    - [✅] [T23.2] Name bulk outputs after the source CSV file [Complexity: 1/10]
    - [✅] [T23.3] Store single outputs in a separate folder with detailed naming convention [Complexity: 1/10]
    - [✅] [T23.4] Build file explorer UI: display bulk outputs in Streamlit expanders (with audio rows and metadata), and stack single outputs as rows without expanders [Complexity: 3/10]
  - Estimated time: 2-3 days

- [ ] [T24] Final Testing & Release Polish [Complexity: 4/10] [Priority: High] [Status: Pending]
  - Context: Ensure the app is stable, user-friendly, and ready for release by performing comprehensive testing and final polish.
  - Dependencies: [T23]
  - Acceptance criteria:
    - [ ] All regression and integration tests pass
    - [ ] UI/UX is reviewed and any minor issues are fixed
    - [ ] No critical or high-priority bugs remain
    - [ ] Documentation is up to date
    - [ ] Release checklist is completed
  - Estimated time: 1-2 days

## Archived/Completed Tasks

- [✅] [T12] Implement automated testing [Complexity: 7/10] [Priority: High] [Status: Complete]
  - Context: Ensure code reliability and prevent regressions.
  - Acceptance criteria: Unit, integration, and end-to-end tests are implemented and passing.
  - Dependencies: []
  - Subtasks:
    - [✅] [T12.1] Unit tests for core functions [Complexity: 2/10]
    - [✅] [T12.2] Integration tests for API interactions [Complexity: 2/10]
    - [✅] [T12.3] End-to-end tests for user workflows [Complexity: 3/10]
  - Estimated time: 2 days

- [✅] [T13] Integrate OLLAMA [Complexity: 5/10] [Priority: High] [Status: Complete]
  - Context: Add support for OLLAMA LLMs in the app.
  - Acceptance criteria: OLLAMA API is integrated, tested, and updated to llama3.2:3b model.
  - Dependencies: []
  - Subtasks:
    - [✅] [T13.1] Research OLLAMA API and integration requirements [Complexity: 1/10]
    - [✅] [T13.2] Design integration architecture [Complexity: 1/10]
    - [✅] [T13.3] Implement OLLAMA integration in the codebase [Complexity: 2/10]
    - [✅] [T13.4] Create tests for OLLAMA integration [Complexity: 1/10]
    - [✅] [T13.5] Update to llama3.2:3b model [Complexity: 1/10]
  - Estimated time: 2 days

- [✅] [T14] Implement Voice Generation [Complexity: 6/10] [Priority: High] [Status: Complete]
  - Context: Add ElevenLabs voice generation and customization features.
  - Acceptance criteria: Voice preview, creation, and customization are available.
  - Dependencies: []
  - Subtasks:
    - [✅] [T14.1] Research ElevenLabs voice generation API [Complexity: 1/10]
    - [✅] [T14.2] Design voice generation workflow [Complexity: 1/10]
    - [✅] [T14.3] Implement voice preview system [Complexity: 2/10]
    - [✅] [T14.4] Create voice from preview functionality [Complexity: 1/10]
    - [✅] [T14.5] Add voice customization options [Complexity: 1/10]
  - Estimated time: 2 days

- [✅] [T15] Remove Home.py and consolidate main entry point logic [Complexity: 2/10] [Priority: Medium] [Status: Complete]
  - Context: Eliminates redundancy and confusion by ensuring a single entry point for the app, improving maintainability.
  - Acceptance criteria: Home.py is deleted, and all main logic is in app.py. No duplicate entry points remain.
  - Dependencies: []
  - Estimated time: 15 minutes
