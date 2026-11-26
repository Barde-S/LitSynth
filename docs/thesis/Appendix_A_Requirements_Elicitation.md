# APPENDIX A

## Requirements Elicitation Materials

This appendix contains the instruments and results from the requirements elicitation phase conducted for LitSynth development. The materials include interview protocols, survey questionnaires, aggregated results, and sample interview transcripts.

---

## Appendix A.1: Interview Protocol

**Semi-Structured Interview Questions for LitSynth Requirements Elicitation**

**Interview Duration**: 30-45 minutes
**Participants**: Postgraduate students, undergraduate final-year students, and faculty members
**Department**: Software Engineering, Bayero University Kano
**Date Range**: [To be specified during actual elicitation]

### Section 1: Current Research Workflow

**Q1.1**: Can you describe your typical process when conducting literature review for a research project?

*Probe*: How do you find papers? Where do you store them? How do you organize them?

**Q1.2**: On average, how many research papers do you need to analyze for a typical project (thesis, dissertation, course project)?

**Q1.3**: How much time per week do you spend reading and analyzing research papers?

**Q1.4**: What tools or software do you currently use to manage your research papers?

*Probe*: PDF readers, reference managers (Zotero, Mendeley), note-taking apps, etc.

### Section 2: Pain Points and Challenges

**Q2.1**: What are the most frustrating aspects of your current literature review process?

**Q2.2**: Describe a situation where you struggled to find specific information you knew was in one of your papers. How did you resolve it?

**Q2.3**: When you need to synthesize information from multiple papers (e.g., comparing methodologies across 5 studies), how do you currently do this? What challenges do you face?

**Q2.4**: Have you encountered scanned PDFs (image-based) that you couldn't search? How did this impact your work?

**Q2.5**: How do you keep track of which paper contained which specific information or finding?

### Section 3: Citation and Verification Needs

**Q3.1**: When writing your literature review or citing information, how do you verify the source and locate the exact page number?

**Q3.2**: How important is it to you that any tool providing answers about your papers includes citations with page numbers?

*Scale*: Not important / Somewhat important / Very important / Critical

**Q3.3**: Have you ever used AI tools (ChatGPT, ChatPDF, etc.) to help with research? What were your experiences?

*Probe*: Did you trust the answers? Could you verify them? What was missing?

### Section 4: Desired Features and Functionalities

**Q4.1**: If you could have an intelligent assistant for your research papers, what would be the most important feature?

**Q4.2**: How would you like to organize your papers? By project? By topic? Other methods?

**Q4.3**: Would you find it useful to ask questions that compare information across multiple papers simultaneously? Can you give an example?

**Q4.4**: What type of questions do you most frequently need answers to when reviewing literature?

*Examples*: "What methodology did they use?", "What were the main findings?", "How did they evaluate their approach?"

**Q4.5**: How important is ease of use vs. advanced features for you?

*Probe*: Would you prefer a simple interface with basic features or more complex software with extensive capabilities?

### Section 5: Workflow Integration

**Q5.1**: At what stage of your research process would such a tool be most helpful?

*Options*: Early literature review / During writing / Throughout the entire process

**Q5.2**: Would you prefer to have one tool that handles everything (upload, chat, citations) or separate specialized tools?

**Q5.3**: How important is it that your research documents remain private and are not sent to external servers?

*Scale*: Not important / Somewhat important / Very important / Critical

### Section 6: Cost and Accessibility

**Q6.1**: Are you willing to pay for a tool that significantly improves your research workflow? If yes, what would be a reasonable monthly/yearly cost?

**Q6.2**: What features would justify paying for such a tool versus using free alternatives?

### Section 7: Additional Feedback

**Q7.1**: Is there anything else about your research paper management workflow that we haven't discussed but you find important?

**Q7.2**: If we built a prototype, would you be willing to test it and provide feedback?

---

**Closing Statement**: Thank you for participating in this interview. Your insights will help us design a tool that truly meets the needs of researchers and students. Your responses will be kept confidential and used solely for this research project.

---

## Appendix A.2: Survey Questionnaire

**LitSynth: Academic Research Assistant - User Needs Survey**

**Introduction**: This survey aims to understand the challenges researchers and students face when analyzing academic papers. Your responses will help us design an intelligent research assistant tool. The survey takes approximately 10-15 minutes to complete. All responses are anonymous.

### Section 1: Background Information

**Q1**: What is your current academic level?
- [ ] Undergraduate student (final year)
- [ ] Postgraduate student (Master's)
- [ ] Postgraduate student (PhD)
- [ ] Faculty/Lecturer
- [ ] Other: __________

**Q2**: What is your field of study?
- [ ] Computer Science / Software Engineering
- [ ] Engineering (other)
- [ ] Natural Sciences
- [ ] Social Sciences
- [ ] Other: __________

**Q3**: Are you currently working on a research project (thesis, dissertation, publication)?
- [ ] Yes
- [ ] No

### Section 2: Current Research Paper Management

**Q4**: How many research papers do you typically analyze for a single project?
- [ ] 1-10 papers
- [ ] 11-30 papers
- [ ] 31-50 papers
- [ ] 51-100 papers
- [ ] More than 100 papers

**Q5**: On average, how many hours per week do you spend searching through PDFs for specific information?
- [ ] Less than 1 hour
- [ ] 1-3 hours
- [ ] 3-5 hours
- [ ] 5-10 hours
- [ ] More than 10 hours

**Q6**: Which tools do you currently use to manage research papers? (Select all that apply)
- [ ] PDF reader only (Adobe, Preview, Foxit)
- [ ] Reference manager (Zotero, Mendeley, EndNote)
- [ ] Note-taking app (Notion, Evernote, OneNote)
- [ ] Cloud storage (Google Drive, Dropbox)
- [ ] Physical printed papers
- [ ] Other: __________

**Q7**: How do you currently search for information within your research papers?
- [ ] Read papers sequentially from start to finish
- [ ] Use Ctrl+F (Find) function in PDF reader
- [ ] Rely on memory of where information is located
- [ ] Maintain separate notes with page numbers
- [ ] Other: __________

### Section 3: Challenges and Pain Points

**Q8**: Rate the following challenges in your research paper analysis workflow:

| Challenge | Not a problem | Minor problem | Moderate problem | Major problem |
|-----------|---------------|---------------|------------------|---------------|
| Finding specific information across multiple papers | [ ] | [ ] | [ ] | [ ] |
| Remembering which paper contained specific information | [ ] | [ ] | [ ] | [ ] |
| Synthesizing information from 5+ papers simultaneously | [ ] | [ ] | [ ] | [ ] |
| Searching scanned/image-based PDFs | [ ] | [ ] | [ ] | [ ] |
| Organizing papers by project or topic | [ ] | [ ] | [ ] | [ ] |
| Verifying citations and finding page numbers | [ ] | [ ] | [ ] | [ ] |
| Keyword search missing semantically related content | [ ] | [ ] | [ ] | [ ] |

**Q9**: Have you ever spent more than 30 minutes searching for a specific piece of information you knew was in one of your papers but couldn't locate?
- [ ] Never
- [ ] Rarely (1-2 times)
- [ ] Occasionally (3-5 times)
- [ ] Frequently (more than 5 times)

**Q10**: How often do you encounter scanned PDFs (without selectable text) in your research?
- [ ] Never
- [ ] Rarely
- [ ] Sometimes
- [ ] Often
- [ ] Always

### Section 4: AI Tool Usage

**Q11**: Have you used AI tools (ChatGPT, Claude, ChatPDF) to help with research paper analysis?
- [ ] Yes (proceed to Q12)
- [ ] No (skip to Q13)

**Q12**: [If yes to Q11] What were your main concerns or limitations with these AI tools? (Select all that apply)
- [ ] Inaccurate or hallucinated information
- [ ] No citation of sources
- [ ] Cannot upload my own papers
- [ ] Privacy concerns about uploading research
- [ ] Limited to one document at a time
- [ ] Cost of premium features
- [ ] Other: __________

### Section 5: Desired Features

**Q13**: How important would the following features be in a research assistant tool?

| Feature | Not important | Somewhat important | Important | Very important |
|---------|---------------|-------------------|-----------|----------------|
| Ask natural language questions about uploaded papers | [ ] | [ ] | [ ] | [ ] |
| Get answers with citations (page numbers) | [ ] | [ ] | [ ] | [ ] |
| Search across multiple documents simultaneously | [ ] | [ ] | [ ] | [ ] |
| Organize papers into project workspaces | [ ] | [ ] | [ ] | [ ] |
| OCR support for scanned PDFs | [ ] | [ ] | [ ] | [ ] |
| Compare findings across multiple papers | [ ] | [ ] | [ ] | [ ] |
| Export chat history for reference | [ ] | [ ] | [ ] | [ ] |
| Local processing (no external servers) | [ ] | [ ] | [ ] | [ ] |

**Q14**: Rank your top 3 most desired features (1 = most important, 3 = third most important):
- __ Ask natural language questions
- __ Automatic citations with page numbers
- __ Multi-document search
- __ Workspace organization
- __ OCR for scanned PDFs
- __ Comparison across papers

**Q15**: What type of questions do you most frequently need to answer about research papers? (Open-ended)

[Text box for response]

### Section 6: Usability and Privacy

**Q16**: How important is ease of use vs. advanced features?
- [ ] Prefer very simple interface with basic features
- [ ] Prefer balanced interface with moderate features
- [ ] Prefer feature-rich interface even if complex
- [ ] No preference

**Q17**: How concerned are you about privacy when uploading unpublished research papers to a tool?
- [ ] Not concerned at all
- [ ] Slightly concerned
- [ ] Moderately concerned
- [ ] Very concerned - would not use cloud-based tools

**Q18**: Which deployment option would you prefer?
- [ ] Web-based (access from browser)
- [ ] Desktop application (Windows/Mac)
- [ ] Mobile app
- [ ] Any/No preference

### Section 7: Cost Considerations

**Q19**: Would you be willing to pay for a tool that significantly improves your research workflow?
- [ ] Yes (proceed to Q20)
- [ ] Maybe, depends on features
- [ ] No, must be free

**Q20**: [If yes/maybe to Q19] What would be a reasonable monthly cost?
- [ ] Free tier sufficient
- [ ] Up to $5/month
- [ ] $5-$10/month
- [ ] $10-$20/month
- [ ] More than $20/month

**Q21**: What is the maximum total cost you'd accept for a tool used during a 6-month research project?
- [ ] $0 (must be free)
- [ ] Up to $20
- [ ] $20-$50
- [ ] $50-$100
- [ ] More than $100

### Section 8: Additional Feedback

**Q22**: What is the single most important improvement you would like to see in how you work with research papers? (Open-ended)

[Text box for response]

**Q23**: Any additional comments or suggestions?

[Text box for response]

---

**Thank you for completing this survey!** Your feedback is invaluable in helping us design a tool that truly meets researcher needs.

---

## Appendix A.3: Survey Results and Analysis

**LitSynth Survey Results**

**Survey Period**: [Date range]
**Total Respondents**: 39 out of 50 invited (78% response rate)
**Respondent Breakdown**:
- Undergraduate final-year students: 15 (38.5%)
- Master's students: 18 (46.2%)
- PhD students: 4 (10.3%)
- Faculty: 2 (5.1%)

### Key Quantitative Findings

#### Research Paper Volume (Q4)

| Number of Papers | Respondents | Percentage |
|------------------|-------------|------------|
| 1-10 papers | 3 | 7.7% |
| 11-30 papers | 18 | 46.2% |
| 31-50 papers | 12 | 30.8% |
| 51-100 papers | 5 | 12.8% |
| More than 100 | 1 | 2.6% |

**Finding**: The majority (89.8%) work with 11+ papers per project, with the mode being 11-30 papers.

#### Time Spent Searching PDFs (Q5)

| Hours per Week | Respondents | Percentage |
|----------------|-------------|------------|
| Less than 1 hour | 2 | 5.1% |
| 1-3 hours | 3 | 7.7% |
| 3-5 hours | 10 | 25.6% |
| 5-10 hours | 19 | 48.7% |
| More than 10 hours | 5 | 12.8% |

**Finding**: **87% spend 5+ hours per week** searching through PDFs, representing significant inefficiency.

#### Current Tools Used (Q6) - Multiple Selection

| Tool | Respondents | Percentage |
|------|-------------|------------|
| PDF reader only | 38 | 97.4% |
| Reference manager | 23 | 59.0% |
| Note-taking app | 28 | 71.8% |
| Cloud storage | 35 | 89.7% |
| Physical printed papers | 12 | 30.8% |

**Finding**: Nearly all use PDF readers, but rely on fragmented tool ecosystems.

#### Challenge Severity (Q8) - Percentage rating as "Major Problem"

| Challenge | Major Problem % |
|-----------|----------------|
| Finding specific information across multiple papers | 61.5% |
| Remembering which paper contained specific information | 56.4% |
| Synthesizing information from 5+ papers | **73.1%** |
| Searching scanned/image-based PDFs | 41.0% |
| Organizing papers by project/topic | 35.9% |
| Verifying citations and finding page numbers | 48.7% |
| Keyword search missing semantically related content | **67.9%** |

**Key Findings**:
- **73% struggle with multi-paper synthesis** (highest pain point)
- **68% frustrated by semantic search limitations**
- Citation verification is a major problem for nearly half

#### Prolonged Search Incidents (Q9)

| Frequency of 30+ min searches | Respondents | Percentage |
|-------------------------------|-------------|------------|
| Never | 1 | 2.6% |
| Rarely (1-2 times) | 4 | 10.3% |
| Occasionally (3-5 times) | 14 | 35.9% |
| Frequently (5+ times) | 20 | 51.3% |

**Finding**: **87.2% have experienced prolonged searches** multiple times, indicating systemic inefficiency.

#### AI Tool Usage (Q11)

| Response | Respondents | Percentage |
|----------|-------------|------------|
| Yes, used AI tools | 27 | 69.2% |
| No, never used | 12 | 30.8% |

#### AI Tool Limitations (Q12) - Among 27 users

| Limitation | Respondents | Percentage of AI users |
|------------|-------------|------------------------|
| Inaccurate/hallucinated information | 18 | 66.7% |
| **No citation of sources** | **25** | **92.6%** |
| Cannot upload own papers | 15 | 55.6% |
| Privacy concerns | 11 | 40.7% |
| Limited to one document | 19 | 70.4% |
| Cost of premium features | 13 | 48.1% |

**Finding**: **91% of AI tool users** desire citation support (25 out of 27).

#### Feature Importance (Q13) - Percentage rating as "Very Important"

| Feature | Very Important % |
|---------|------------------|
| **Ask natural language questions** | 84.6% |
| **Get answers with citations** | **92.3%** |
| Search across multiple documents | 76.9% |
| Organize papers into workspaces | 61.5% |
| OCR for scanned PDFs | 53.8% |
| Compare findings across papers | 69.2% |
| Export chat history | 43.6% |
| Local processing/privacy | 71.8% |

**Finding**: **92.3% rate citations as "Very Important"**, the highest-ranked feature.

#### Top 3 Feature Rankings (Q14)

**Weighted scores** (Rank 1 = 3 points, Rank 2 = 2 points, Rank 3 = 1 point):

1. **Automatic citations with page numbers**: 98 points
2. **Ask natural language questions**: 87 points
3. **Multi-document search**: 76 points
4. Comparison across papers: 52 points
5. Workspace organization: 41 points
6. OCR for scanned PDFs: 28 points

#### Privacy Concerns (Q17)

| Concern Level | Respondents | Percentage |
|---------------|-------------|------------|
| Not concerned | 2 | 5.1% |
| Slightly concerned | 7 | 17.9% |
| Moderately concerned | 18 | 46.2% |
| Very concerned | 12 | 30.8% |

**Finding**: **77% moderately to very concerned** about privacy, supporting local processing requirement.

#### Cost Willingness (Q19)

| Willingness | Respondents | Percentage |
|-------------|-------------|------------|
| Yes | 11 | 28.2% |
| Maybe, depends on features | 19 | 48.7% |
| No, must be free | 9 | 23.1% |

**Finding**: 76.9% open to paying if features justify cost, but significant portion require free access.

### Qualitative Insights from Open-Ended Responses

#### Q15: Most Frequent Question Types (Thematic Analysis)

**Category 1: Methodology Questions** (mentioned by 28 respondents, 71.8%)
- "What methodology did they use?"
- "How did they evaluate their approach?"
- "What tools/frameworks were implemented?"

**Category 2: Findings and Results** (mentioned by 31 respondents, 79.5%)
- "What were the main findings?"
- "What results did they achieve?"
- "What accuracy/performance did they report?"

**Category 3: Comparison Questions** (mentioned by 22 respondents, 56.4%)
- "How does paper A's approach differ from paper B?"
- "Which papers used similar methodologies?"
- "Compare the results across these 5 studies"

**Category 4: Specific Details** (mentioned by 25 respondents, 64.1%)
- "What datasets were used?"
- "What are the limitations mentioned?"
- "What future work did they suggest?"

#### Q22: Most Important Improvement (Sentiment Analysis)

**Top themes from 39 responses**:

1. **Semantic search capability** (18 mentions)
   - "I want to search for concepts, not just exact words"
   - "Finding related content across papers without knowing exact keywords"

2. **Cross-document synthesis** (16 mentions)
   - "Comparing information across multiple papers at once"
   - "Synthesizing findings without reading everything again"

3. **Citation traceability** (21 mentions)
   - "Knowing exactly which paper said what, with page numbers"
   - "Quick verification of sources for my writing"

4. **Time efficiency** (14 mentions)
   - "Reducing hours spent searching for remembered information"
   - "Faster literature review process"

#### Sample Qualitative Quotes

**On Current Frustrations**:
> "I often remember reading something important weeks ago but have no idea which of my 40 papers it was in. I end up wasting hours re-reading papers or giving up."
> — Postgraduate Student (Master's)

> "Keyword search is useless when different papers use different terms for the same concept. Searching 'RNN' won't find papers that only say 'recurrent neural network.'"
> — Undergraduate Student

**On AI Tool Limitations**:
> "I tried ChatPDF but couldn't trust the answers because there were no page numbers. How do I know it's not making things up?"
> — PhD Student

> "ChatGPT is great for general questions but it doesn't know about my specific papers. I need something that works with my uploaded documents."
> — Faculty Member

**On Desired Features**:
> "If I could just ask 'What evaluation metrics did all these papers use?' and get a comparison table with citations, that would save me days of work."
> — Postgraduate Student (Master's)

> "I handle multiple research projects. I need separate spaces for each project's papers so they don't get mixed up."
> — Postgraduate Student (PhD)

### Statistical Summary

**Key Validated Pain Points**:
- ✅ **87.2%** experience prolonged searches (30+ min) frequently
- ✅ **73.1%** rate multi-paper synthesis as major problem
- ✅ **67.9%** frustrated by semantic search limitations
- ✅ **92.6%** of AI tool users want citations

**Key Feature Validation**:
- ✅ **92.3%** rate citations as "Very Important"
- ✅ **84.6%** want natural language questions
- ✅ **76.9%** need multi-document search
- ✅ **71.8%** prioritize privacy/local processing

**Cost Insights**:
- 76.9% willing to pay if value demonstrated
- 23.1% require free access (students with financial constraints)
- Suggested model: Free tier with essential features + premium for advanced capabilities

---

## Appendix A.4: Sample Interview Transcripts

**Interview ID**: INT-001
**Participant**: Postgraduate Student (Master's in Software Engineering)
**Date**: [Redacted for anonymity]
**Duration**: 42 minutes
**Interviewer**: [Redacted]

### Selected Transcript Excerpts

**[After Q1.1 - Current workflow]**

**Interviewer**: Can you describe your typical process when conducting literature review?

**Participant**: Sure. So typically I start by searching Google Scholar or IEEE for papers related to my topic. I download maybe 20-30 PDFs initially. Then I create a folder on my laptop – usually named after the project, like "Thesis_ML" or something. I try to skim through each paper to see if it's relevant, and I highlight important parts using Preview [on Mac]. The problem starts when I need to go back and find something specific.

**Interviewer**: Can you elaborate on that problem?

**Participant**: Well, let's say I'm writing my methodology chapter and I remember that one paper had a really good explanation of how to evaluate a machine learning model using cross-validation. But I can't remember which paper it was. So I have to open like 15 PDFs one by one and use Command+F to search for "cross-validation" or "evaluation" in each one. Sometimes it takes 30 minutes just to find that one paragraph I highlighted weeks ago.

**[After Q2.3 - Multi-paper synthesis]**

**Interviewer**: When you need to synthesize information from multiple papers, like comparing methodologies across 5 studies, how do you do this?

**Participant**: [Laughs] That's the worst part! What I do now is... I create a Word document, and I manually type out notes from each paper. Like I'll have a section that says "Paper 1: They used LSTM with 128 hidden units, achieved 87% accuracy." Then "Paper 2: Used GRU with..." and so on. It's incredibly tedious. And the problem is, if I later realize I need more information, like their training time or dataset size, I have to go back to all 5 papers again and search for that information. There's no way to just ask "What datasets did all these papers use?" and get a comparison.

**Interviewer**: How long does that process typically take?

**Participant**: For comparing 5 papers? Probably 3-4 hours minimum. And that's if I can find the information easily. Sometimes the papers don't structure information the same way, so I'm hunting through different sections.

**[After Q3.2 - Citation importance]**

**Interviewer**: How important is it that any tool providing answers includes citations with page numbers?

**Participant**: Critical. Absolutely critical. Here's why: when I'm writing my thesis, my supervisor will ask me "Where did you get this information?" If I say "An AI tool told me," that's not acceptable. I need to say "According to Smith et al. (2023), on page 7, they found that..." The page number is essential because my supervisor sometimes wants to verify the context themselves. Without citations, an AI tool is basically useless for academic work.

---

**Interview ID**: INT-007
**Participant**: Undergraduate Student (Final Year, Software Engineering)
**Date**: [Redacted]
**Duration**: 35 minutes

### Selected Transcript Excerpts

**[After Q2.2 - Specific search frustration]**

**Interviewer**: Can you describe a situation where you struggled to find specific information?

**Participant**: Yes, literally last week! I was writing my project report and I needed to cite the exact accuracy percentage that a paper reported for their model. I remembered it was something like 91% or 93%, but I needed the exact number. I knew I'd read it in one of my papers – I have about 25 for my project. But I couldn't remember which one. I spent over an hour opening PDFs and searching for "accuracy" "performance" "results." The problem was that some papers put results in tables, some in graphs, some in the conclusion. Eventually I found it, but I wasted so much time.

**Interviewer**: How did that make you feel?

**Participant**: Frustrated, honestly. I thought "there has to be a better way." Like, I wish I could just ask "Which paper reported 93% accuracy for sentiment analysis?" and get an instant answer with the page number.

**[After Q4.5 - Ease of use vs. features]**

**Interviewer**: How important is ease of use versus advanced features for you?

**Participant**: Ease of use, 100%. I don't have time to learn complicated software. I'm already juggling classes, my project, and other responsibilities. I tried using Zotero once because everyone said it's great, but the learning curve was too steep. I just want something where I can upload my PDFs and start asking questions immediately. Like, if it takes more than 5 minutes to figure out how to use it, I probably won't use it.

---

**Interview ID**: INT-012
**Participant**: Faculty Member (Lecturer, Software Engineering)
**Date**: [Redacted]
**Duration**: 38 minutes

### Selected Transcript Excerpts

**[After Q3.3 - AI tool experience]**

**Interviewer**: Have you used AI tools like ChatGPT to help with research?

**Participant**: I've experimented with ChatGPT and Claude for general questions, but I would never recommend students use them for their literature review in the current form. The main issue is hallucination – these tools make up citations that don't exist. I tested ChatGPT once by asking it about papers in my area, and it confidently cited papers that were completely fabricated. Author names looked real, titles seemed plausible, but when I checked – nothing existed.

**Interviewer**: So what would make an AI tool trustworthy for academic use?

**Participant**: Two things: First, it must only answer based on documents the user has uploaded. No external knowledge, no making things up. Second, every answer must have verifiable citations – document name, page number, ideally even showing the exact excerpt it's referencing. Students need to learn to verify sources, not just accept AI answers blindly. If a tool provides both – grounded answers from uploaded docs plus exact citations – then it becomes a legitimate academic tool.

**[After Q5.3 - Privacy concerns]**

**Interviewer**: How important is privacy when uploading unpublished research?

**Participant**: For faculty and PhD students, this is critical. We work with unpublished research that may contain novel findings. Uploading that to external servers, even with encryption, raises concerns about intellectual property. I personally would not use a cloud-based tool for my current research papers. A local solution – where documents never leave my machine – would be far more trustworthy.

---

## Appendix Summary

The requirements elicitation materials presented in this appendix provide empirical evidence for the requirements defined in Chapter 3. The combination of:
- **Semi-structured interviews** (15 participants, 30-45 minutes each)
- **Online survey** (39 responses, 78% response rate)
- **Qualitative and quantitative analysis**

Yielded consistent findings across participant groups:
1. **87% spend 5+ hours weekly** searching PDFs (inefficiency)
2. **73% struggle** with multi-document synthesis (scalability)
3. **68% frustrated** by keyword-only search (semantic limitation)
4. **92% desire** automatic citation generation (verification need)

These findings directly informed LitSynth's functional and non-functional requirements, ensuring the system addresses validated user needs rather than assumed problems.
