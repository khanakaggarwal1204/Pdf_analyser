//API Functions
console.log("NEW APP.JS LOADED")
window.onerror = function (msg, src, line, col, err) {
  console.error("GLOBAL ERROR:", msg, "at line", line, err);
};
console.log("Page loaded at", new Date().toLocaleTimeString());
const API = {
  async uploadDocument(file) {
    const formData = new FormData();
    formData.append("file", file);

    const response = await fetch("http://127.0.0.1:8000/upload", {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      throw new Error("Upload failed");
    }

    const data = await response.json();

    return {
      id: crypto.randomUUID(),
      name: data.filename,
      pages: "-",
      status: "indexed",
    };
  },

  async askQuestion(question) {
    const response = await fetch("http://127.0.0.1:8000/ask", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        question: question,
      }),
    });

    if (!response.ok) {
      throw new Error("Failed to get answer");
    }

    const data = await response.json();

    return {
      answer: data.answer,
      citations: [],
    };
  },
};

function delay(ms) {
  return new Promise((res) => setTimeout(res, ms));
}

const state = {
  user: null,
  documents: [],
};

const signinOverlay = document.getElementById("signin-overlay");
const signinForm = document.getElementById("signin-form");
const signinNameInput = document.getElementById("signin-name");
const guestBtn = document.getElementById("guest-btn");
const appEl = document.getElementById("app");
const userChip = document.getElementById("user-chip");
const signoutBtn = document.getElementById("signout-btn");
const savedUser = localStorage.getItem("user");
if (savedUser) {
  enterApp(savedUser);
}

function enterApp(name) {
  state.user = name || "Guest";
  localStorage.setItem("user", state.user);

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
  localStorage.removeItem("user");
  appEl.hidden = true;
  signinOverlay.hidden = false;
  signinNameInput.value = "";
});

const fileInput = document.getElementById("file-input");
const dropzone = document.getElementById("dropzone");
const catalogDrawer = document.getElementById("catalog-drawer");
const catalogEmpty = document.getElementById("catalog-empty");
const docCount = document.getElementById("doc-count");

// fileInput.addEventListener("change", async (e) => {
//   console.log("CHANGE EVENT");
//   await handleFiles(e.target.files);
//   console.log("HANDLEFILES FINISHED");
// });

fileInput.addEventListener("change", async (e) => {
  console.log("CHANGE EVENT");

  try {
    await handleFiles(e.target.files);
    console.log("HANDLEFILES FINISHED");
  } catch (err) {
    console.error("OUTER ERROR:", err);
  }
});

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
dropzone.addEventListener("drop", (e) => {
  e.preventDefault();
  handleFiles(e.dataTransfer.files);
});

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
  <p class="doc-meta">
    <span>indexing…</span>
    <span>⏳</span>
  </p>
`;
  catalogDrawer.appendChild(card);
}

function replacePendingCard(id, doc) {
  const card = document.getElementById(id);

  if (!card) return;

  card.innerHTML = `
    <div class="doc-header">
      <p class="doc-name">${escapeHtml(doc.name)}</p>

      <button class="delete-btn" data-file="${doc.name}">
        🗑️
      </button>
    </div>

    <p class="doc-meta">
      <span class="doc-status">
        indexed · ${doc.pages}p
      </span>

      <span>✓</span>
    </p>
  `;

  const deleteBtn = card.querySelector(".delete-btn");

  deleteBtn.addEventListener("click", async () => {
    await deleteDocument(doc.name);

    card.remove();

    state.documents = state.documents.filter(
      d => d.name !== doc.name
    );

    updateDocCount();
  });
}

function removeCard(id) {
  const card = document.getElementById(id);
  if (card) card.remove();
}

function updateDocCount() {
  const n = state.documents.length;
  docCount.textContent = `${n} document${n === 1 ? "" : "s"}`;
}

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
    const { answer, citations } = await API.askQuestion(question);
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

async function deleteDocument(filename) {
  try {
    const response = await fetch(
      `http://127.0.0.1:8000/delete/${encodeURIComponent(filename)}`,
      {
        method: "DELETE",
      }
    );

    if (!response.ok) {
      throw new Error("Delete failed");
    }

    state.documents = state.documents.filter(doc => doc.name !== filename);

    renderCatalog();

  } catch (err) {
    console.error(err);
    alert("Couldn't delete the document.");
  }
}