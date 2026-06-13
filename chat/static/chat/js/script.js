document.addEventListener("DOMContentLoaded", () => {

    addCopyButtons();
    highlightCode();

    document
    .querySelectorAll(".markdown-content")
    .forEach(element => {

        element.innerHTML =
            marked.parse(
                element.textContent
            );

    });

    const sidebar =
        document.querySelector(".sidebar");

    const openBtn =
        document.getElementById("toggleSidebar");

    const closeBtn =
        document.getElementById("closeSidebar");

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

    const form =
        document.getElementById("chat-form");

    const input =
        document.getElementById("message-input");

    input.addEventListener("keydown", function(e){

        if(e.key === "Enter" && !e.shiftKey){

            e.preventDefault();

            form.requestSubmit();

        }

    });

    const messages =
        document.getElementById("messages");

    form.addEventListener("submit", async (e) => {

        e.preventDefault();

        const userMessage =
            input.value.trim();

        const fileInput =
            document.getElementById("file-input");

        if(
            !userMessage &&
            fileInput.files.length === 0
        ){
            return;
        }

        messages.innerHTML += `
            <div class="user-container">
                <div class="user-message">
                    ${
                        userMessage ||
                        "📄 PDF Uploaded"
                    }
                </div>
            </div>
        `;

        input.value = "";

        messages.scrollTop =
            messages.scrollHeight;

        const formData =
            new FormData();
formData.append(
    "message",
    userMessage
);

if(
    fileInput &&
    fileInput.files.length > 0
){

    formData.append(
        "file",
        fileInput.files[0]
    );

}

const thinkingId =
    "thinking-" + Date.now();

messages.innerHTML += `
    <div class="ai-container" id="${thinkingId}">
        <div class="avatar">⚡</div>

        <div class="ai-message">
            Thinking...
        </div>
    </div>
`;

messages.scrollTop =
    messages.scrollHeight;

let data;

try{

    const response = await fetch(
        `/send-message/${CHAT_ID}/`,
        {
            method: "POST",

            headers: {
                "X-CSRFToken":
                getCookie("csrftoken")
            },

            body: formData
        }
    );

    data = await response.json();

    console.log(
        "Backend Response:",
        data
    );

}
catch(error){

    console.error(
        "Fetch Error:",
        error
    );

    data = {
        bot_response:
        "⚠️ Server error. Please try again."
    };

}

input.value = "";

if(fileInput){

    fileInput.value = "";

}

document
    .getElementById(thinkingId)
    ?.remove();

const aiId =
    "ai-" + Date.now();

messages.innerHTML += `
    <div class="ai-container">

        <div class="avatar">
            ⚡
        </div>

        <div
            class="ai-message"
            id="${aiId}">
        </div>

    </div>
`;

typeMessage(

    document.getElementById(aiId),

    data.bot_response ||
    "⚠️ No response received."

);

addCopyButtons();

highlightCode();

messages.scrollTop =
    messages.scrollHeight;

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


function addCopyButtons(){

    document.querySelectorAll("pre").forEach(pre => {

        if(pre.querySelector(".copy-btn")) return;

        const btn = document.createElement("button");

        btn.innerText = "Copy";

        btn.className = "copy-btn";

        btn.onclick = () => {

            const codeText = pre.innerText.replace("Copy", "");

            navigator.clipboard.writeText(codeText);

            btn.innerText = "Copied!";

            setTimeout(() => {

                btn.innerText = "Copy";

            }, 1500);

        };

        pre.prepend(btn);

    });

}
function highlightCode(){

    document
        .querySelectorAll("pre code")
        .forEach((block) => {

            hljs.highlightElement(block);

        });

}


function typeMessage(element, text){

    if(
        !element
    ){
        return;
    }

    if(
        !text ||
        typeof text !== "string"
    ){

        element.innerHTML =
            "⚠️ No response received.";

        return;
    }

    let i = 0;

    const timer = setInterval(() => {

        if(
            i >= text.length
        ){

            clearInterval(timer);

            return;
        }

        element.innerHTML =
            marked.parse(
                text.substring(
                    0,
                    i + 1
                )
            );

        addCopyButtons();

        highlightCode();

        i++;

    }, 15);

}

function renameChat(chatId){

    const renameInput =
        document.getElementById(
            "renameInput"
        );

    if(!renameInput){

        alert(
            "Rename input not found."
        );

        return;
    }

    const newTitle =
        renameInput.value.trim();

    if(!newTitle){

        alert(
            "Type a new title first."
        );

        return;
    }

    const form =
        document.getElementById(
            "renameForm"
        );

    if(!form){

        alert(
            "Rename form not found."
        );

        return;
    }

    form.action =
        `/rename-chat/${chatId}/`;

    form.submit();

}
function showRename(chatId){

    const form =
        document.getElementById(
            `rename-form-${chatId}`
        );

    form.classList.toggle(
        "show-rename"
    );
}

function startRename(chatId){

    const titleView =
        document.getElementById(
            `title-view-${chatId}`
        );

    const renameForm =
        document.getElementById(
            `rename-form-${chatId}`
        );

    titleView.style.display = "none";

    renameForm.style.display = "block";

    renameForm
        .querySelector("input")
        .focus();
}


function handleRename(event,chatId){

    if(event.key === "Enter"){

        event.preventDefault();

        document
            .getElementById(
                `rename-form-${chatId}`
            )
            .submit();
    }

    if(event.key === "Escape"){

        document.getElementById(
            `rename-form-${chatId}`
        ).style.display = "none";

        document.getElementById(
            `title-view-${chatId}`
        ).style.display = "block";
    }
}