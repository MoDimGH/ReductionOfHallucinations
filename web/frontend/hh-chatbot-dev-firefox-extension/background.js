browser.runtime.onMessage.addListener(async (request, sender) => {
    if (request.type === "chat_request") {
      const response = await fetch("http://172.236.193.62/api/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ message: request.message })
      });
      const data = await response.json();
      return Promise.resolve(data);
    }
  });
  