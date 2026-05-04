# AI Text Classifier — React Frontend

Chat UI for the AI Text Classifier + RAG Agent backend.

## Setup

```bash
cd frontend
npm install
```

## Configure API URL

```bash
cp .env.example .env.local
# Edit .env.local and set VITE_API_URL to your backend URL
```

Default: `http://localhost:8000`

## Run (development)

```bash
npm run dev
```

Opens at <http://localhost:5173>

## Build (production)

```bash
npm run build
npm run preview
```

## Features

- **Chat Window** — full conversation history, auto-scroll, typing effect on assistant replies
- **Input Box** — submit with Enter or Send button, disabled while loading
- **File Upload** — drag-and-drop or click, accepts `.pdf` and `.txt`, success/error toast
- **Documents Sidebar** — live list of uploaded documents, refreshes after each upload

## Design

- Tailwind CSS only (no component library)
- Responsive from 375px (mobile) to 1440px (desktop)
- No authentication or session management
