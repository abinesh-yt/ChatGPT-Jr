document.addEventListener("DOMContentLoaded", () => {

    // SIDEBAR

    const sidebar = document.querySelector(".sidebar");

    const openBtn = document.getElementById("toggleSidebar");

    const closeBtn = document.getElementById("closeSidebar");

    openBtn.addEventListener("click", () => {

        sidebar.classList.add("show");

        openBtn.style.display = "none";

        closeBtn.style.display = "block";

    });

    closeBtn.addEventListener("click", () => {

        sidebar.classList.remove("show");

        closeBtn.style.display = "none";

        openBtn.style.display = "block";

    });

    // CHAT

    const form = document.getElementById("chat-form");

    const input = document.getElementById("message-input");
    input.addEventListener("keydown", function(e){

    if(e.key === "Enter" && !e.shiftKey){

        e.preventDefault();

        form.requestSubmit();
    }

});

    const messages = document.getElementById("messages");

    form.addEventListener("submit", async (e) => {

        e.preventDefault();

        const userMessage = input.value.trim();

        if (!userMessage) return;

        messages.innerHTML += `
            <div class="user-container">
                <div class="user-message">
                    ${userMessage}
                </div>
            </div>
        `;

        input.value = "";

        messages.scrollTop = messages.scrollHeight;

        const formData = new FormData();

        formData.append("message", userMessage);

        // Thinking message

        const thinkingId = "thinking-" + Date.now();

        messages.innerHTML += `
            <div class="ai-container" id="${thinkingId}">
                <div class="avatar">⚡</div>

                <div class="ai-message">
                    Thinking...
                </div>
            </div>
        `;

        messages.scrollTop = messages.scrollHeight;

        const response = await fetch(
            `/send-message/${CHAT_ID}/`,
            {
                method: "POST",
                headers: {
                    "X-CSRFToken": getCookie("csrftoken")
                },
                body: formData
            }
        );

        const data = await response.json();

        document
            .getElementById(thinkingId)
            .remove();

        messages.innerHTML += `
            <div class="ai-container">
                <div class="avatar">⚡</div>

                <div class="ai-message">
                    ${marked.parse(data.bot_response)}
                </div>
            </div>
        `;

        messages.scrollTop = messages.scrollHeight;

    });

});

function getCookie(name) {

    let cookieValue = null;

    if (document.cookie && document.cookie !== "") {

        const cookies = document.cookie.split(";");

        for (let cookie of cookies) {

            cookie = cookie.trim();

            if (
                cookie.substring(
                    0,
                    name.length + 1
                ) === (name + "=")
            ) {

                cookieValue = decodeURIComponent(
                    cookie.substring(
                        name.length + 1
                    )
                );

                break;
            }
        }
    }

    return cookieValue;
}