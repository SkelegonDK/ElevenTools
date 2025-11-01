## 1. Update Version and Basic Information
- [ ] 1.1 Update version number from "Alpha v0.1.0" to "v0.3.0" in title
- [ ] 1.2 Verify version consistency with pyproject.toml

## 2. Update Features Section
- [ ] 2.1 Add OpenRouter model selection with fuzzy search to Features list
- [ ] 2.2 Add free model filtering capability to Features list
- [ ] 2.3 Update Translation feature description to mention model selection

## 3. Update Configuration Section
- [ ] 3.1 Add OpenRouter API key requirement to secrets.toml example
- [ ] 3.2 Update configuration instructions to mention both ElevenLabs and OpenRouter keys

## 4. Update Testing Section
- [ ] 4.1 Add Playwright UI tests to testing documentation
- [ ] 4.2 Update test file list to match actual test structure (test_openrouter_model_functions.py, ui_tests/)
- [ ] 4.3 Add information about running UI tests with Playwright
- [ ] 4.4 Update test execution examples to show current test organization

## 5. Update TODO List and Documentation References
- [ ] 5.1 Mark completed testing items as done
- [ ] 5.2 Mark caching implementation as completed (model fetching uses @st.cache_data)
- [ ] 5.3 Remove or update outdated TODO items
- [ ] 5.4 Add new feature items if relevant (model selection, fuzzy search)
- [ ] 5.5 Remove or update references to `docs/` folder (todo.md, design.md, architecture.md) - these are now superseded by OpenSpec for task management and spec-driven development
- [ ] 5.6 Update any references to docs/todo.md to point to OpenSpec change proposals instead

## 6. Review and Validation
- [ ] 6.1 Verify all features mentioned in README are actually implemented
- [ ] 6.2 Verify all test commands work correctly
- [ ] 6.3 Check for consistency with openspec/project.md and openspec/specs/ (instead of outdated docs/ folder)
- [ ] 6.4 Ensure README accurately reflects current project capabilities
- [ ] 6.5 Verify no outdated references to docs/todo.md, docs/design.md, or docs/architecture.md remain

