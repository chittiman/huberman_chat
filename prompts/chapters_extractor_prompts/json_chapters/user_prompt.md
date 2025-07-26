Analyze this YouTube video transcript and return a JSON structure with:
1. Overall summary (3-4 sentences)
2. Chapter timestamps with headings and content
3. Key topics list

Transcript:
```
{{transcript}}
```

Return only valid JSON in this format:
```json
{
  "overall_summary": "...",
  "chapters": [
    {
      "timestamp": "0:00",
      "heading": "...",
      "content": "..."
    }
  ],
  "topics": ["topic1", "topic2", "..."]
}
```