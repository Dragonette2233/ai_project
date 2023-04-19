// Используем setTimeout для того, чтобы скрыть flash сообщение через 5 секунд

setTimeout(function(){
    var alerts = document.querySelectorAll('.alert');
    alerts.forEach(function(alert){
      alert.style.display = 'none';
    });
  }, 5000);

function deleteNote(noteID) {
    fetch('/delete-note', {
        method: 'POST',
        body: JSON.stringify({noteID: noteID})
    }).then((_res) => {
        window.location.href = "/";
    });
}