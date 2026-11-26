# Diagram Creation Guide for Chapter 3

This guide provides instructions for converting the ASCII diagrams in Chapter 3 into professional visual diagrams suitable for thesis submission.

## Required Diagrams (7 total)

### Figure 3.1: Project Workflow
**Type**: Linear Process Flow Diagram
**Tool Recommendation**: draw.io, Lucidchart, or PowerPoint

**Elements**:
- 6 rectangular boxes arranged horizontally
- Arrows connecting them left to right
- Labels: Introduction → Literature Review → Analysis and Design → Implementation and Testing → Writeup → Defense Slides

**Styling**:
- Box fill: Light blue (#E3F2FD)
- Border: Dark blue (#1976D2), 2pt
- Arrow style: Solid line with arrowhead
- Font: Arial or Times New Roman, 11pt
- Dimensions: Approx. 15cm wide × 3cm tall

**Location in document**: After line 11 in Chapter3_Methodology.md

---

### Figure 3.2: Iterative Incremental Development Model
**Type**: Circular Process Diagram with Increments List
**Tool Recommendation**: draw.io or Lucidchart

**Elements**:
**Part A - Circular Process**:
- 5 boxes arranged in circular pattern
- Labels: Planning → Design → Implementation → Testing → Evaluation
- Evaluation has arrow back to Planning (showing iteration)
- Arrow pointing down to "Next Increment or Release"

**Part B - Increments List** (below the circular diagram):
- 4 numbered increment boxes
- Increment 1: Core RAG System (bullet points)
- Increment 2: Multi-Workspace Support (bullet points)
- Increment 3: Enhanced Retrieval (bullet points)
- Increment 4: Advanced Features (bullet points)

**Styling**:
- Process boxes: Light green (#E8F5E9), border green (#388E3C)
- Increment boxes: Light orange (#FFF3E0), border orange (#F57C00)
- Font: Arial, 10pt
- Dimensions: 12cm wide × 15cm tall total

**Location**: After line 39 in Chapter3_Methodology.md

---

### Figure 3.3: Use Case Diagram for LitSynth
**Type**: UML Use Case Diagram
**Tool Recommendation**: draw.io (has UML shapes), Lucidchart, Visual Paradigm, or PlantUML

**Elements**:
- **Actor**: Stick figure labeled "User (Researcher/Student)" on left
- **System boundary**: Large rectangle labeled "LitSynth System" at top
- **Use cases**: 11 oval shapes inside system boundary:
  1. Register/Login
  2. Create Workspace
  3. Upload PDF
  4. Process Document (with note: System - Automated)
  5. Ask Question (Chat)
  6. Retrieve Context (with note: System)
  7. Generate Response (with note: System - Gemini API)
  8. View Chat History
  9. View Documents
  10. Delete Document
  11. Delete Chat
  12. Logout

**Relationships**:
- Actor connects to: Register/Login, Create Workspace, Upload PDF, Ask Question, View Chat History, View Documents, Delete Document, Delete Chat, Logout
- Upload PDF «include» Process Document
- Ask Question «include» Retrieve Context
- Retrieve Context «include» Generate Response

**Styling**:
- System boundary: Light gray rectangle
- Use cases: White ovals with black border
- Actor: Black stick figure
- Include relationships: Dashed arrows with «include» label
- Associations: Solid lines
- Font: Arial, 10pt
- Dimensions: 14cm wide × 18cm tall

**Location**: After line 259 in Chapter3_Methodology.md

---

### Figure 3.4: Activity Diagram - PDF Upload and Processing
**Type**: UML Activity Diagram (Flowchart)
**Tool Recommendation**: draw.io, Lucidchart, or Visual Paradigm

**Elements**:
- **Start node**: Filled black circle
- **Action boxes**: Rounded rectangles
- **Decision diamonds**: Diamond shapes
- **End node**: Circle with filled black circle inside

**Flow** (top to bottom):
1. START
2. User selects PDF file(s)
3. Decision: Valid PDF format? Size < 50MB?
   - NO → Display error message → END
   - YES → Continue
4. Upload file to backend server
5. Extract text from PDF (PyMuPDF)
6. Decision: Text extracted successfully?
   - NO → Apply OCR (Google Vision) → Receive OCR extracted text → Continue
   - YES → Continue
7. Split text into chunks (RecursiveCharacterTextSplitter: 700 chars, 100 overlap)
8. For each chunk: Generate embedding (nomic-embed-text-v1.5, 768 dims), Store in ChromaDB
9. Save document record to PostgreSQL
10. Display success notification
11. END

**Styling**:
- Start/End: Black filled circles
- Actions: Light blue rounded rectangles (#BBDEFB)
- Decisions: Yellow diamonds (#FFF9C4)
- OCR branch: Light red actions (#FFCDD2) to distinguish
- Arrows: Black solid lines with arrowheads
- Font: Arial, 9pt
- Dimensions: 12cm wide × 25cm tall

**Location**: After line 416 in Chapter3_Methodology.md

---

### Figure 3.5: Sequence Diagram - Chat Interaction
**Type**: UML Sequence Diagram
**Tool Recommendation**: draw.io, PlantUML, or Visual Paradigm

**Participants** (vertical lifelines, left to right):
1. User
2. Frontend
3. Backend
4. Embeddings Model
5. ChromaDB
6. Gemini API
7. PostgreSQL

**Interactions** (arrows between lifelines):
1. User → Frontend: Enter question and click Send
2. Frontend → Backend: POST /chat {query, chat_id, workspace}
3. Backend → Backend: Validate JWT token
4. Backend → Embeddings Model: Generate query embedding
5. Embeddings Model → Backend: 768-dim vector
6. Backend → ChromaDB: Hybrid search (vector + BM25)
7. ChromaDB → Backend: Top 4 chunks with metadata
8. Backend → Backend: Construct RAG prompt with context
9. Backend → Gemini API: Send prompt for completion
10. Gemini API → Backend: Generated response with citations
11. Backend → Backend: Parse citations from response
12. Backend → PostgreSQL: Save user msg + AI response
13. PostgreSQL → Backend: Saved (confirmation)
14. Backend → Frontend: Return {response, citations}
15. Frontend → User: Display AI answer with citation boxes

**Styling**:
- Lifelines: Vertical dashed lines
- Participants: Rectangles at top with labels
- Activation boxes: Thin rectangles on lifelines during processing
- Messages: Solid arrows with labels above
- Return messages: Dashed arrows
- Font: Arial, 8pt
- Dimensions: 18cm wide × 22cm tall

**Location**: After line 513 in Chapter3_Methodology.md

---

### Figure 3.6: System Architecture - Package Diagram
**Type**: UML Package Diagram (Component Architecture)
**Tool Recommendation**: draw.io or Lucidchart

**Structure** (3-tier architecture):

**Frontend Layer** (top large box):
- Main box labeled "FRONTEND LAYER (React)"
- Contains 3 nested sub-boxes:
  1. COMPONENTS (list of components)
  2. STATE MANAGEMENT (Zustand) (authStore, themeStore)
  3. SERVICES (apiService, exportService)

**Backend Layer** (middle large box):
- Main box labeled "BACKEND LAYER (FastAPI - Python)"
- Contains 3 nested sub-boxes:
  1. API ENDPOINTS (list of endpoints by category)
  2. BUSINESS LOGIC (processors.py, chat.py, retrieval.py, vector.py)
  3. EXTERNAL INTEGRATIONS (Gemini API, Vision API, HuggingFace)

**Data Layer** (bottom, 2 boxes side by side):
- Left box: "DATA LAYER (PostgreSQL/SQLModel)"
  - Contains: Tables list (users, workspaces, documents, chats, chat_messages)
- Right box: "VECTOR DATABASE (ChromaDB)"
  - Contains: Collections description, Search Operations, Persistence

**Connections**:
- Frontend → Backend: Arrow labeled "HTTP/REST API (JWT Authentication)"
- Backend → Data Layer: Two arrows (one to PostgreSQL, one to ChromaDB)

**Styling**:
- Layer boxes: Outer borders with shadows
- Frontend: Light blue background (#E3F2FD)
- Backend: Light green background (#E8F5E9)
- Data layers: Light yellow background (#FFF9C4)
- Nested boxes: White background with gray borders
- Font: Arial, 9pt
- Dimensions: 18cm wide × 24cm tall

**Location**: After line 581 in Chapter3_Methodology.md

---

### Figure 3.7: Entity-Relationship Diagram for LitSynth
**Type**: ER Diagram (Crow's Foot Notation)
**Tool Recommendation**: draw.io, Lucidchart, MySQL Workbench, or ERDPlus

**Entities** (5 rectangles with attributes):

1. **User**
   - PK: id (INTEGER)
   - email (VARCHAR) UNIQUE
   - hashed_password
   - created_at

2. **Workspace**
   - PK: workspace_id (VARCHAR) UUID
   - FK: user_id → User.id
   - name (VARCHAR)
   - created_at (TIMESTAMP)
   - updated_at (TIMESTAMP)

3. **Document**
   - PK: doc_id (VARCHAR)
   - FK: workspace_id → Workspace
   - filename
   - file_path
   - pages (INT)
   - chunks (INT)
   - status (ENUM)
   - upload_date

4. **Chat**
   - PK: chat_id (VARCHAR) UUID
   - FK: workspace_id → Workspace
   - title (VARCHAR)
   - created_at
   - updated_at
   - message_count

5. **ChatMessage**
   - PK: id (INTEGER)
   - FK: chat_id → Chat
   - role (ENUM) 'user'/'assistant'
   - content (TEXT)
   - timestamp
   - sources (JSONB) nullable

**Relationships** (Crow's Foot Notation):
- User (1) ────< Workspace (M): One user owns many workspaces
- Workspace (1) ────< Document (M): One workspace contains many documents
- Workspace (1) ────< Chat (M): One workspace has many chats
- Chat (1) ────< ChatMessage (M): One chat has many messages

**Annotations**:
- Add "CASCADE DELETE" labels on relationship lines
- Mark PK and FK columns clearly

**Styling**:
- Entity boxes: Light blue (#E3F2FD) with blue borders
- Primary keys: Bold text with key icon
- Foreign keys: Italic text with arrow symbol
- Relationship lines: Crow's foot notation (one-to-many)
- Font: Arial, 9pt
- Dimensions: 16cm wide × 20cm tall

**Location**: After line 780 in Chapter3_Methodology.md

---

## General Diagram Guidelines

### For All Diagrams:

1. **File Format**:
   - Save as high-resolution PNG (300 DPI minimum) for thesis submission
   - Also save editable source file (e.g., .drawio, .vsdx) for future edits

2. **Color Scheme**:
   - Use professional, muted colors (avoid bright neon)
   - Ensure sufficient contrast for black/white printing
   - Recommended palette: Blues (#E3F2FD to #1976D2), Greens (#E8F5E9 to #388E3C)

3. **Font**:
   - Use Times New Roman (matches thesis body text) or Arial
   - Minimum font size: 9pt (must be readable when printed)
   - Consistent font across all diagrams

4. **Labeling**:
   - Every diagram must have a figure number (Figure 3.X)
   - Include descriptive caption below diagram
   - Caption format: "**Figure 3.X**: [Description]"

5. **Sizing**:
   - Diagrams should fit within thesis page margins
   - Maximum width: 15cm (for portrait A4 page with margins)
   - If larger needed, consider landscape orientation for that page

6. **Alignment**:
   - Center diagrams horizontally on page
   - Leave adequate white space around diagrams

7. **Consistency**:
   - Use same arrow styles across all diagrams
   - Use same color scheme for similar elements (e.g., all decision diamonds same color)
   - Maintain consistent border thickness

### Tools Comparison:

| Tool | Best For | Free? | Learning Curve |
|------|----------|-------|----------------|
| **draw.io** | All diagram types | Yes | Low-Medium |
| **Lucidchart** | Professional polish | Free tier limited | Low |
| **PlantUML** | UML diagrams from code | Yes | Medium |
| **Visual Paradigm** | Complex UML | Free community edition | Medium-High |
| **PowerPoint** | Simple flowcharts | Requires MS Office | Low |

**Recommendation**: Start with draw.io (free, web-based, good for all types). Export as PNG at 300 DPI.

---

## Workflow for Creating Diagrams:

1. **Read the ASCII diagram** in Chapter3_Methodology.md to understand structure
2. **Read the supporting text** (paragraphs after each diagram) for context
3. **Open your chosen tool** (e.g., draw.io at app.diagrams.net)
4. **Create the diagram** following the specifications above
5. **Export as PNG** (300 DPI, high quality)
6. **Save source file** (e.g., diagram_name.drawio) for future edits
7. **Insert into thesis document** replacing the ASCII representation
8. **Add caption** in format: **Figure 3.X**: [Description]

---

## Checklist Before Submission:

For each diagram, verify:
- [ ] Figure number is correct and sequential (3.1 through 3.7)
- [ ] Caption accurately describes the diagram
- [ ] All text is readable (not too small)
- [ ] Colors print well in grayscale (test print)
- [ ] Diagram is centered on page
- [ ] No spelling errors in labels
- [ ] Consistent styling with other diagrams
- [ ] High resolution (300 DPI PNG)
- [ ] Referenced correctly in text (e.g., "as shown in Figure 3.4")

---

## Alternative: Professional Diagram Service

If time is limited or professional quality is critical, consider hiring a technical illustrator from:
- Fiverr.com (search "UML diagram" or "technical diagram")
- Upwork.com
- Local design students

Provide them with:
1. The ASCII diagrams from Chapter3_Methodology.md
2. This guide
3. Your university's thesis formatting requirements

Typical cost: $10-30 per diagram, 24-48 hour turnaround.
