(function () {
    if (document.getElementById("chatbot-container")) return;
  
    const iframe = document.createElement("iframe");
    iframe.src = browser.runtime.getURL("ui.html");
    iframe.id = "chatbot-container";
    iframe.style.cssText = `
      position: fixed;
      bottom: 20px;
      right: 20px;
      width: 400px;
      height: 600px;
      z-index: 9999;
      border: none;
      border-radius: 10px;
      box-shadow: 0 0 10px rgba(0,0,0,0.5);
    `;
    document.body.appendChild(iframe);
  })();
  