# SmartDoc AI — Frontend

A plain HTML/CSS/JS frontend for the SmartDoc AI RAG assistant: file upload,
chat interface, and source citations. No build step, no dependencies.

## Files
- `index.html` — page structure (sign-in screen + app shell)
- `style.css` — the "card catalog" design system (all colors/fonts as CSS variables at the top of the file)
- `app.js` — all interactivity: sign-in, upload, chat, citations

## Run it
Just open `index.html` in a browser, or serve the folder:

```bash
cd smartdoc-ai
python -m http.server 5500
# then open http://localhost:5500
```

## Right now it's running on mock data
Everything that should eventually talk to your FastAPI backend is isolated
at the top of `app.js` in the `API` object:

```js
const API = {
  async uploadDocument(file) { ... },   // currently fakes an upload + delay
  async askQuestion(question, docs) { ... } // currently fakes a RAG answer
};
```

### To connect your real backend
Replace the body of each method. For example:

```js
async uploadDocument(file) {
  const formData = new FormData();
  formData.append("file", file);
  const res = await fetch("http://localhost:8000/api/upload", {
    method: "POST",
    body: formData,
  });
  if (!res.ok) throw new Error("Upload failed");
  return await res.json(); // expects { id, name, pages, status }
}

async askQuestion(question, docs) {
  const res = await fetch("http://localhost:8000/api/query", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      question,
      doc_ids: docs.map((d) => d.id),
    }),
  });
  if (!res.ok) throw new Error("Query failed");
  return await res.json(); // expects { answer, citations: [{ doc, page, excerpt }] }
}
```

Nothing else in the file needs to change — the UI (upload cards, chat
bubbles, citation tabs) reads whatever shape comes back from these two
functions, as long as it matches the shapes noted above.

### Auth
The sign-in screen is fully mocked (no password, no server check) since
your spec listed authentication as optional. It just captures a display
name for the header. Swap `signinForm`'s submit handler in `app.js` for a
real login call whenever you're ready, or delete the overlay entirely and
call `enterApp("Guest")` on load if you decide to skip auth altogether.

## Notes for your FastAPI/CORS setup
If your backend runs on a different port than the frontend (likely, during
development), add CORS middleware in FastAPI:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten this before deploying
    allow_methods=["*"],
    allow_headers=["*"],
)
```
