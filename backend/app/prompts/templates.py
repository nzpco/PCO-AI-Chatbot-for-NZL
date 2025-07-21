from llama_index.prompts import PromptTemplate

# Template for generating summaries of legislation fragments
SUMMARY_TEMPLATE = PromptTemplate(
    template="""You are a legal summarizer specialized in legislative content. Create a precise one-sentence summary of this {fragment_type}.

TEXT TO SUMMARIZE:
{text}

INSTRUCTIONS:
1. Begin with an active verb describing what this {fragment_type} does (establishes, requires, prohibits, defines, etc.)
2. Include key legal terminology that would enhance semantic search
3. Capture all substantive elements while omitting procedural details unless essential
4. Use present tense and formal language
5. Maintain factual accuracy without interpretation
6. Include any defined thresholds, timelines, or requirements that are central to meaning

FORMAT:
- Single sentence of 25-50 words
- No introductory text or explanations
- No bullet points
- Start directly with the active verb

OUTPUT:
SHORT: [your summary]"""
)

# SUMMARY_LONG_TEMPLATE = PromptTemplate(
#     template="""Please provide a detailed summary of the following {fragment_type} text.
#     Include all key points and provisions. Keep the summary clear and professional.
#     Do not include any introductory text.

#     Text to summarize:
#     {text}

#     Summary:"""
# )

CONTEXT_SUMMARY_TEMPLATE = PromptTemplate(
    template="""You are a legal context summarizer specialized in legislative hierarchies. Your task is to create a concise context description for a specific legislative {fragment_type} that helps readers quickly understand its place in the broader legislative framework.

INPUT:
- {fragment_type} title: {heading}
- {fragment_type} content/summary: {content}
- Parent Hierarchy: {chunk_id}
- Parent Summaries:
{parent_summaries_list}

INSTRUCTIONS:
1. First, identify the EXACT structural purpose of this section:
   - For technical sections (like Title, Commencement, Interpretation sections): Focus on explaining their structural function within legislative organization
   - For substantive sections: Explain their relation to parent containers and the Act's objectives

2. Create a 2-3 sentence context description that:
   - Accurately describes what this specific section does (without inventing content)
   - Places it correctly within the legislative hierarchy
   - Explains its relationship to the Act's structure or objectives

3. Your description must:
   - Be factually precise with no assumptions beyond the provided information
   - Use clear legal terminology without unnecessary complexity
   - Focus on structural and organizational context
   - Avoid repeating the section's content verbatim

FORMAT:
- Begin with "Context:" followed by your description
- Use present tense and neutral tone
- 40-60 words maximum

EXAMPLE A (Technical section):
- Section Title: "Short Title"
- Section Content: "This Act is the Data Protection Act 2023."
- Parent Hierarchy: "Data Protection Act 2023 > Part 1: Preliminary"

EXAMPLE A OUTPUT:
Context: This section establishes the official citation name of the legislation within Part 1's preliminary provisions. The short title section is a standard technical component that appears at the beginning of Acts and provides the formal reference name used in legal citations and official documents."""
)

COMBINED_SUMMARY_TEMPLATE = PromptTemplate(
    template="""You are a legal summarizer specialized in legislative hierarchies. Create both concise and detailed summaries of this {fragment_type}.

TEXT TO SUMMARIZE:
{text}

INSTRUCTIONS:
1. Create TWO distinct summaries:

   For the SHORT summary (one sentence):
   - Begin with an active verb describing the primary regulatory function
   - Identify the main legal mechanisms or frameworks established
   - Include key terminology that enables semantic search
   - 30-50 words maximum

   For the DETAILED summary:
   - Start with a brief introductory sentence stating overall purpose
   - Use bullet points to identify distinct regulatory elements or subject areas
   - Include relationships between major provisions
   - Preserve specialty legal terminology
   - Identify any exceptions, qualifications, or conditional applications
   - 100-150 words total

2. Both summaries must:
   - Use present tense and formal language
   - Maintain factual precision without interpretation
   - Focus on regulatory effect rather than procedural details
   - Preserve terms that would be valuable for semantic search

FORMAT:
Provide exactly this format without deviation:
SHORT: [your one-sentence summary]
LONG: [your detailed bullet-point summary]"""
)

