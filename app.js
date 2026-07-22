/* =========================================================
   SmartDoc AI — frontend logic
   Everything that talks to a backend is isolated in the
   "API LAYER" section below. Right now it returns mock
   data with a simulated delay — swap the internals of
   uploadDocument() and askQuestion() for real fetch() calls
   to your FastAPI endpoints once they're ready.
   ========================================================= */

/* ---------------------------------------------------------
   API LAYER (mocked — replace with real calls later)
   --------------------------------------------------------- */
const API = {
  // TODO: replace with `await fetch('/api/upload', { method: 'POST', body: formData })`
  async uploadDocument(file) {
    await delay(600 + Math.random() * 500);
    return {
      id: crypto.randomUUID(),
      name: file.name,
      pages: Math.floor(Math.random() * 40) + 3,
      status: "indexed",
    };
  },

  // TODO: replace with `await fetch('/api/query', { method: 'POST', body: JSON.stringify({ question, doc_ids }) })`
  async askQuestion(question, docs) {
    await delay(900 + Math.random() * 700);

    if (docs.length === 0) {
      return {
        answer:
          "I don't have any documents to search yet. Upload a PDF, DOCX, or TXT file in the Card Catalog on the left, and I'll ground my answers in it.",
        citations: [],
      };
    }

    // Mocked answer + citations, shaped like what the real RAG
    // pipeline (LangChain + ChromaDB) will eventually return.
    const sourceDoc = docs[Math.floor(Math.random() * docs.length)];
    return {
      answer: `Based on "${sourceDoc.name}", here's a grounded answer to "${question}" — this is placeholder text standing in for the real retrieval-augmented response your FastAPI backend will generate once it's connected.`,
      citations: [
        {
          doc: sourceDoc.name,
          page: Math.floor(Math.random() * sourceDoc.pages) + 1,
          excerpt:
            "This is a stand-in excerpt showing where a real chunk of retrieved document text will appear once the vector database is wired up.",
        },
        docs.length > 1
          ? {
              doc: docs[(docs.indexOf(sourceDoc) + 1) % docs.length].name,
              page: Math.floor(Math.random() * 20) + 1,
              excerpt:
                "A second supporting excerpt, demonstrating multi-source citation coverage across your uploaded documents.",
            }
          : null,
      ].filter(Boolean),
    };
  },
};

function delay(ms) {
  return new Promise((res) => setTimeout(res, ms));
}

/* ---------------------------------------------------------
   STATE
   --------------------------------------------------------- */
const state = {
  user: null,
  documents: [], // { id, name, pages, status }
};

/* ---------------------------------------------------------
   SIGN-IN (optional / mocked — no real auth backend)
   --------------------------------------------------------- */
const signinOverlay = document.getElementById("signin-overlay");
const signinForm = document.getElementById("signin-form");
const signinNameInput = document.getElementById("signin-name");
const guestBtn = document.getElementById("guest-btn");
const appEl = document.getElementById("app");
const userChip = document.getElementById("user-chip");
const signoutBtn = document.getElementById("signout-btn");

function enterApp(name) {
  state.user = name || "Guest";
  userChip.textContent = state.user;
  signinOverlay.hidden = true;
  appEl.hidden = false;
  document.getElementById("chat-input").focus();
}

signinForm.addEventListener("submit", (e) => {
  e.preventDefault();
  enterApp(signinNameInput.value.trim());
});

guestBtn.addEventListener("click", () => enterApp("Guest"));

signoutBtn.addEventListener("click", () => {
  appEl.hidden = true;
  signinOverlay.hidden = false;
  signinNameInput.value = "";
});

/* ---------------------------------------------------------
   FILE UPLOAD / CARD CATALOG
   --------------------------------------------------------- */
const fileInput = document.getElementById("file-input");
const dropzone = document.getElementById("dropzone");
const catalogDrawer = document.getElementById("catalog-drawer");
const catalogEmpty = document.getElementById("catalog-empty");
const docCount = document.getElementById("doc-count");

fileInput.addEventListener("change", (e) => handleFiles(e.target.files));

["dragover", "dragenter"].forEach((evt) =>
  dropzone.addEventListener(evt, (e) => {
    e.preventDefault();
    dropzone.classList.add("dragover");
  })
);
["dragleave", "drop"].forEach((evt) =>
  dropzone.addEventListener(evt, (e) => {
    e.preventDefault();
    dropzone.classList.remove("dragover");
  })
);
dropzone.addEventListener("drop", (e) => handleFiles(e.dataTransfer.files));

async function handleFiles(fileList) {
  const files = Array.from(fileList || []);
  for (const file of files) {
    const placeholderId = `pending-${crypto.randomUUID()}`;
    renderPendingCard(placeholderId, file.name);
    try {
      const doc = await API.uploadDocument(file);
      state.documents.push(doc);
      replacePendingCard(placeholderId, doc);
    } catch (err) {
      removeCard(placeholderId);
      console.error("Upload failed:", err);
    }
    updateDocCount();
  }
}

function renderPendingCard(id, name) {
  catalogEmpty.style.display = "none";
  const card = document.createElement("div");
  card.className = "index-card";
  card.id = id;
  card.innerHTML = `
    <p class="doc-name">${escapeHtml(name)}</p>
    <p class="doc-meta"><span>indexing…</span><span>⏳</span></p>
  `;
  catalogDrawer.appendChild(card);
}

function replacePendingCard(id, doc) {
  const card = document.getElementById(id);
  if (!card) return;
  card.innerHTML = `
    <p class="doc-name">${escapeHtml(doc.name)}</p>
    <p class="doc-meta"><span class="doc-status">indexed · ${doc.pages}p</span><span>✓</span></p>
  `;
}

function removeCard(id) {
  const card = document.getElementById(id);
  if (card) card.remove();
}

function updateDocCount() {
  const n = state.documents.length;
  docCount.textContent = `${n} document${n === 1 ? "" : "s"}`;
}

/* ---------------------------------------------------------
   CHAT
   --------------------------------------------------------- */
const chatForm = document.getElementById("chat-form");
const chatInput = document.getElementById("chat-input");
const chatThread = document.getElementById("chat-thread");
const sendBtn = document.getElementById("send-btn");

chatForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const question = chatInput.value.trim();
  if (!question) return;

  removeIntro();
  addUserMessage(question);
  chatInput.value = "";
  sendBtn.disabled = true;

  const typingEl = addTypingIndicator();

  try {
    const { answer, citations } = await API.askQuestion(question, state.documents);
    typingEl.remove();
    addAssistantMessage(answer, citations);
  } catch (err) {
    typingEl.remove();
    addAssistantMessage(
      "Something went wrong reaching the assistant. Please try again.",
      []
    );
    console.error(err);
  } finally {
    sendBtn.disabled = false;
    chatInput.focus();
  }
});

function removeIntro() {
  const intro = document.querySelector(".thread-intro");
  if (intro) intro.remove();
}

function addUserMessage(text) {
  const el = document.createElement("div");
  el.className = "msg user";
  el.innerHTML = `<div class="msg-bubble">${escapeHtml(text)}</div>`;
  chatThread.appendChild(el);
  scrollToBottom();
}

function addTypingIndicator() {
  const el = document.createElement("div");
  el.className = "msg assistant";
  el.innerHTML = `<div class="msg-bubble typing">Retrieving relevant passages…</div>`;
  chatThread.appendChild(el);
  scrollToBottom();
  return el;
}

function addAssistantMessage(text, citations) {
  const el = document.createElement("div");
  el.className = "msg assistant";
  const msgId = crypto.randomUUID().slice(0, 8);

  const tabsHtml = citations
    .map(
      (c, i) => `
      <button class="citation-tab" data-target="cite-${msgId}-${i}">
        Source ${i + 1} · ${escapeHtml(c.doc)}
      </button>`
    )
    .join("");

  const cardsHtml = citations
    .map(
      (c, i) => `
      <div class="citation-card" id="cite-${msgId}-${i}">
        <p class="cite-source"><span>${escapeHtml(c.doc)}</span><span>p. ${c.page}</span></p>
        <p class="cite-excerpt">"${escapeHtml(c.excerpt)}"</p>
      </div>`
    )
    .join("");

  el.innerHTML = `
    <div class="msg-bubble">${escapeHtml(text)}</div>
    ${citations.length ? `<div class="citations">${tabsHtml}</div>${cardsHtml}` : ""}
  `;

  chatThread.appendChild(el);
  wireCitationTabs(el);
  scrollToBottom();
}

function wireCitationTabs(container) {
  container.querySelectorAll(".citation-tab").forEach((btn) => {
    btn.addEventListener("click", () => {
      const target = document.getElementById(btn.dataset.target);
      if (target) target.classList.toggle("open");
    });
  });
}

function scrollToBottom() {
  chatThread.scrollTop = chatThread.scrollHeight;
}

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}
