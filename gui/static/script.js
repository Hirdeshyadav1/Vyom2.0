async function sendMsg() {
  const input = document.getElementById('msgInput');
  const text = input.value.trim();
  if (!text) return;
  addMsg(text, 'user');
  input.value = '';
  const typing = addMsg('Vyom soch raha hai...', 'vyom');
  try {
    const res = await fetch('/api/chat', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({message: text})
    });
    const data = await res.json();
    typing.innerText = data.response;
  } catch (e) {
    typing.innerText = 'Connection error — server check karo.';
  }
}

function addMsg(text, cls) {
  const div = document.createElement('div');
  div.className = 'msg ' + cls;
  div.innerText = text;
  document.getElementById('chat').appendChild(div);
  div.scrollIntoView();
  return div;
}

document.getElementById('msgInput').addEventListener('keypress', function(e) {
  if (e.key === 'Enter') sendMsg();
});
