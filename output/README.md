# Output Directory

The Round 1B solution will generate results here.

## Output Format

The system produces `challenge1b_output.json` with the following structure:

```json
{
  "metadata": {
    "documents": ["file1.pdf", "file2.pdf"],
    "persona": "Your specified persona",
    "job_to_be_done": "Your specified task",
    "processing_timestamp": "2025-07-28T15:30:00Z"
  },
  "extracted_sections": [
    {
      "document": "file1.pdf",
      "page": 3,
      "section_title": "Important Section Title",
      "importance_rank": 1
    }
  ],
  "subsection_analysis": [
    {
      "document": "file1.pdf",
      "page": 3,
      "refined_text": "Key content extracted and refined..."
    }
  ]
}
```

## Files Generated

- `challenge1b_output.json` - Main output file with ranked sections
- Additional debug/log files may be generated during processing
