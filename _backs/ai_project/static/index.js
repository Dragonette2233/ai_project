
var element = document.getElementById("ai_request_response");

if (element != null) {

  element.scrollTop = element.scrollHeight;

}

setTimeout(
  function(){
    var alerts = document.querySelectorAll('.alert');
    alerts.forEach(
      function(alert){
      alert.style.display = 'none';
    });
  }, 
  5000);

function deleteNote(noteID) {
    fetch('/delete-note', {
        method: 'POST',
        body: JSON.stringify({noteID: noteID})
    }).then((_res) => {
        window.location.href = "/";
    });
}

function displaySnipper() {

    const spinner = document.getElementById('ai_request_spinner');
    const form = document.getElementById('ai_form');
    const textarea = document.getElementById('ai_request');

    form.addEventListener('submit', function(event) {
      if (textarea.value.length <= 3) {
        event.preventDefault(); // отменяем отправку формы
        
      }
      else {
        spinner.style.display = "inline-block";
      }
    });
    
};