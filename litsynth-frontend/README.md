# LitSynth Frontend

A modern React-based frontend for LitSynth - an intelligent academic research assistant.

## Features

- **Authentication**: Secure token-based authentication
- **Workspace Management**: Create, view, and delete research workspaces
- **Document Upload**: Upload PDF research papers to workspaces
- **Intelligent Chat**: Chat with AI about your research documents with source citations
- **Chat History Management**: Delete individual messages or clear entire chat history
- **User Profile**: View API information and manage access tokens

## Tech Stack

- **React 18** - UI library
- **TypeScript** - Type-safe code
- **Vite** - Fast build tool and dev server
- **TailwindCSS** - Utility-first CSS framework
- **React Router** - Client-side routing
- **React Query** - Data fetching and state management
- **Zustand** - Lightweight state management
- **Axios** - HTTP client
- **Lucide React** - Icon library
- **React Markdown** - Markdown rendering for chat messages

## Prerequisites

Before you begin, ensure you have the following installed:

- **Node.js** (v18 or higher) - [Download here](https://nodejs.org/)
- **npm** (comes with Node.js) or **yarn**

To check if Node.js is installed:
```bash
node --version
npm --version
```

## Installation

1. **Navigate to the frontend directory:**
```bash
cd /Users/Work/Documents/Final-Year-Project/litsynth-frontend
```

2. **Install dependencies:**
```bash
npm install
```

This will install all required packages listed in `package.json`.

## Configuration

The frontend is configured to connect to the backend API at `http://localhost:8000`.

If your backend runs on a different host or port, update the `API_BASE_URL` in [src/services/api.ts](src/services/api.ts#L12):

```typescript
const API_BASE_URL = 'http://localhost:8000';
```

## Running the Development Server

1. **Start the backend server first** (in a separate terminal):
```bash
cd /Users/Work/Documents/Final-Year-Project/litsynth-backend/src
source ../venv/bin/activate
python -m uvicorn main:app --port 8000 --reload
```

2. **Start the frontend development server:**
```bash
npm run dev
```

The application will be available at: **http://localhost:3000**

## Building for Production

To create an optimized production build:

```bash
npm run build
```

The built files will be in the `dist/` directory.

To preview the production build locally:

```bash
npm run preview
```

## Project Structure

```
litsynth-frontend/
├── public/                 # Static assets
├── src/
│   ├── components/        # Reusable UI components
│   │   ├── Layout.tsx
│   │   ├── LoadingSpinner.tsx
│   │   └── Modal.tsx
│   ├── pages/             # Page components
│   │   ├── LoginPage.tsx
│   │   ├── DashboardPage.tsx
│   │   ├── ChatPage.tsx
│   │   └── ProfilePage.tsx
│   ├── services/          # API service layer
│   │   └── api.ts
│   ├── store/             # State management
│   │   └── authStore.ts
│   ├── types/             # TypeScript type definitions
│   │   └── index.ts
│   ├── App.tsx            # Main app component with routing
│   ├── main.tsx           # Application entry point
│   └── index.css          # Global styles
├── index.html             # HTML entry point
├── package.json           # Dependencies and scripts
├── tsconfig.json          # TypeScript configuration
├── vite.config.ts         # Vite configuration
├── tailwind.config.js     # TailwindCSS configuration
└── postcss.config.js      # PostCSS configuration
```

## Usage

### 1. Login

- Open the application at `http://localhost:3000`
- Enter your access token (e.g., `Dxqj7Oc1Lj9JWlLI0mNiAh4IRMRUmu1r`)
- Click "Sign In"

### 2. Create a Workspace

- Click "New Workspace" button on the dashboard
- Enter workspace name, token name, and description
- Click "Create Workspace"

### 3. Upload Documents

- Open a workspace by clicking "Open Chat"
- Click "Upload PDF" in the left sidebar
- Select a PDF research paper
- Wait for the upload to complete

### 4. Chat with Your Documents

- Type your question in the chat input
- Press Enter or click the Send button
- View the AI response with source citations
- Delete individual messages using the X button that appears on hover
- Clear entire chat history using "Clear Chat" button

### 5. Manage Workspaces

- View all workspaces on the dashboard
- Delete workspaces by clicking the trash icon (appears on hover)
- Navigate between workspaces

### 6. Profile Settings

- Click "Profile" in the navigation bar
- View and copy your access token
- See API information and system details

## API Integration

The frontend communicates with the backend through the API service layer ([src/services/api.ts](src/services/api.ts)).

### Main API Endpoints:

- `GET /workspaces` - List all workspaces
- `POST /workspaces` - Create a new workspace
- `DELETE /workspaces/{id}` - Delete a workspace
- `GET /workspaces/{id}/documents` - List documents in a workspace
- `POST /workspaces/{id}/upload` - Upload a PDF document
- `DELETE /workspaces/{id}/documents/{filename}` - Delete a document
- `POST /workspaces/{id}/chat` - Send a chat message

## Development

### Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

### Code Style

This project uses:
- **ESLint** for code linting
- **TypeScript** for type checking
- **Prettier** (recommended) for code formatting

## Troubleshooting

### Port Already in Use

If port 3000 is already in use, Vite will automatically try the next available port (3001, 3002, etc.).

To specify a different port, modify [vite.config.ts](vite.config.ts):

```typescript
server: {
  port: 3001, // Change to your preferred port
}
```

### CORS Errors

If you encounter CORS errors, ensure the backend has proper CORS configuration in [main.py](../litsynth-backend/src/main.py).

### Backend Connection Issues

1. Verify the backend is running on `http://localhost:8000`
2. Check the API URL in [src/services/api.ts](src/services/api.ts)
3. Ensure your access token is valid

### Build Errors

If you encounter build errors:

1. Clear node_modules and reinstall:
```bash
rm -rf node_modules package-lock.json
npm install
```

2. Clear Vite cache:
```bash
rm -rf node_modules/.vite
```

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## License

Part of the LitSynth Final Year Project.

## Contributing

This is a final year project. For questions or issues, contact the project maintainer.
