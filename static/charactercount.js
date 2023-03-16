function countText() {
    let text = document.count_text.text.value;
    document.getElementById('characters').innerText = text.length;
    document.getElementById('words').innerText = text.length == 0 ? 0 : text.split(/\s+/).length;
    document.getElementById('rows').innerText = text.length == 0 ? 0 : text.split(/\n/).length;
  }