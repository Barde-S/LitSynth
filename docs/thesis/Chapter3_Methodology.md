# CHAPTER THREE

## METHODOLOGY

### 3.1 Introduction

This chapter presents the methodology employed in developing LitSynth, an intelligent academic research assistant. The chapter begins with an overview of the project workflow, followed by a description of the chosen system development model. Requirements analysis is then conducted through elicitation, definition, and modeling using use case diagrams. The chapter concludes with the system design phase, presenting architectural diagrams, database schema, and behavioral models that guided the implementation of LitSynth.

### 3.2 Project Workflow

Figure 3.1 illustrates the systematic workflow followed in developing LitSynth. The project commenced with an introduction phase where the problem domain was identified and research objectives were established. This was followed by an extensive literature review of existing academic research assistance tools and RAG (Retrieval-Augmented Generation) systems. The analysis and design phase involved requirements gathering, system modeling, and architectural planning. Implementation and testing encompassed the actual development of the system using React, FastAPI, and ChromaDB, along with comprehensive unit, integration, and system testing. The final phases involved documentation and preparation of defense materials.

```
┌─────────────┐    ┌──────────────┐    ┌─────────────┐    ┌──────────────────┐    ┌─────────┐    ┌───────────────┐
│Introduction │ -> │  Literature  │ -> │  Analysis   │ -> │ Implementation   │ -> │Writeup  │ -> │Defense Slides │
│             │    │    Review    │    │ and Design  │    │  and Testing     │    │         │    │               │
└─────────────┘    └──────────────┘    └─────────────┘    └──────────────────┘    └─────────┘    └───────────────┘
```
**Figure 3.1: Project Workflow**

### 3.3 System Development Model

The Iterative Incremental development model was adopted for LitSynth due to the experimental nature of RAG-based systems and the need for continuous refinement based on user feedback.

The Iterative Incremental model is a software development approach where the system is developed through repeated cycles (iterative) and in smaller portions at a time (incremental), allowing developers to take advantage of what was learned during development of earlier parts of the system (Pressman, 2014).

This model was selected for the following reasons:

**1. Flexibility in Requirements**: Academic research tools require iterative refinement of retrieval accuracy and response quality, which this model accommodates. The semantic search capabilities and citation generation mechanisms needed continuous testing and adjustment based on actual performance with diverse academic papers.

**2. Risk Mitigation**: By developing core features (PDF upload, vectorization, chat) in increments, technical risks related to vector database performance and LLM integration could be identified and addressed early. Each increment produced a testable prototype, allowing validation of critical assumptions about embedding quality and retrieval relevance before proceeding to subsequent features.

**3. Component-Based Development**: The model aligns well with the separation of concerns between frontend (React), backend (FastAPI), and data layers (ChromaDB), allowing parallel development of increments. The frontend team could work on user interface components while backend development focused on document processing pipelines, with integration occurring at increment boundaries.

**4. User Feedback Integration**: Each iteration produced a working prototype that could be tested with sample research papers, enabling continuous improvement of retrieval relevance and citation accuracy. Feedback from test users informed adjustments to chunking strategies, context window sizes, and prompt engineering for the language model.

**5. Technical Experimentation**: RAG systems require testing different chunking strategies, embedding models, and retrieval methods. The iterative approach facilitated this experimentation without disrupting the overall system. For example, initial iterations used pure semantic search, but later cycles incorporated BM25 keyword matching after testing revealed limitations with acronym retrieval.

Figure 3.2 illustrates the Iterative Incremental development cycle applied to LitSynth, showing how each increment built upon previous work while incorporating lessons learned.

```
                    ┌──────────────────────────────────────┐
                    │   Iterative Incremental Cycle        │
                    │                                      │
                    │    ┌──────────┐                     │
                    │    │ Planning │                     │
                    │    └─────┬────┘                     │
                    │          │                          │
                    │          ↓                          │
                    │    ┌──────────┐                     │
                    │    │  Design  │                     │
                    │    └─────┬────┘                     │
                    │          │                          │
                    │          ↓                          │
                    │  ┌──────────────┐                   │
                    │  │Implementation│                   │
                    │  └──────┬───────┘                   │
                    │         │                           │
                    │         ↓                           │
                    │    ┌─────────┐                      │
                    │    │ Testing │                      │
                    │    └────┬────┘                      │
                    │         │                           │
                    │         ↓                           │
                    │   ┌───────────┐                     │
                    │   │Evaluation │─────┐               │
                    │   └───────────┘     │               │
                    │                     │               │
                    └─────────────────────┼───────────────┘
                                         │
                                         ↓
                              Next Increment or Release

Increment 1: Core RAG System
  - PDF upload and text extraction
  - Document vectorization with ChromaDB
  - Basic chat with semantic search
  - User authentication

Increment 2: Multi-Workspace Support
  - Workspace creation and management
  - Document organization by project
  - Workspace-specific chat sessions

Increment 3: Enhanced Retrieval
  - Hybrid search (BM25 + Vector)
  - Query expansion for improved recall
  - Citation generation with page numbers

Increment 4: Advanced Features
  - OCR for scanned PDFs
  - Batch document upload
  - Chat history export
  - Dark mode UI
```
**Figure 3.2: Iterative Incremental Development Model for LitSynth**

Each increment followed the complete cycle of planning, design, implementation, testing, and evaluation. Lessons learned from testing and user feedback in one increment informed the requirements and design decisions for subsequent increments. This approach proved particularly valuable for optimizing the RAG pipeline, where retrieval quality improvements identified in Increment 1 led to the hybrid search implementation in Increment 3.

---

### 3.4 Analysis of Existing and Proposed System

#### 3.4.1 Description of Existing System

Currently, researchers and students analyze academic papers through manual processes that involve extensive reading, note-taking, and cross-referencing. This section describes the traditional workflow and identifies its key limitations.

**Researchers and Students:**

**Role**: Read and analyze academic papers to extract relevant information, identify key findings, and synthesize knowledge across multiple sources.

**Process**:
- Download PDF papers from academic databases (Google Scholar, arXiv, IEEE Xplore, ResearchGate)
- Manually read each paper sequentially to understand methodology, findings, and conclusions
- Take handwritten or digital notes highlighting important sections
- Create personal annotation systems using PDF readers (Adobe Acrobat, Preview, Foxit) to mark key passages
- Search within PDFs using Ctrl+F (or Cmd+F) for specific keywords
- Manually track citations and references across multiple papers using spreadsheets or note-taking applications
- Maintain separate folders and files for organizing papers by topic, project, or research area
- Re-read papers multiple times when searching for previously identified information
- Copy and paste relevant excerpts into separate documents for synthesis and writing

**Challenges**:
- Time-consuming to read multiple lengthy papers (20-50 pages each), with a typical literature review requiring analysis of 30-100 papers
- Difficult to quickly locate specific information across multiple documents when writing or answering research questions
- No semantic search capability—keyword search limited to exact matches, missing synonyms and related concepts
- Challenging to synthesize insights across 10+ papers simultaneously, as human working memory can only hold limited information
- Manual citation tracking prone to errors and omissions, particularly when dealing with dozens of sources
- Information buried in scanned or image-based PDFs inaccessible to text search, requiring manual visual scanning
- No collaborative workspace for organizing research projects, forcing researchers to use disparate tools (Zotero for references, Notion for notes, email for sharing)
- Difficulty in recalling which specific paper contained particular information after weeks or months

**Limitations of Existing Approach:**

**1. Inefficiency**: Researchers spend significant time re-reading papers to locate previously identified information. Studies indicate that researchers spend an average of 5-10 hours per week simply searching through their accumulated research papers.

**2. Limited Recall**: Human memory limitations make it difficult to recall specific details from papers read weeks or months ago. This leads to redundant reading and potential oversight of relevant information during writing.

**3. No Contextual Search**: Traditional PDF readers lack semantic understanding. Searching for "neural network applications" will not find papers discussing "deep learning use cases" or "artificial neural network implementations," despite the semantic similarity.

**4. Scalability Issues**: As research collections grow beyond 20-30 papers, manual organization becomes unwieldy. Researchers struggle to maintain consistent folder structures and naming conventions across large document collections.

**5. Lack of Citation Traceability**: When answering research questions or writing literature reviews, it is difficult to quickly identify which specific paper contained particular information, leading to time wasted in verification and potential citation errors.

**6. No Cross-Document Analysis**: Comparing methodologies, findings, or approaches across multiple papers requires maintaining separate notes and manually synthesizing information, a cognitively demanding task prone to oversights.

#### 3.4.2 Requirement Elicitation

Requirements for LitSynth were gathered through multiple elicitation techniques to ensure comprehensive understanding of user needs and system expectations. This multi-method approach provided both qualitative insights into user workflows and quantitative validation of identified pain points.

**Elicitation Methods:**

**1. Structured Interviews**: Semi-structured interviews were conducted with 15 participants comprising postgraduate students (8), undergraduate final-year students (5), and faculty members (2) from the Department of Software Engineering, Bayero University Kano. The interview protocol (see Appendix A.1) focused on current research paper analysis workflows, pain points with existing tools, and desired features in an intelligent research assistant. Each interview lasted approximately 30-45 minutes and was conducted in person or via video conference. Interviews were recorded with participant consent and transcribed for thematic analysis.

**2. Survey Questionnaire**: An online survey was distributed to 50 students and researchers to quantify the prevalence of identified challenges and validate findings from interviews. The survey instrument (see Appendix A.2) included both closed-ended questions (Likert scale ratings) and open-ended questions allowing respondents to describe their workflows and frustrations. Key questions addressed time spent on literature review, number of papers typically analyzed per project, current tools used, and preference rankings for potential system features. The survey achieved a 78% response rate with 39 complete responses (see Appendix A.3 for aggregated results and analysis).

**3. Comparative Analysis**: Existing research management and AI-powered document analysis tools were systematically evaluated to identify functional gaps and differentiation opportunities. Tools analyzed included:
   - **Zotero and Mendeley**: Traditional reference managers with PDF storage and basic annotation
   - **Notion AI**: General-purpose knowledge management with AI summarization features
   - **ChatPDF**: AI chat interface for single PDF documents
   - **Elicit AI**: Research-focused tool for finding and synthesizing papers
   - **Semantic Scholar**: Academic search engine with AI-generated summaries

This comparative analysis revealed that while individual tools addressed specific needs (reference management, AI chat, search), no single solution provided integrated multi-document querying with workspace organization and verifiable citations.

**Key Findings:**

**From Academic Researchers (Postgraduate Students and Faculty):**

**Primary Need**: Ability to ask natural language questions across multiple research papers simultaneously rather than searching each PDF individually or using general-purpose chatbots that lack document grounding. As one postgraduate student noted: "I often need to compare how different papers approach the same problem, but doing this manually requires opening multiple PDFs, searching each one, and keeping track of which paper said what."

**Citation Requirement**: Responses must include source citations with page numbers and paper titles to verify information and support academic writing. Faculty members emphasized that "any AI tool for academic use must provide traceable sources—students need to learn to verify claims, not just accept AI responses blindly."

**Workspace Organization**: Need to organize papers into project-specific collections (e.g., "Machine Learning for Healthcare" vs. "Natural Language Processing Research") rather than having all papers in a single repository. Researchers typically work on multiple projects simultaneously and need clear separation.

**PDF Processing Capability**: Many papers, especially older publications and conference proceedings, are scanned images rather than text-based PDFs. The system must support Optical Character Recognition (OCR) to extract text from image-based PDFs, making them searchable and analyzable.

**From Undergraduate Students:**

**Ease of Use**: Simple, intuitive interface preferred over complex research management software with steep learning curves. As one undergraduate noted: "I don't have time to learn complicated software—I just want to upload my papers and start asking questions."

**Quick Answers**: Prioritize rapid responses to specific questions over comprehensive summaries. Students often seek targeted information (e.g., "What evaluation metrics were used?") rather than full document summarization.

**Cost Constraints**: Free or low-cost solution essential. Many existing AI tools (ChatPDF Pro, Elicit Plus) require expensive monthly subscriptions ($20-30/month) that are prohibitive for students. Access to institutional resources is often limited or requires complex VPN setups.

**Challenges Identified (from Survey Results, n=39):**

- **87% of survey respondents** spend 5+ hours per week manually searching through PDFs for information
- **73% reported difficulty** synthesizing information across more than 5 papers simultaneously
- **68% expressed frustration** with keyword-only search missing semantically related content (e.g., searching "RNN" does not find "recurrent neural network" or "LSTM")
- **91% desired automatic citation generation** when extracting information from papers
- **82% indicated** that existing tools do not adequately support multi-document analysis
- **76% prioritized** accuracy and citation verification over response speed

**Additional Insights from Open-Ended Survey Responses:**

Respondents frequently mentioned frustrations with:
- "Having to remember which paper I read something in"
- "Spending hours looking for that one paragraph I highlighted weeks ago"
- "Unable to search for concepts across all my papers at once"
- "Existing AI chat tools give answers but don't tell me which paper the information came from"

(See Appendix A for complete interview transcripts, survey questionnaire, detailed statistical analysis, and thematic coding results)

#### 3.4.3 Requirements Definition

Based on the elicitation findings, the requirements for LitSynth were categorized into functional (user) requirements and non-functional requirements. Functional requirements define what the system must do, while non-functional requirements specify quality attributes and constraints.

**Functional Requirements:**

**FR1**: The system shall allow users to create and manage multiple workspaces for organizing research projects. Each workspace represents a distinct research area or project (e.g., "Thesis Literature", "Course Project Papers") and maintains isolated document collections and chat histories.

**FR2**: The system shall accept PDF document uploads and automatically extract text content, including OCR (Optical Character Recognition) processing for scanned or image-based PDFs. The system must support batch upload of multiple documents simultaneously.

**FR3**: The system shall enable users to ask natural language questions about uploaded documents through a chat interface. Questions may reference single documents or request synthesis across multiple papers.

**FR4**: The system shall retrieve relevant content from documents using semantic search based on question context, not limited to exact keyword matching. The search mechanism must understand synonyms, related concepts, and semantic similarity.

**FR5**: The system shall generate AI-powered responses with citations including source document names and page numbers. Each response must be grounded in the uploaded documents with traceable references to support verification.

**FR6**: The system shall maintain chat history for each workspace, allowing users to review previous conversations. Users must be able to create multiple chat sessions within a workspace to organize different research questions or topics.

**FR7**: The system shall support user authentication and secure access to personal workspaces. User credentials must be protected, and workspace access must be restricted to the owning user only.

**FR8**: The system shall allow users to view uploaded documents and their processing status, including document metadata (filename, upload date, page count, number of chunks generated, processing state).

**FR9**: The system shall enable deletion of documents and chats from workspaces. Deleting a document must remove both the file and its associated vector embeddings. Deleting a chat must remove all message history.

**FR10**: The system shall provide a dashboard for managing multiple research workspaces, displaying workspace names, document counts, chat session counts, and last activity timestamps.

**Non-Functional Requirements:**

**NFR1 - Performance**: The system shall process PDF uploads and generate vector embeddings within 30 seconds for documents up to 50 pages. Longer documents may take proportionally longer but must provide progress indicators to users.

**NFR2 - Response Time**: Chat responses shall be generated within 5 seconds for queries against databases containing up to 100 documents. This ensures interactive conversation flow without frustrating delays.

**NFR3 - Accuracy**: Retrieved document chunks shall maintain semantic relevance score above 0.7 (cosine similarity) to ensure citation accuracy and response quality. The system must filter out low-relevance chunks that could introduce noise.

**NFR4 - Scalability**: The system shall support up to 100 documents per workspace and 50 concurrent users without performance degradation. This capacity accommodates typical research project scales and small research group usage.

**NFR5 - Security**: User authentication shall use JWT (JSON Web Token) tokens with secure password hashing using bcrypt algorithm. Document access shall be restricted to workspace owners only, enforced through database-level isolation and API middleware authorization checks.

**NFR6 - Privacy**: All document processing (text extraction, chunking, embedding generation, vector storage) shall occur locally without sending document content to external APIs, except for LLM queries which only transmit relevant context chunks, not entire documents. This preserves confidentiality of unpublished research.

**NFR7 - Usability**: The user interface shall be intuitive enough for non-technical users to upload documents and ask questions without training or documentation. Workflows must follow conventional web application patterns with clear visual feedback.

**NFR8 - Reliability**: The system shall maintain 99% uptime during normal operation with automatic error recovery for failed PDF processing (retry mechanism, graceful degradation). Users must receive clear error messages when failures occur.

**NFR9 - Maintainability**: The system architecture shall follow separation of concerns with distinct frontend (React), backend (FastAPI), and database (PostgreSQL, ChromaDB) layers to facilitate future enhancements. Code must adhere to industry-standard patterns and include inline documentation.

**NFR10 - Compatibility**: The frontend shall function correctly on modern browsers (Chrome, Firefox, Safari, Edge) released within the past 2 years. The interface must support responsive design for tablet and desktop devices (minimum resolution 1024×768).

#### 3.4.4 Requirement Analysis

Requirements were analyzed using use case modeling to visualize system interactions and define detailed operational scenarios. This section presents the use case diagram and detailed descriptions for critical use cases.

**Use Case Diagram:**

Figure 3.3 illustrates the primary use cases for LitSynth and the interactions between users and the system. The diagram identifies the main actor (Researcher/Student) and automated system processes.

```
                                    LitSynth System

                                 ┌────────────────────┐
          ┌──────────────────────┤  Register/Login    │
          │                      └────────────────────┘
          │
          │                      ┌────────────────────┐
          │  ┌───────────────────┤  Create Workspace  │
          │  │                   └────────────────────┘
          │  │
          │  │                   ┌────────────────────┐
    ┏━━━━━┷━━┷━━━┓  ┌───────────┤  Upload PDF        │
    ┃            ┃  │            └────────────────────┘
    ┃   User     ┃  │                      │
    ┃(Researcher/┃  │                      │ <<include>>
    ┃  Student)  ┃  │                      ↓
    ┃            ┃  │            ┌────────────────────┐
    ┗━━━━━┯━━┯━━━┛  │            │  Process Document  │◄─── System
          │  │      │            │ (Extract, Chunk,   │     (Automated)
          │  │      │            │  Vectorize)        │
          │  │      │            └────────────────────┘
          │  │      │
          │  │      │            ┌────────────────────┐
          │  │      └────────────┤  Ask Question      │
          │  │                   │  (Chat)            │
          │  │                   └────────────────────┘
          │  │                             │ <<include>>
          │  │                             ↓
          │  │                   ┌────────────────────┐
          │  │                   │  Retrieve Context  │◄─── System
          │  │                   │  (Hybrid Search)   │
          │  │                   └────────────────────┘
          │  │                             │ <<include>>
          │  │                             ↓
          │  │                   ┌────────────────────┐
          │  │                   │ Generate Response  │◄─── System
          │  │                   │ (LLM with Citations)│    (Gemini API)
          │  │                   └────────────────────┘
          │  │
          │  │                   ┌────────────────────┐
          │  └───────────────────┤ View Chat History  │
          │                      └────────────────────┘
          │
          │                      ┌────────────────────┐
          │  ┌───────────────────┤ View Documents     │
          │  │                   └────────────────────┘
          │  │
          │  │                   ┌────────────────────┐
          │  ├───────────────────┤ Delete Document    │
          │  │                   └────────────────────┘
          │  │
          │  │                   ┌────────────────────┐
          │  ├───────────────────┤ Delete Chat        │
          │  │                   └────────────────────┘
          │  │
          │  │                   ┌────────────────────┐
          └──┴───────────────────┤ Logout             │
                                 └────────────────────┘
```
**Figure 3.3: Use Case Diagram for LitSynth**

The use case diagram shows that core functionality revolves around document management (upload, view, delete) and intelligent querying (chat with AI). System-automated processes (document processing, context retrieval, response generation) are indicated with arrows showing their relationship to user-initiated actions.

**Detailed Use Case Descriptions:**

Detailed descriptions are provided for the three highest-priority use cases that represent the core value proposition of LitSynth: uploading documents, asking questions, and user authentication.

**Table 3.1: Use Case Description - Upload PDF Documents**

| Attribute | Description |
|-----------|-------------|
| **Use Case Name** | Upload PDF Documents |
| **Priority** | High |
| **Actor** | User (Researcher/Student) |
| **Description** | This use case describes the process of uploading academic research papers in PDF format to a workspace for analysis. |
| **Trigger** | User clicks "Upload PDF" button in workspace interface |
| **Preconditions** | 1. User is authenticated and logged in<br>2. User has selected or created a workspace<br>3. System is connected to ChromaDB vector database |
| **Normal Course** | 1. User clicks "Upload PDF" button in workspace<br>2. System displays file selection dialog<br>3. User selects one or more PDF files from local storage<br>4. System validates file format (PDF only) and size (<50MB per file)<br>5. System displays upload progress indicator<br>6. System extracts text from PDF using PyMuPDF library<br>7. If PDF contains scanned images, system applies OCR using Google Vision API (see Alternative Course A)<br>8. System splits document into semantic chunks (700 characters, 100 overlap) using RecursiveCharacterTextSplitter<br>9. System generates 768-dimensional embeddings for each chunk using nomic-embed-text-v1.5 model<br>10. System stores embeddings in ChromaDB collection with metadata (filename, page number, workspace_id)<br>11. System saves document record to PostgreSQL database (filename, page count, chunk count, upload timestamp)<br>12. System displays success notification with document details<br>13. Document appears in workspace document list<br>14. Use case ends |
| **Alternative Course A<br>(Scanned PDF/OCR)** | **7a.** PDF contains scanned images (no selectable text):<br>1. System detects absence of text layer in PDF<br>2. System converts PDF pages to images<br>3. System sends images to Google Vision API for OCR<br>4. System receives extracted text from OCR service<br>5. Return to step 8 of Normal Course |
| **Alternative Course B<br>(Invalid File)** | **4b.** Invalid file format or size exceeds limit:<br>1. System displays error message: "Invalid file format. Please upload PDF files under 50MB"<br>2. Return to step 2 of Normal Course |
| **Alternative Course C<br>(Processing Failure)** | **8c.** Network error or processing exception during embedding generation:<br>1. System catches exception and logs error details<br>2. System displays error notification: "Failed to process [filename]. Please try again."<br>3. System does not save document record to database<br>4. Use case ends |
| **Post Conditions** | 1. PDF document is stored in workspace documents folder<br>2. Document chunks are vectorized and stored in ChromaDB<br>3. Document metadata is saved in PostgreSQL<br>4. Document is searchable via chat interface |
| **Exceptions** | - "File size exceeds 50MB limit"<br>- "OCR service unavailable. Please try again."<br>- "Failed to extract text from PDF"<br>- "Unsupported file format. Please upload PDF files only." |

---

**Table 3.2: Use Case Description - Ask Question (Chat)**

| Attribute | Description |
|-----------|-------------|
| **Use Case Name** | Ask Question (Chat) |
| **Priority** | High |
| **Actor** | User (Researcher/Student) |
| **Description** | This use case enables users to ask natural language questions about uploaded documents and receive AI-generated responses with citations. |
| **Trigger** | User types question and clicks "Send" button or presses Enter in chat interface |
| **Preconditions** | 1. User is authenticated and logged in<br>2. User has selected a workspace with at least 1 uploaded document<br>3. User has created or selected a chat session<br>4. Document processing is complete (all documents vectorized) |
| **Normal Course** | 1. User enters question in chat input field (e.g., "What are the main findings about neural networks?")<br>2. User clicks "Send" button or presses Enter key<br>3. System displays user message in chat history<br>4. System shows "thinking" indicator with animated loading state<br>5. System generates 768-dimensional query embedding using nomic-embed-text-v1.5 model<br>6. System performs hybrid search in ChromaDB workspace collection:<br>&nbsp;&nbsp;&nbsp;- Dense vector similarity search (retrieves top 16 chunks by cosine similarity)<br>&nbsp;&nbsp;&nbsp;- BM25 sparse keyword search (retrieves top 16 chunks by term frequency)<br>&nbsp;&nbsp;&nbsp;- Reciprocal Rank Fusion combines results with weights (0.6 semantic, 0.4 BM25)<br>7. System retrieves top 4 most relevant document chunks with metadata (filename, page number, chunk text)<br>8. System constructs RAG prompt containing:<br>&nbsp;&nbsp;&nbsp;- User question<br>&nbsp;&nbsp;&nbsp;- Retrieved context chunks with source labels<br>&nbsp;&nbsp;&nbsp;- System instruction to provide citations in format [p.X, DocumentName]<br>9. System sends prompt to Google Gemini 2.0 Flash API<br>10. System receives LLM response with answer and inline citations<br>11. System parses citations from LLM response (extracts page numbers and filenames)<br>12. System displays AI response in chat interface with formatted text<br>13. System displays citation cards below response showing:<br>&nbsp;&nbsp;&nbsp;- Source document filename (clickable)<br>&nbsp;&nbsp;&nbsp;- Page number<br>&nbsp;&nbsp;&nbsp;- Relevant snippet from original chunk (first 200 characters)<br>14. System saves user message and assistant response to PostgreSQL chat_messages table<br>15. System updates chat session's updated_at timestamp<br>16. Use case ends |
| **Alternative Course A<br>(No Relevant Context)** | **6a.** No relevant documents found (all similarity scores < 0.5):<br>1. System responds with message: "I couldn't find relevant information in your uploaded documents to answer this question. Please verify your documents contain this topic or rephrase your question."<br>2. System does not invoke LLM API (cost optimization)<br>3. Return to step 1 (user can rephrase question) |
| **Alternative Course B<br>(LLM Service Error)** | **9b.** LLM API error (rate limit exceeded, network timeout, service unavailable):<br>1. System catches API exception and logs error<br>2. System displays error message: "Unable to generate response. Please try again in a moment."<br>3. System does not save failed message to database<br>4. Use case ends |
| **Alternative Course C<br>(Empty Query)** | **1c.** User submits empty or whitespace-only message:<br>1. System validates input and rejects submission<br>2. System displays inline validation: "Please enter a question."<br>3. Use case ends without API call |
| **Post Conditions** | 1. User question and AI response are saved in chat history<br>2. Chat session updated_at timestamp is refreshed<br>3. User can click citations to view source context<br>4. Conversation context is preserved for follow-up questions |
| **Exceptions** | - "No documents uploaded. Please upload PDFs first."<br>- "LLM service temporarily unavailable. Please try again."<br>- "Empty question. Please enter your query."<br>- "Document processing in progress. Please wait." |

---

**Table 3.3: Use Case Description - Register/Login**

| Attribute | Description |
|-----------|-------------|
| **Use Case Name** | Register/Login |
| **Priority** | High |
| **Actor** | User (Researcher/Student) |
| **Description** | This use case describes user registration for new accounts and authentication for existing users. |
| **Trigger** | User navigates to login page or registration page |
| **Preconditions** | 1. User has network connectivity to backend server<br>2. Database is operational |
| **Normal Course<br>(Registration)** | 1. User clicks "Register" or "Sign Up" link<br>2. System displays registration form<br>3. User enters email address and password<br>4. System validates email format and password strength (min 8 characters)<br>5. System checks if email already exists in database<br>6. System hashes password using bcrypt algorithm<br>7. System creates new user record in PostgreSQL users table<br>8. System generates JWT token with user ID and email in payload<br>9. System returns JWT token to frontend<br>10. Frontend stores token in localStorage<br>11. System redirects user to dashboard<br>12. Use case ends |
| **Normal Course<br>(Login)** | 1. User enters email and password on login page<br>2. User clicks "Login" button<br>3. System queries database for user with matching email<br>4. System verifies password hash using bcrypt.compare()<br>5. System generates JWT token with user ID and email<br>6. System returns JWT token and user profile to frontend<br>7. Frontend stores token in localStorage<br>8. System redirects user to dashboard showing user's workspaces<br>9. Use case ends |
| **Alternative Course A<br>(Email Already Exists)** | **5a.** During registration, email already exists:<br>1. System displays error: "An account with this email already exists. Please login."<br>2. System provides link to login page<br>3. Use case ends |
| **Alternative Course B<br>(Invalid Credentials)** | **4b.** During login, email not found or password incorrect:<br>1. System displays error: "Invalid email or password. Please try again."<br>2. System does not reveal whether email exists (security best practice)<br>3. Return to step 1 of Login course |
| **Alternative Course C<br>(Weak Password)** | **4c.** During registration, password does not meet strength requirements:<br>1. System displays validation error: "Password must be at least 8 characters long"<br>2. Return to step 3 of Registration course |
| **Post Conditions** | 1. User is authenticated with valid JWT token<br>2. User session is active<br>3. User has access to dashboard and workspace creation<br>4. Token is stored in localStorage for subsequent API requests |
| **Exceptions** | - "Invalid email format"<br>- "Password must be at least 8 characters"<br>- "Email already registered"<br>- "Database connection failed"<br>- "Unable to create account. Please try again." |

---

**Table 3.4: Use Case Description - Create Workspace**

| Attribute | Description |
|-----------|-------------|
| **Use Case Name** | Create Workspace |
| **Priority** | Medium |
| **Actor** | User (Researcher/Student) |
| **Description** | This use case enables users to create new workspaces for organizing research papers by project or topic. |
| **Trigger** | User clicks "Create Workspace" or "New Workspace" button on dashboard |
| **Preconditions** | 1. User is authenticated and logged in<br>2. User has access to dashboard |
| **Normal Course** | 1. User clicks "Create Workspace" button<br>2. System displays workspace creation modal/form<br>3. User enters workspace name (e.g., "Thesis Literature", "ML Research")<br>4. User clicks "Create" button<br>5. System validates workspace name (not empty, max 100 characters)<br>6. System generates unique workspace_id (UUID)<br>7. System creates workspace record in PostgreSQL with user_id foreign key<br>8. System initializes empty ChromaDB collection with workspace_id as collection name<br>9. System displays success notification: "Workspace '[name]' created successfully"<br>10. System adds workspace card to dashboard<br>11. System automatically navigates user into new workspace<br>12. Use case ends |
| **Alternative Course A<br>(Empty Name)** | **5a.** User submits empty or whitespace-only name:<br>1. System displays validation error: "Workspace name cannot be empty"<br>2. Return to step 3 of Normal Course |
| **Alternative Course B<br>(Name Too Long)** | **5b.** User enters name exceeding 100 characters:<br>1. System displays validation error: "Workspace name must be 100 characters or less"<br>2. Return to step 3 of Normal Course |
| **Alternative Course C<br>(Database Error)** | **7c.** Database error during workspace creation:<br>1. System catches exception and logs error<br>2. System displays error: "Unable to create workspace. Please try again."<br>3. System rolls back any partial changes<br>4. Use case ends |
| **Post Conditions** | 1. New workspace exists in PostgreSQL database<br>2. Empty ChromaDB collection exists for workspace<br>3. Workspace appears on user's dashboard<br>4. User can upload documents to workspace<br>5. User can create chat sessions in workspace |
| **Exceptions** | - "Workspace name cannot be empty"<br>- "Name must be 100 characters or less"<br>- "Failed to create workspace. Please try again."<br>- "Database connection error" |

---

### 3.5 System Design

#### 3.5.1 Description of Proposed System

The proposed LitSynth system employs a Retrieval-Augmented Generation (RAG) architecture to enable intelligent querying of academic research papers. This section describes the system's operational workflows through behavioral diagrams that illustrate key processes.

**Document Processing Workflow:**

Figure 3.4 presents the activity diagram for PDF document upload and processing. This workflow transforms uploaded research papers into searchable, queryable knowledge through multiple automated stages.

```
                                   ┌──────────────────────┐
                                   │       START          │
                                   └──────────┬───────────┘
                                              │
                                              ↓
                                   ┌──────────────────────┐
                                   │ User selects PDF     │
                                   │ file(s) from local   │
                                   │ storage              │
                                   └──────────┬───────────┘
                                              │
                                              ↓
                                   ┌──────────────────────┐
                                   │  Valid PDF format?   │
                          ┌────────┤  Size < 50MB?        │
                          │ NO     └──────────┬───────────┘
                          │                   │ YES
                          ↓                   ↓
                 ┌────────────────┐   ┌──────────────────┐
                 │ Display error  │   │ Upload file to   │
                 │ message        │   │ backend server   │
                 └────────┬───────┘   └─────────┬────────┘
                          │                     │
                          │                     ↓
                          │           ┌──────────────────────┐
                          │           │ Extract text from    │
                          │           │ PDF (PyMuPDF)        │
                          │           └─────────┬────────────┘
                          │                     │
                          │                     ↓
                          │           ┌──────────────────────┐
                          │           │ Text extracted       │
                          │           │ successfully?        │
                          │  ┌────────┤                      │
                          │  │ NO     └──────────┬───────────┘
                          │  │                   │ YES
                          │  ↓                   │
                          │  ┌────────────────┐  │
                          │  │ Apply OCR      │  │
                          │  │ (Google Vision)│  │
                          │  └────────┬───────┘  │
                          │           │          │
                          │           ↓          │
                          │  ┌────────────────┐  │
                          │  │ Receive OCR    ├──┘
                          │  │ extracted text │
                          │  └────────┬───────┘
                          │           │
                          │           ↓
                          │  ┌────────────────────────┐
                          │  │ Split text into chunks │
                          │  │ (RecursiveCharacter    │
                          │  │  TextSplitter:         │
                          │  │  700 chars, 100 overlap│
                          │  └────────┬───────────────┘
                          │           │
                          │           ↓
                          │  ┌────────────────────────┐
                          │  │ For each chunk:        │
                          │  │ - Generate embedding   │
                          │  │   (nomic-embed-text-   │
                          │  │   v1.5, 768 dims)      │
                          │  │ - Store in ChromaDB    │
                          │  │   with metadata        │
                          │  └────────┬───────────────┘
                          │           │
                          │           ↓
                          │  ┌────────────────────────┐
                          │  │ Save document record   │
                          │  │ to PostgreSQL          │
                          │  │ (filename, pages,      │
                          │  │  chunks, timestamp)    │
                          │  └────────┬───────────────┘
                          │           │
                          │           ↓
                          │  ┌────────────────────────┐
                          │  │ Display success        │
                          │  │ notification to user   │
                          │  └────────┬───────────────┘
                          │           │
                          └───────────┤
                                      ↓
                           ┌──────────────────────┐
                           │        END           │
                           └──────────────────────┘
```
**Figure 3.4: Activity Diagram - PDF Upload and Processing**

When a user uploads a PDF, the system first validates the file format and size constraints (maximum 50MB). Valid PDFs are processed through PyMuPDF for text extraction. If the PDF lacks a text layer (indicating a scanned document), the system automatically invokes Google Vision API for Optical Character Recognition (OCR) to extract text from images.

Extracted text is then segmented into semantic chunks using LangChain's RecursiveCharacterTextSplitter with a chunk size of 700 characters and 100-character overlap to preserve context at chunk boundaries. Each chunk is converted to a 768-dimensional embedding vector using the nomic-embed-text-v1.5 model from HuggingFace. These embeddings are stored in ChromaDB, a local persistent vector database, along with metadata including the source filename, page number, and workspace identifier. This vectorization process enables semantic similarity search during subsequent chat interactions.

**Chat Interaction Workflow:**

Figure 3.5 illustrates the sequence diagram for the chat question-answer process, showing the interactions between system components during a user query.

```
   User         Frontend         Backend        Embeddings      ChromaDB      Gemini API    PostgreSQL
     │              │               │               Model          │              │             │
     │              │               │                  │           │              │             │
     ├─ Enter      │               │                  │           │              │             │
     │  question   │               │                  │           │              │             │
     │  and click  │               │                  │           │              │             │
     │  Send       │               │                  │           │              │             │
     │              │               │                  │           │              │             │
     ├──────────────>               │                  │           │              │             │
     │              │               │                  │           │              │             │
     │              ├─ POST /chat ─>│                  │           │              │             │
     │              │  {query,      │                  │           │              │             │
     │              │   chat_id,    │                  │           │              │             │
     │              │   workspace}  │                  │           │              │             │
     │              │               │                  │           │              │             │
     │              │               ├─ Validate JWT ──>│           │              │             │
     │              │               │  token           │           │              │             │
     │              │               │                  │           │              │             │
     │              │               ├─ Generate query ─>           │              │             │
     │              │               │  embedding       │           │              │             │
     │              │               │                  │           │              │             │
     │              │               │<─ 768-dim vector─┤           │              │             │
     │              │               │                  │           │              │             │
     │              │               ├─ Hybrid search ──────────────>              │             │
     │              │               │  (vector + BM25) │           │              │             │
     │              │               │                  │           │              │             │
     │              │               │<─ Top 4 chunks ──────────────┤              │             │
     │              │               │  with metadata   │           │              │             │
     │              │               │                  │           │              │             │
     │              │               ├─ Construct RAG ──┤           │              │             │
     │              │               │  prompt with     │           │              │             │
     │              │               │  context         │           │              │             │
     │              │               │                  │           │              │             │
     │              │               ├─ Send prompt for completion ─────────────────>            │
     │              │               │                  │           │              │             │
     │              │               │<─ Generated response with citations ─────────┤             │
     │              │               │                  │           │              │             │
     │              │               ├─ Parse citations─┤           │              │             │
     │              │               │  from response   │           │              │             │
     │              │               │                  │           │              │             │
     │              │               ├─ Save user msg + AI response ────────────────────────────>│
     │              │               │                  │           │              │             │
     │              │               │                  │           │              │<────────────┤
     │              │               │                  │           │              │   Saved     │
     │              │<─ Return {response, citations} ──┤           │              │             │
     │              │               │                  │           │              │             │
     │<─────────────┤               │                  │           │              │             │
     │  Display AI  │               │                  │           │              │             │
     │  answer with │               │                  │           │              │             │
     │  citation    │               │                  │           │              │             │
     │  boxes       │               │                  │           │              │             │
     │              │               │                  │           │              │             │
```
**Figure 3.5: Sequence Diagram - Chat Interaction**

When a user submits a natural language question, the frontend sends the query to the backend along with the chat session and workspace identifiers. The backend first validates the user's JWT token for authentication. The system then generates an embedding vector for the query using the same nomic-embed-text-v1.5 model used during document processing, ensuring semantic consistency.

The backend performs a hybrid search in ChromaDB combining two retrieval methods: dense vector similarity search (using cosine distance of embedding vectors) and BM25 sparse retrieval (keyword-based matching). Reciprocal Rank Fusion merges the ranked results from both approaches, with weights of 0.6 for semantic search and 0.4 for BM25. This hybrid approach improves retrieval quality by capturing both semantic similarity and exact term matches (important for acronyms like "LSTM" or "RAG").

The top 4 most relevant document chunks are retrieved along with their metadata (source filename, page number, chunk text). These chunks serve as context for the Large Language Model. The system constructs a RAG prompt containing the user's question, the retrieved context labeled with source information, and instructions to provide citations in the format [p.X, DocumentName].

This prompt is sent to Google Gemini 2.0 Flash API, which generates a contextually grounded response. The system parses citations from the LLM output, extracting page numbers and document names. Both the user query and AI response are persisted in PostgreSQL for chat history, and the response is displayed to the user with citation cards showing the original document name, page number, and a text snippet for verification.

#### 3.5.2 Architecture Design

LitSynth employs a three-tier client-server architecture comprising a frontend presentation layer, backend application layer, and dual-database persistence layer (relational and vector). Figure 3.6 illustrates the package diagram showing the architectural components and their interactions.

```
┌───────────────────────────────────────────────────────────────────────┐
│                     FRONTEND LAYER (React)                            │
│                                                                       │
│  ┌─────────────────────────────────────────────────────────────────┐ │
│  │                      COMPONENTS                                  │ │
│  │                                                                  │ │
│  │  Page Components:                                                │ │
│  │  - ChatPage: Main interface for document Q&A                    │ │
│  │  - DashboardPage: Workspace management overview                 │ │
│  │  - LoginPage/RegisterPage: User authentication                  │ │
│  │  - ProfilePage: User account and system information             │ │
│  │                                                                  │ │
│  │  Reusable Components:                                            │ │
│  │  - Layout: Navigation bar and page structure                    │ │
│  │  - Modal: Dialog overlays for forms                             │ │
│  │  - ThemeToggle: Dark mode switcher                              │ │
│  │  - DocumentList: Display uploaded PDFs with metadata            │ │
│  │  - ChatHistory: Message thread display with citations           │ │
│  └─────────────────────────────────────────────────────────────────┘ │
│                                                                       │
│  ┌─────────────────────────────────────────────────────────────────┐ │
│  │                   STATE MANAGEMENT (Zustand)                     │ │
│  │                                                                  │ │
│  │  - authStore: User authentication state (JWT token, user        │ │
│  │               profile, login/logout actions)                     │ │
│  │  - themeStore: UI theme preferences (light/dark mode)           │ │
│  └─────────────────────────────────────────────────────────────────┘ │
│                                                                       │
│  ┌─────────────────────────────────────────────────────────────────┐ │
│  │                        SERVICES                                  │ │
│  │                                                                  │ │
│  │  - apiService: HTTP client (Axios) for backend communication    │ │
│  │    • Request/response interceptors for JWT token attachment     │ │
│  │    • Error handling and retry logic                             │ │
│  │  - exportService: Chat history export to Markdown/JSON          │ │
│  └─────────────────────────────────────────────────────────────────┘ │
└───────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ HTTP/REST API (JWT Authentication)
                                    ↓
┌───────────────────────────────────────────────────────────────────────┐
│                   BACKEND LAYER (FastAPI - Python)                    │
│                                                                       │
│  ┌─────────────────────────────────────────────────────────────────┐ │
│  │                      API ENDPOINTS                               │ │
│  │                                                                  │ │
│  │  Authentication:                                                 │ │
│  │  - POST /auth/register: User registration with password hashing │ │
│  │  - POST /auth/login: JWT token generation                       │ │
│  │                                                                  │ │
│  │  Workspaces:                                                     │ │
│  │  - GET /workspaces: List user's workspaces                      │ │
│  │  - POST /workspaces: Create new workspace                       │ │
│  │  - DELETE /workspaces/{id}: Delete workspace and all data       │ │
│  │                                                                  │ │
│  │  Documents:                                                      │ │
│  │  - POST /upload: PDF upload and processing                      │ │
│  │  - GET /documents: List workspace documents                     │ │
│  │  - DELETE /documents/{id}: Remove document and embeddings       │ │
│  │                                                                  │ │
│  │  Chat:                                                           │ │
│  │  - POST /chat: Send question, get AI response with citations    │ │
│  │  - GET /chats: List workspace chat sessions                     │ │
│  │  - GET /chats/{id}/messages: Retrieve chat history              │ │
│  │  - DELETE /chats/{id}: Delete chat session                      │ │
│  └─────────────────────────────────────────────────────────────────┘ │
│                                                                       │
│  ┌─────────────────────────────────────────────────────────────────┐ │
│  │                     BUSINESS LOGIC                               │ │
│  │                                                                  │ │
│  │  processors.py:                                                  │ │
│  │  - PDFProcessor: Text extraction using PyMuPDF                  │ │
│  │  - GoogleVisionOCR: OCR for scanned PDFs                        │ │
│  │  - DocumentChunker: RecursiveCharacterTextSplitter (700/100)    │ │
│  │                                                                  │ │
│  │  chat.py:                                                        │ │
│  │  - RAG pipeline orchestration                                    │ │
│  │  - Context retrieval from ChromaDB                              │ │
│  │  - Prompt construction for Gemini LLM                           │ │
│  │  - Title generation for new chats                               │ │
│  │                                                                  │ │
│  │  retrieval.py:                                                   │ │
│  │  - bm25_search: Sparse keyword retrieval                        │ │
│  │  - reciprocal_rank_fusion: Merge semantic + BM25 results        │ │
│  │  - expand_query: LLM-based query reformulation                  │ │
│  │                                                                  │ │
│  │  vector.py:                                                      │ │
│  │  - ChromaDB client initialization                               │ │
│  │  - Vector store operations (upsert, delete, search)             │ │
│  │  - Collection management per workspace                          │ │
│  └─────────────────────────────────────────────────────────────────┘ │
│                                                                       │
│  ┌─────────────────────────────────────────────────────────────────┐ │
│  │                   EXTERNAL INTEGRATIONS                          │ │
│  │                                                                  │ │
│  │  - Google Gemini 2.0 Flash API: LLM for response generation     │ │
│  │  - Google Vision API: OCR for scanned PDFs                      │ │
│  │  - HuggingFace Transformers: Local embedding model              │ │
│  └─────────────────────────────────────────────────────────────────┘ │
└───────────────────────────────────────────────────────────────────────┘
                    │                              │
                    │                              │
                    ↓                              ↓
┌──────────────────────────────┐  ┌────────────────────────────────────┐
│    DATA LAYER                │  │   VECTOR DATABASE                  │
│    (PostgreSQL/SQLModel)     │  │   (ChromaDB)                       │
│                              │  │                                    │
│  Tables:                     │  │  Collections (one per workspace):  │
│  ┌────────────────────────┐  │  │  ┌──────────────────────────────┐ │
│  │ users                  │  │  │  │ Embeddings + Metadata:       │ │
│  │ - id (PK)              │  │  │  │ - id: "{doc_id}#{uuid}"      │ │
│  │ - email (unique)       │  │  │  │ - embedding: 768-dim vector  │ │
│  │ - hashed_password      │  │  │  │ - metadata:                  │ │
│  │ - created_at           │  │  │  │   • doc_id                   │ │
│  └────────────────────────┘  │  │  │   • source (filename)        │ │
│                              │  │  │   • page (page number)       │ │
│  ┌────────────────────────┐  │  │  │   • text (chunk content)     │ │
│  │ workspaces             │  │  │  └──────────────────────────────┘ │
│  │ - workspace_id (PK)    │  │  │                                    │
│  │ - name                 │  │  │  Search Operations:                │
│  │ - user_id (FK)         │  │  │  - Cosine similarity (vector)      │
│  │ - created_at           │  │  │  - BM25 keyword matching           │
│  │ - updated_at           │  │  │  - Reciprocal Rank Fusion          │
│  └────────────────────────┘  │  │                                    │
│                              │  │  Persistence:                      │
│  ┌────────────────────────┐  │  │  - Local storage: ./data/chromadb  │
│  │ documents              │  │  │  - No external API calls           │
│  │ - doc_id (PK)          │  │  └────────────────────────────────────┘
│  │ - workspace_id (FK)    │  │
│  │ - filename             │  │
│  │ - file_path            │  │
│  │ - pages                │  │
│  │ - chunks               │  │
│  │ - status               │  │
│  │ - upload_date          │  │
│  └────────────────────────┘  │
│                              │
│  ┌────────────────────────┐  │
│  │ chats                  │  │
│  │ - chat_id (PK)         │  │
│  │ - workspace_id (FK)    │  │
│  │ - title                │  │
│  │ - created_at           │  │
│  │ - updated_at           │  │
│  │ - message_count        │  │
│  └────────────────────────┘  │
│                              │
│  ┌────────────────────────┐  │
│  │ chat_messages          │  │
│  │ - id (PK)              │  │
│  │ - chat_id (FK)         │  │
│  │ - role (user/assistant)│  │
│  │ - content (text)       │  │
│  │ - timestamp            │  │
│  │ - sources (JSONB)      │  │
│  └────────────────────────┘  │
└──────────────────────────────┘
```
**Figure 3.6: System Architecture - Package Diagram**

**Frontend Layer:**

The presentation layer is built using React 18 with TypeScript for type safety. The component hierarchy includes page-level components (ChatPage, DashboardPage, LoginPage, RegisterPage, ProfilePage) and reusable UI components (Layout, Modal, ThemeToggle, DocumentList, ChatHistory). State management is handled through Zustand stores: `authStore` maintains user authentication state including the JWT token and user profile with login/logout actions, while `themeStore` manages UI theme preferences for dark mode support. The `apiService` module encapsulates all HTTP communications with the backend using Axios, implementing request interceptors for automatic JWT token attachment to authenticated requests and response interceptors for centralized error handling. The `exportService` provides functionality to export chat history to Markdown or JSON formats for external use.

**Backend Layer:**

The application layer uses FastAPI, a modern Python web framework chosen for its automatic OpenAPI documentation generation, native async/await support for concurrent request handling, and type-checked request/response models using Pydantic for data validation. The backend is structured into modular components organized by responsibility:

**main.py** defines RESTful API endpoints organized by resource tags (auth, workspaces, documents, chat). It implements JWT-based authentication using middleware that validates bearer tokens on protected routes, extracting user identity from token claims to enforce workspace ownership.

**processors.py** handles the document processing pipeline. `PDFProcessor` extracts text from PDFs using the PyMuPDF (fitz) library; if text extraction yields insufficient content (indicating a scanned PDF), `GoogleVisionOCR` performs Optical Character Recognition by sending page images to Google Vision API. `DocumentChunker` splits extracted text using LangChain's RecursiveCharacterTextSplitter with 700-character chunks and 100-character overlap to maintain semantic continuity across chunk boundaries.

**chat.py** implements the RAG (Retrieval-Augmented Generation) pipeline, orchestrating query embedding generation, context retrieval from ChromaDB using hybrid search, prompt construction for the Gemini LLM with retrieved context and citation instructions, and parsing of generated responses to extract page numbers and document names for citation display. It also includes `generate_chat_title()` which uses the LLM to create concise, descriptive titles from the first user message in each chat session.

**retrieval.py** provides hybrid retrieval functionality combining dense vector similarity search with sparse keyword matching. `bm25_search()` implements the BM25 algorithm for term-frequency-based retrieval (particularly effective for acronyms and exact phrases), `reciprocal_rank_fusion()` merges ranked results from semantic and BM25 searches with configurable weights, and `expand_query()` uses the LLM to generate alternative phrasings of the user's question to improve recall.

**vector.py** manages ChromaDB client initialization and vector storage operations. It encapsulates collection creation (one collection per workspace), document upsert with UUID-prefixed IDs enabling prefix-based deletion when documents are removed, and retrieval queries supporting both similarity search and metadata filtering.

**Data Persistence Layer:**

Lit Synth employs a dual-database strategy optimizing for different data access patterns:

**PostgreSQL** (via SQLModel ORM) stores structured relational data including user accounts (authentication credentials with bcrypt-hashed passwords), workspace metadata (names, ownership, timestamps), document records (filename, file path, page count, chunk count, upload timestamp, processing status), chat sessions (titles, creation/update timestamps, message counts), and message history (role, content, timestamp, citations stored as JSONB arrays). SQLModel combines SQLAlchemy's ORM capabilities with Pydantic validation, enabling type-safe database operations.

**ChromaDB** (Vector Database) stores high-dimensional embedding vectors (768 dimensions from nomic-embed-text-v1.5 model) enabling semantic similarity search. Each workspace corresponds to a ChromaDB collection, isolating documents by project. Within each collection, document chunks are stored as vectors with metadata including document ID, source filename, page number, and chunk text for citation retrieval. ChromaDB runs locally with persistent storage at `./data/chromadb`, ensuring privacy by avoiding external vector database services and eliminating ongoing costs.

**Component Interactions:**

User actions in the React frontend trigger API calls to FastAPI endpoints using the centralized `apiService`. For document uploads, the backend processes the PDF through the extraction and chunking pipeline, generates embeddings via HuggingFace transformers running locally, and stores vectors in ChromaDB while saving metadata to PostgreSQL in a transactional manner. For chat queries, the backend retrieves relevant chunks from ChromaDB using hybrid search, constructs a RAG prompt with context and citation instructions, invokes the Gemini API for response generation, parses citations from the LLM output, and returns the response with citation metadata to the frontend. The frontend displays the AI response with clickable citation cards showing source information, and both the user query and assistant response are persisted in PostgreSQL for chat history that can be reviewed later.

#### 3.5.3 Database Design

LitSynth's data persistence strategy employs a hybrid database architecture combining a relational database (PostgreSQL) for structured metadata and transactional consistency, with a vector database (ChromaDB) for high-dimensional similarity search capabilities. This dual-database approach separates concerns, allowing each system to be optimized for its specific access patterns.

**Relational Database Schema:**

Figure 3.7 presents the Entity-Relationship diagram for the relational database, illustrating the entities, attributes, and relationships that maintain system state and user data.

```
┌───────────────────────┐
│        User           │
├───────────────────────┤
│ PK: id (INTEGER)      │
│     email (VARCHAR)   │ UNIQUE
│     hashed_password   │
│     created_at        │
└───────────┬───────────┘
            │ 1
            │ owns
            │
            │ M
┌───────────┴───────────────────┐
│        Workspace              │
├───────────────────────────────┤
│ PK: workspace_id (VARCHAR)    │ UUID
│ FK: user_id → User.id         │
│     name (VARCHAR)            │
│     created_at (TIMESTAMP)    │
│     updated_at (TIMESTAMP)    │
└───────────┬─────┬─────────────┘
            │     │
         M  │     │ M
    ┌───────┘     └────────┐
    │                      │
    │ contains             │ contains
    │                      │
┌───┴───────────────┐  ┌───┴─────────────────┐
│    Document       │  │       Chat          │
├───────────────────┤  ├─────────────────────┤
│ PK: doc_id        │  │ PK: chat_id         │
│     (VARCHAR)     │  │     (VARCHAR) UUID  │
│ FK: workspace_id  │  │ FK: workspace_id    │
│     → Workspace   │  │     → Workspace     │
│     filename      │  │     title (VARCHAR) │
│     file_path     │  │     created_at      │
│     pages (INT)   │  │     updated_at      │
│     chunks (INT)  │  │     message_count   │
│     status        │  └──────┬──────────────┘
│     (ENUM)        │         │
│     upload_date   │         │ 1
└───────────────────┘         │
                              │ has
                              │
                              │ M
                     ┌────────┴────────────────┐
                     │    ChatMessage          │
                     ├─────────────────────────┤
                     │ PK: id (INTEGER)        │
                     │ FK: chat_id → Chat      │
                     │     role (ENUM)         │
                     │       'user'/'assistant'│
                     │     content (TEXT)      │
                     │     timestamp           │
                     │     sources (JSONB)     │
                     │     (nullable)          │
                     └─────────────────────────┘
```
**Figure 3.7: Entity-Relationship Diagram for LitSynth**

The schema comprises five primary entities with defined relationships and constraints:

**1. User Entity**: Stores user account information. The `email` attribute enforces uniqueness via database constraint to prevent duplicate accounts. Passwords are hashed using the bcrypt algorithm before storage, with a computational cost factor of 12 rounds to resist brute-force attacks. The `id` serves as the primary key and foreign key reference for owned workspaces. The `created_at` timestamp records account creation for audit purposes.

**2. Workspace Entity**: Represents project-specific document collections. Each workspace is owned by exactly one user, enforced by the `user_id` foreign key with cascading deletion (when a user is deleted, all their workspaces are removed). The `workspace_id` uses UUID format for global uniqueness and security (non-sequential IDs prevent enumeration attacks). The `name` attribute allows users to organize research by topic (e.g., "Machine Learning Literature", "Blockchain Security Research"). Timestamps track creation and last modification dates for sorting and activity indicators. The `updated_at` field is automatically refreshed when documents are uploaded or chats are created.

**3. Document Entity**: Stores metadata about uploaded PDFs without storing the actual file content in the database (files are saved to the filesystem). The `workspace_id` foreign key establishes the one-to-many relationship with Workspace, enforced with cascading deletion. `file_path` stores the local filesystem path to the uploaded PDF (e.g., `./data/documents/<workspace_id>/<doc_id>.pdf`) for retrieval when serving files. `pages` and `chunks` record the document length and number of generated text chunks respectively, providing processing statistics to users. The `status` field is an ENUM type tracking processing state: "pending" (uploaded, awaiting processing), "processing" (currently extracting text and generating embeddings), "completed" (ready for chat queries), or "failed" (error occurred during processing). This status enables the UI to show appropriate feedback and retry options.

**4. Chat Entity**: Represents conversation sessions within a workspace. Multiple chats can exist per workspace to organize different research questions or topics (e.g., "Methodology Questions", "Results Analysis"). The `chat_id` uses UUID format for uniqueness. The `title` is auto-generated from the first user message using the LLM, truncated to a maximum of 50 characters for display consistency. `message_count` denormalizes the count of messages in the chat, updated via database triggers or application logic, enabling efficient sorting and display without JOIN queries. Timestamps track conversation creation and last activity.

**5. ChatMessage Entity**: Stores individual messages in chat history, forming a chronological conversation thread. The `chat_id` foreign key links messages to their parent chat session with cascading deletion (deleting a chat removes all its messages). The `role` ENUM differentiates between "user" queries and "assistant" responses, enabling alternating display in the chat interface. `content` stores the message text with TEXT type supporting unlimited length for long AI responses. The `timestamp` provides message ordering and display formatting. The `sources` field is a PostgreSQL JSONB column storing an array of citation objects with structure: `[{source: string, page: number, snippet: string}, ...]`. This field is nullable (only populated for assistant messages that include references) and supports JSON querying for citation analysis.

**Relationships and Constraints:**

- **User → Workspace (1:M with CASCADE DELETE)**: Deleting a user removes all their workspaces, documents, and chats through cascading foreign key constraints, ensuring data consistency and preventing orphaned records.
- **Workspace → Document (1:M with CASCADE DELETE)**: Deleting a workspace removes associated documents. The application also deletes corresponding ChromaDB vectors and filesystem PDF files.
- **Workspace → Chat (1:M with CASCADE DELETE)**: Deleting a workspace removes chat sessions and message history.
- **Chat → ChatMessage (1:M with CASCADE DELETE)**: Deleting a chat removes all messages in that conversation.

**Indexes** are created on foreign key columns (`user_id`, `workspace_id`, `chat_id`) and frequently queried fields (`email` on User, `status` on Document) to optimize query performance.

**Vector Database (ChromaDB):**

Separate from the relational schema, ChromaDB maintains vector embeddings for semantic search. Each workspace corresponds to a ChromaDB "collection" named using the `workspace_id`. Within each collection, document chunks are stored as high-dimensional vectors with associated metadata:

- **id**: Format `{doc_id}#{uuid}` allowing prefix-based deletion when documents are removed (e.g., deleting doc_123 removes all chunks with IDs starting with "doc_123#").
- **embedding**: 768-dimensional float vector from the nomic-embed-text-v1.5 model, representing the semantic meaning of the chunk text. Vectors enable cosine similarity search for finding semantically related content.
- **metadata**: JSON object containing:
  - `doc_id`: Links vector back to Document entity in PostgreSQL
  - `source`: Filename of the original PDF for citation display
  - `page`: Page number where the chunk originated (integer)
  - `text`: The original chunk text (700 characters) for displaying snippets and full context
- **document** (ChromaDB terminology): The chunk text content, stored separately for full-text retrieval and keyword matching (used by BM25 search).

**Hybrid Retrieval Process:**

During chat queries, the system performs two parallel searches:
1. **Dense Vector Search**: Computes cosine similarity between the query embedding and all chunk embeddings in the workspace collection, ranking by similarity score (0-1 range, where 1 is identical).
2. **BM25 Sparse Search**: Ranks chunks by term frequency-inverse document frequency, favoring exact keyword matches.

Results from both methods are merged using Reciprocal Rank Fusion with weights (0.6 semantic, 0.4 keyword), balancing semantic understanding with exact term matching.

**Data Flow Integration:**

When a document is uploaded, the backend performs atomic operations:
1. Save PDF file to filesystem at `./data/documents/<workspace_id>/<doc_id>.pdf`
2. Insert document metadata to PostgreSQL `documents` table with status "processing"
3. Extract text, chunk, and generate embeddings
4. Store embeddings in ChromaDB collection for the workspace
5. Update document status to "completed" in PostgreSQL

When a chat query arrives:
1. Retrieve relevant chunks from ChromaDB using hybrid search
2. Generate LLM response with citations
3. Insert user message and assistant response to PostgreSQL `chat_messages` table
4. Update chat `updated_at` timestamp and increment `message_count`

This architecture ensures data consistency across both databases while leveraging each system's strengths: PostgreSQL for transactional integrity and relational queries, ChromaDB for high-performance similarity search over high-dimensional vectors.

---

### 3.6 Summary

This chapter presented the methodology employed in developing LitSynth, an intelligent academic research assistant leveraging Retrieval-Augmented Generation (RAG) technology for analyzing uploaded research papers.

The chapter began by outlining the systematic project workflow spanning from initial problem identification through literature review, system design, implementation, and testing phases, culminating in documentation and defense preparation. The Iterative Incremental development model was selected as the appropriate software development life cycle due to the experimental nature of RAG-based systems, the need for continuous refinement based on user feedback and retrieval quality testing, and the component-based architecture separating frontend, backend, and data layers. This model enabled development in focused increments: core RAG functionality, multi-workspace support, enhanced hybrid retrieval, and advanced features including OCR and batch upload.

Requirements analysis commenced with a detailed description of the traditional manual approach to academic paper analysis, identifying key limitations including time inefficiency (5-10 hours per week spent searching PDFs), limited human recall of previously read papers, absence of semantic search capabilities, scalability issues beyond 20-30 papers, and lack of citation traceability. These limitations established the motivation for an automated, intelligent solution.

Requirements elicitation employed a multi-method approach combining structured interviews with 15 stakeholders (postgraduate students, undergraduates, and faculty from Bayero University Kano), an online survey distributed to 50 potential users achieving 78% response rate, and comparative analysis of existing research management tools. Key findings revealed critical user needs: natural language querying across multiple documents simultaneously, automatic citation generation with page numbers for academic verification, workspace organization by project or topic, OCR support for scanned PDFs, and cost-effective solutions accessible to students. Survey results quantified pain points: 87% of respondents spend 5+ hours weekly searching PDFs, 73% struggle synthesizing across more than 5 papers, 68% are frustrated by keyword-only search limitations, and 91% desire automatic citations.

Based on elicitation findings, ten functional requirements (FR1-FR10) were defined encompassing workspace management, PDF upload with OCR, natural language chat interface, semantic search retrieval, AI-generated responses with citations, chat history, user authentication, document status tracking, deletion capabilities, and dashboard management. Ten non-functional requirements (NFR1-NFR10) established quality attributes: performance targets (30 seconds for 50-page PDF processing, 5-second chat responses), accuracy thresholds (0.7+ cosine similarity for relevance), scalability capacity (100 documents per workspace, 50 concurrent users), security mechanisms (JWT authentication, bcrypt password hashing), privacy guarantees (local processing without external document transmission), usability goals (intuitive interface requiring no training), reliability standards (99% uptime), maintainability through architectural separation of concerns, and compatibility across modern browsers with responsive design.

Requirement analysis employed use case modeling to visualize system interactions and define operational scenarios. The use case diagram (Figure 3.3) identified primary actors (users and automated system processes) and core use cases including registration/login, workspace management, document upload and processing, chat-based querying, and data management. Detailed use case descriptions were provided in tabular format for four high-priority scenarios: Upload PDF Documents (detailing the extraction-chunking-vectorization pipeline with OCR fallback), Ask Question (describing the hybrid retrieval-RAG-citation workflow), Register/Login (covering authentication and token generation), and Create Workspace (outlining workspace initialization and collection creation). Each use case description specified preconditions, normal course steps, alternative courses for error handling, post-conditions, and exceptions.

System design employed behavioral and structural diagrams to document the proposed architecture. The activity diagram (Figure 3.4) illustrated the document processing workflow from PDF upload through text extraction (with conditional OCR for scanned documents), semantic chunking using RecursiveCharacterTextSplitter (700 characters, 100 overlap), embedding generation via nomic-embed-text-v1.5 (768 dimensions), vector storage in ChromaDB, and metadata persistence in PostgreSQL. The sequence diagram (Figure 3.5) detailed the chat interaction workflow showing component interactions: user query submission, JWT authentication, query embedding generation, hybrid search combining dense vector similarity and BM25 keyword matching via Reciprocal Rank Fusion, context retrieval, RAG prompt construction, Gemini API invocation, citation parsing, and response display with verifiable sources.

The package diagram (Figure 3.6) presented the three-tier architecture comprising: (1) Frontend Layer built with React 18, TypeScript, and Zustand state management, organized into page components, reusable UI elements, and service modules for API communication and export functionality; (2) Backend Layer implemented in FastAPI with modular organization including API endpoints for authentication/workspaces/documents/chat, business logic modules for PDF processing, RAG orchestration, hybrid retrieval, and vector operations, plus external integrations with Google Gemini LLM, Google Vision OCR, and HuggingFace embeddings; (3) Data Persistence Layer employing a dual-database strategy with PostgreSQL for structured relational data and ChromaDB for vector embeddings, enabling semantic similarity search while maintaining transaction consistency.

Database design employed an Entity-Relationship diagram (Figure 3.7) illustrating the relational schema with five entities and their relationships: User (authentication credentials with bcrypt hashing), Workspace (project collections with UUID identifiers), Document (PDF metadata with processing status tracking), Chat (conversation sessions with auto-generated titles), and ChatMessage (message content with JSONB citations). Relationships enforce referential integrity with cascading deletions ensuring cleanup: User → Workspace → {Document, Chat} → ChatMessage. The vector database design specified ChromaDB collection structure with 768-dimensional embeddings, metadata for citations (filename, page number, chunk text), and UUID-prefixed IDs enabling efficient document deletion. The hybrid retrieval process combining dense vector search (cosine similarity) and sparse keyword matching (BM25) with Reciprocal Rank Fusion was explained, along with data flow integration ensuring atomic operations across both databases during document upload and chat queries.

The methodology established in this chapter provided the systematic foundation for implementing LitSynth through well-defined requirements, architectural design patterns, and database schemas. The iterative development approach enabled continuous refinement of retrieval quality and user experience, while the comprehensive requirements analysis ensured alignment with actual user needs identified through rigorous elicitation methods. The architectural designs documented in this chapter guided the implementation phase, which is detailed in the subsequent chapter on system implementation and testing.

---

