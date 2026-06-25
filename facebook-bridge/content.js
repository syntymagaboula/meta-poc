const BACKEND_URL =
  "https://animated-space-journey-jjppwrvpv94w2p6wp-8000.app.github.dev/webhook/facebook";

const processedMessages = new Set();

async function sendToBackend(messageId, text) {
  try {
    await fetch(BACKEND_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        source: "facebook",
        message_id: messageId,
        message: text,
        timestamp: new Date().toISOString()
      })
    });

    console.log("Envoyé :", text);
  } catch (error) {
    console.error("Erreur webhook :", error);
  }
}

function scanMessages() {

  const messages = document.querySelectorAll(
    "[data-message-id]"
  );

  messages.forEach((messageNode) => {

    const messageId =
      messageNode.getAttribute("data-message-id");

    if (!messageId) return;

    if (processedMessages.has(messageId))
      return;

    const text =
      messageNode.innerText?.trim();

    if (!text) return;

    processedMessages.add(messageId);

    sendToBackend(
      messageId,
      text
    );
  });
}

setInterval(
  scanMessages,
  2000
);

console.log(
  "Canalbox Facebook Bridge démarré"
);