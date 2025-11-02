# Fix Sidebar Font Consistency Issue

## Why

The sidebar font in the Streamlit application changes inconsistently each time a button is pressed, creating a poor user experience. This appears to be caused by CSS being re-injected on each Streamlit rerun without proper caching or explicit sidebar font styling. The issue affects visual consistency and may indicate deeper problems with CSS loading or font application. We need Playwright UI tests to debug this behavior and verify the fix.

## What Changes

- Add explicit sidebar font styling to ensure consistent font application
- Implement CSS loading optimization to prevent re-injection issues
- Create Playwright UI tests to detect and debug font consistency issues
- Verify font consistency across all pages after button interactions
- Document font loading patterns and best practices

## Impact

- Affected specs: New capability `ui-consistency` for UI styling requirements
- Affected code: `custom_style.css`, `app.py`, `pages/*.py` (CSS loading), `tests/ui_tests/` (new tests)
- Improved visual consistency across all application pages
- Better understanding of Streamlit CSS loading behavior
- Foundation for future UI consistency testing

