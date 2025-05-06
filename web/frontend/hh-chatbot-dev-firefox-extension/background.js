browser.runtime.onMessage.addListener(async (request, sender) => {
    if (request.type === "chat_request") {
        const response = await fetch("http://172.236.193.62/api/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ question: request.message, url: request.url })
        });
        const data = await response.json();
        return Promise.resolve(data);
    }
  });
  