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
    const botReply = await browser.runtime.sendMessage({
        type: "chat_request",
        message: userText,
        url: window.location.href
    });

    console.log(JSON.stringify(botReply, 0, 2));

    appendMessage('Bot', botReply.answer.content);
    chatHistory.push({ from: 'Bot', text: botReply.answer.content });
    localStorage.setItem('chatbotSession', JSON.stringify(chatHistory));
}

button.onclick = sendMessage;
input.onkeydown = (e) => {
    if (e.key === 'Enter') sendMessage();
};

window.addEventListener('beforeunload', () => {
    localStorage.setItem('chatbotSession', JSON.stringify(chatHistory));
});