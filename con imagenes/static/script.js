async function sendMessage() {
  const input = document.getElementById("userInput");
  const responseBox = document.getElementById("response");

  const message = input.value.trim();
  if (!message) return;

  const res = await fetch("/chat", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ message })
  });

  const data = await res.json();
  responseBox.textContent = data.reply;
  input.value = "";
}
