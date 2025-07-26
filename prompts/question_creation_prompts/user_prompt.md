Generate evaluation questions for a RAG system based on the following structured Huberman Lab podcast data. This data has been extracted and organized from the original transcript into chapters with headings, content summaries, and topic lists. Create questions that real users would ask and that test different RAG capabilities.

**Input Data:**

**Overall Summary:**
{{overall_summary}}

**Chapters:**
{{chapters}}

**Topics Covered:**
{{topics}}

**Requirements:**
- Generate 2-4 questions total (adapt based on content richness)
- Focus on descriptive questions, include prescriptive/methodological only if content supports them
- Vary difficulty levels and answer scope when possible
- Ensure questions are answerable from provided content

**Final Checklist:**
- [ ] Questions sound natural and user-like
- [ ] Content types match what's actually available in the data
- [ ] Mix of difficulty levels when content allows
- [ ] Both single-chapter and cross-chapter questions included when appropriate
- [ ] Ground truth references match actual chapter headings/timestamps
- [ ] Questions are specific and focused
- [ ] Total question count is 4-8 based on content richness

Generate the questions in the specified JSON format.