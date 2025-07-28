# Input Directory

Place your PDF documents here for processing.

## Usage

1. Copy your PDF files to this directory
2. Update the `documents` array in `input_config.json` to list your PDF filenames
3. Run the Round 1B solution

## Example

If you have files:
- `research-paper-1.pdf`
- `research-paper-2.pdf`
- `business-report.pdf`

Update your `input_config.json`:
```json
{
  "persona": "Research Analyst",
  "job_to_be_done": "Extract key findings and methodologies for literature review",
  "documents": [
    "research-paper-1.pdf",
    "research-paper-2.pdf", 
    "business-report.pdf"
  ]
}
```
