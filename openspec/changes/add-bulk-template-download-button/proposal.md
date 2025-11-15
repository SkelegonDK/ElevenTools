## Why
Users need an easy way to access the bulk generation CSV template file to understand the expected format and use it as a starting point for their own bulk generation files. Currently, users must manually locate or create the template file, which creates friction in the workflow.

## What Changes
- Add a download button for `bulk_template.csv` on the Bulk Generation page
- Button should be prominently placed near the CSV upload instructions
- Download should provide the template file with example data showing proper format

## Impact
- Affected specs: `bulk-generation`
- Affected code: `pages/Bulk_Generation.py`
- User experience: Improved onboarding and template access for bulk generation feature

