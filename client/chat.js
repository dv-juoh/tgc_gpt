const eventSource = new EventSource("http://127.0.0.1:8000/sse");
eventSource.onmessage = function (event) {
  if (!event.data) {
    return;
  }
  const messagesDiv = document.getElementById("chat-messages");
  const botMessageDiv = document.createElement("div");
  botMessageDiv.classList.add("chat-message", "bot");
  const botMessageContent = document.createElement("p");
  botMessageContent.textContent = event.data;
  botMessageDiv.appendChild(botMessageContent);
  messagesDiv.appendChild(botMessageDiv);
  messagesDiv.scrollTop = messagesDiv.scrollHeight;
};
eventSource.onerror = function (error) {
  console.error("EventSource failed:", error);
  eventSource.close();
};

document.getElementById("chat-form").onsubmit = function (event) {
  event.preventDefault();
  const form = event.target;
  const messageInput = document.getElementById("message");
  const userMessage = messageInput.value;

  const messagesDiv = document.getElementById("chat-messages");
  const userMessageDiv = document.createElement("div");
  userMessageDiv.classList.add("chat-message", "user");
  const userMessageContent = document.createElement("p");
  userMessageContent.textContent = `User: ${userMessage}`;
  userMessageDiv.appendChild(userMessageContent);
  messagesDiv.appendChild(userMessageDiv);
  messagesDiv.scrollTop = messagesDiv.scrollHeight;

  fetch("http://127.0.0.1:8000/api/chat", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ context: userMessage }),
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.status === "Message received") {
      }
    })
    .catch((error) => {
      console.error("Error submitting form:", error);
    });

  form.reset();
};
