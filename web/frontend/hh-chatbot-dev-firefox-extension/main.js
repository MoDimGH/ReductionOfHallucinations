const isExtension = typeof browser !== 'undefined' && browser.runtime && browser.runtime.sendMessage;

const input = document.querySelector('input');
const button = document.querySelector('button');
const messages = document.querySelector('#chatbot-messages');

function appendMessage(from, text) {
    const div = document.createElement('div');
    div.textContent = `${from}: ${text}`;
    messages.appendChild(div);
    messages.scrollTop = messages.scrollHeight;
}

const chatHistory = JSON.parse(localStorage.getItem('chatbotSession') || '[]');
chatHistory.forEach(m => appendMessage(m.from, m.text));

function sendMessage() {
    const userText = input.value.trim();
    if (!userText) return;
    appendMessage('Du', userText);
    input.value = '';

    const message = { from: 'You', text: userText };
    chatHistory.push(message);

    fetchAnswer(userText);
}

async function fetchAnswer(userText) {
    const botReply = typeof browser !== 'undefined' ? await browser.runtime.sendMessage({
        type: "chat_request",
        message: userText,
        url: window.location.href
    }) : await fetch_standalone({
        type: "chat_request",
        message: userText,
        url: window.location.href
    });

    appendMessage('Bot', botReply.answer);
    chatHistory.push({ from: 'Bot', text: botReply.answer });
    localStorage.setItem('chatbotSession', JSON.stringify(chatHistory));
}

async function fetch_standalone(request) {
    console.log("Chat request received");
    if (request.type === "chat_request") {
        try {
            console.log("request.message")
            const response = await fetch("http://172.236.193.62:8000/api/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ question: request.message, url: request.url })
            });

            if (!response.ok) throw new Error(`Server error`);

            const data = await response.json();
            const botReply = data.answer || 'Ups! Ein Fehler ist aufgetreten.';
            return { answer: botReply };
        } catch (err) {
            console.error(err);
            return { answer: 'Ups! Ein Fehler ist aufgetreten.' };
        }
    }
    return { answer:'Ups! Ein Fehler ist aufgetreten.' };
}

button.onclick = sendMessage;
input.onkeydown = (e) => {
    if (e.key === 'Enter') sendMessage();
};

window.addEventListener('beforeunload', () => {
    localStorage.setItem('chatbotSession', JSON.stringify(chatHistory));
});