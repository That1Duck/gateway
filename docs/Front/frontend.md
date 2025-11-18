# Frontend Architecture Overview

This document provides a high-level technical overview of the `frontend` component of the project. It is intended for developers who will work on, extend, or maintain the codebase. The goal is to provide a clear understanding of the structure, responsibilities, and interaction patterns within the frontend system.

---

# 1. Technology Stack

The frontend is implemented using the following technologies:

* **Nuxt 3 (Vue 3 framework)** – core application runtime, routing, server-side rendering (optional), and project structure.
* **TypeScript** – static typing for improved maintainability and reliability.
* **Pinia** – state management (if needed; some components work without global state).
* **TailwindCSS** – utility-first CSS styling.
* **Shadcn/UI for Vue** – prebuilt UI components (Sidebar, Buttons, Cards, etc.).
* **Lucide Icons** – icon set.
* **Fetch API via `$fetch`** – communication with the backend.

The frontend communicates with the backend (`gateway`) through HTTP/JSON REST API endpoints.

---

# 2. Project Structure

The structure follows standard Nuxt 3 conventions:

```
frontend/
│
├── components/          # Reusable UI components
│   ├── UploadDropzone.vue
│   ├── DocumentList.vue
│   └── ...
│
├── composables/         # Shared composable functions (logic reuse)
│   └── useUploader.ts   # Upload logic, progress tracking, polling
│
├── pages/               # Application pages rendered by Nuxt
│   └── documents.vue    # Main page for document uploads and status
│
├── assets/              # Global styles, images, fonts
├── public/              # Static assets served directly
├── app.vue              # Root component
├── nuxt.config.ts       # Global configuration
└── package.json
```

Each folder has specific responsibilities:

* **components/** contains purely UI-layer code.
* **composables/** contains business logic shared between components.
* **pages/** defines routes and composes UI + logic.

---

# 3. Core Functional Components

## 3.1 UploadDropzone.vue

Responsible for:

* File selection (input + drag-and-drop)
* Calling `useUploader()` to upload the file
* Emitting an event to the page when an upload finishes

Contains no business logic; delegates all network operations to composables.

## 3.2 DocumentList.vue

Responsible for:

* Rendering the list of uploaded documents
* Displaying statuses (`queued`, `processing`, `ready`, `failed`)
* Triggering explicit refresh of document information

This component only visualizes state provided by the page.

## 3.3 documents.vue

The main page responsible for:

* Integrating UploadDropzone and DocumentList
* Holding the list of documents in local component state
* Polling the backend for updated processing status

It uses `useUploader()` for polling and upsert logic.

---

# 4. Composables (Logic Layer)

## 4.1 useUploader.ts

This composable provides:

* Logic for uploading files via XMLHttpRequest to support progress events
* Reactive state: `isUploading`, `progress`, `error`
* Function `uploadFile()` for performing the upload
* Function `pollStatus()` for continuously querying the backend until the document reaches a terminal state
* Function `fetchDocument()` for retrieving updated document metadata

It abstracts away all interaction with the backend so components remain clean.

---

# 5. API Interaction

The frontend communicates with the backend via the configured API base:

```
apiBase = useRuntimeConfig().public.apiBase
```

Key endpoints used:

* `POST /api/v1/files/upload` – upload a new file
* `GET /api/v1/files/{id}` – retrieve document metadata and processing status

The application uses polling to detect when background processing (handled by Dramatiq worker) has completed.

---

# 6. UI Framework and Styling

The frontend uses:

* **TailwindCSS** for layout and styling
* **Shadcn/UI** components for consistent UI patterns
* **Lucide Icons** for icons

Components follow a structured and composable design, enabling straightforward extension.

---

# 7. How to Extend the Frontend

Developers can easily extend functionality by following these patterns:

### Adding New Pages

* Create a new `.vue` file under `pages/`
* Nuxt automatically registers it as a route

### Adding New Business Logic

* Create a new composable under `composables/`
* Use the naming convention `useXxx.ts`

### Adding New UI Components

* Place reusable elements under `components/`
* Keep components visually focused and move logic into composables

### Adding API Endpoints

* Add new backend route
* Create a corresponding composable or extend `useUploader()`

---

# 8. Summary

This frontend is structured around:

* Clean separation of presentation (components), business logic (composables), and routing (pages)
* Predictable data flow between page → composable → backend
* Modern Vue/Nuxt architecture designed for incremental extension

Developers can expand the system by adding pages, composables, or components without modifying the existing architecture.
