# LitSynth Quick Start Guide

## Prerequisites Check

First, verify that Node.js is installed on your system:

```bash
node --version
npm --version
```

If not installed, download and install Node.js from: https://nodejs.org/ (version 18 or higher)

## Installation & Setup

### Step 1: Navigate to the frontend directory

```bash
cd /Users/Work/Documents/Final-Year-Project/litsynth-frontend
```

### Step 2: Install dependencies

```bash
npm install
```

This will install all required packages. It may take a few minutes.

### Step 3: Start the backend server (in a separate terminal)

```bash
cd /Users/Work/Documents/Final-Year-Project/litsynth-backend/src
source ../venv/bin/activate
python -m uvicorn main:app --port 8000 --reload
```

### Step 4: Start the frontend development server

```bash
cd /Users/Work/Documents/Final-Year-Project/litsynth-frontend
npm run dev
```

### Step 5: Open the application

Open your browser and go to: **http://localhost:3000**

## First Time Usage

1. **Login**
   - Use the test token: `Dxqj7Oc1Lj9JWlLI0mNiAh4IRMRUmu1r`
   - Click "Sign In"

2. **Create a Workspace**
   - Click "New Workspace"
   - Fill in the form:
     - Name: "My Research Papers"
     - Token Name: "my_token"
     - Description: "Machine Learning research"
   - Click "Create Workspace"

3. **Upload Documents**
   - Click "Open Chat" on your workspace
   - Click "Upload PDF" in the left sidebar
   - Select a PDF file (you can use the provided test papers in the test-papers folder)
   - Wait for upload to complete

4. **Start Chatting**
   - Type a question like: "What are the main papers in this workspace?"
   - Press Enter or click Send
   - View the AI response with citations

## Test Papers

You can test with these academic papers:
- ALBERT paper (Lan et al., 2019)
- Attention Is All You Need (Vaswani et al., 2017)
- RoBERTa paper (Liu et al., 2019)

## Troubleshooting

### Port 3000 is already in use
Vite will automatically use the next available port (3001, 3002, etc.). Check the terminal output for the actual URL.

### Cannot connect to backend
Make sure the backend server is running on port 8000. Check the terminal where you started the backend.

### npm install fails
Try:
```bash
rm -rf node_modules package-lock.json
npm install
```

## Features to Explore

- ✅ Create multiple workspaces
- ✅ Upload multiple PDFs to each workspace
- ✅ Chat with AI about your documents
- ✅ View source citations
- ✅ Delete individual messages (hover over message)
- ✅ Clear entire chat history
- ✅ Delete documents
- ✅ Delete workspaces
- ✅ View your profile and API information

## Support

For issues or questions, refer to the main [README.md](README.md) file.
