browser.runtime.onMessage.addListener((request, sender, sendResponse) => {
    console.log("Chat request received");
    if (request.type === "chat_request") {
        (async () => {
            try {
                console.log("request.message")
                const response = await fetch("http://172.236.193.62:8000/api/chat", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ question: request.message, url: request.url })
                });

                if (!response.ok) throw new Error(`Server error`);
		
                const data = await response.json();
                console.log(JSON.stringify(data, 0, 2));
		const botReply = data.answer || 'Entschuldigung, ich habe keine Antwort finden können.';
                return sendResponse({ answer: botReply });
            } catch (err) {
                console.error(err);
                return sendResponse({ answer: `Ups! Ein Fehler ist aufgetreten. ${err}` });
            }
        })();
    } else {
        sendResponse({ answer: 'Ups! Ein Fehler ist aufgetreten.' });
    }
    return true;
});