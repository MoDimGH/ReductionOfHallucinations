(function () {
    if (document.getElementById("hamburg-chatbot")) return;
  
    const iframe = document.createElement("iframe");
    iframe.src = browser.runtime.getURL("ui.html");
    iframe.id = "hamburg-chatbot";
    iframe.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        width: 350px;
        height: 500px;
        background: white;
        border: 1px solid #ccc;
        border-radius: 12px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.2);
        z-index: 10000;
        font-family: sans-serif;
        display: flex;
        flex-direction: column;
    `;
    document.body.appendChild(iframe);
  })();
  