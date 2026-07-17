const chatWindow = document.getElementById("chat-window");
const chatForm = document.getElementById("chat-form");
const chatInput = document.getElementById("chat-input");

function appendMessage(role, html) {
    const wrapper = document.createElement("div");
    wrapper.className = `chat-message ${role}`;
    const icon = role === "user" ? "bi-person-fill" : "bi-robot";
    wrapper.innerHTML = `<i class="bi ${icon}"></i><div class="bubble">${html}</div>`;
    chatWindow.appendChild(wrapper);
    chatWindow.scrollTop = chatWindow.scrollHeight;
    return wrapper;
}

async function askQuestion(question) {
    appendMessage("user", question);
    const thinkingBubble = appendMessage("assistant", "<em>Retrieving relevant documents and generating an answer...</em>");

    try {
        const res = await fetch("/api/assistant/ask", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ question }),
        });
        const data = await res.json();

        if (!res.ok) {
            thinkingBubble.querySelector(".bubble").innerHTML = `<span class="text-danger">${data.error}</span>`;
            return;
        }

        let html = data.answer.replace(/\n/g, "<br>");
        if (data.sources && data.sources.length) {
            html += `<div class="chat-sources">Sources: ${data.sources.join(", ")}</div>`;
        }
        thinkingBubble.querySelector(".bubble").innerHTML = html;
    } catch (err) {
        thinkingBubble.querySelector(".bubble").innerHTML = `<span class="text-danger">Request failed: ${err}</span>`;
    }
}

chatForm.addEventListener("submit", (e) => {
    e.preventDefault();
    const question = chatInput.value.trim();
    if (!question) return;
    chatInput.value = "";
    askQuestion(question);
});

document.querySelectorAll(".suggested-query").forEach(btn => {
    btn.addEventListener("click", () => askQuestion(btn.textContent.trim()));
});
