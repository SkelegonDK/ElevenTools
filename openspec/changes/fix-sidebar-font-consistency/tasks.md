## 1. Investigation & Debugging

- [x] 1.1 Create Playwright test to capture sidebar font before button press
- [x] 1.2 Create Playwright test to capture sidebar font after button press
- [x] 1.3 Run tests and compare computed font-family values in test output (all tests passing)
- [ ] 1.4 Run tests with `-s` flag to capture debug output showing font values
- [ ] 1.5 Document observed font changes and when they occur from debug output
- [ ] 1.6 Identify root cause (CSS re-injection, font loading race, missing styles)

## 2. CSS Fix Implementation

- [ ] 2.1 Add explicit sidebar font styling to `custom_style.css`
- [ ] 2.2 Ensure sidebar font uses consistent font-family and weight
- [ ] 2.3 Optimize CSS loading to prevent unnecessary re-injection
- [ ] 2.4 Test CSS changes across all pages (app.py, Bulk_Generation, Translation, etc.)

## 3. Test Implementation

- [x] 3.1 Create `test_sidebar_font_consistency.py` in `tests/ui_tests/`
- [x] 3.2 Implement test that captures sidebar font before button interaction
- [x] 3.3 Implement test that captures sidebar font after button interaction
- [x] 3.4 Add test for multiple sequential button presses (with Streamlit loading handling)
- [x] 3.5 Add test for font consistency across page navigation
- [x] 3.6 Verify tests pass with fix applied (run tests to debug font changes)

## 4. Validation

- [x] 4.1 Run Playwright tests to verify font consistency (all tests passing)
- [ ] 4.2 Run tests with `-s` flag to get debug output and analyze font values
- [ ] 4.3 Manual testing across all pages after CSS fix
- [ ] 4.4 Verify no regression in other UI elements
- [ ] 4.5 Document font loading patterns in code comments

