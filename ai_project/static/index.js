
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
    // const requestBtn = document.getElementById("ai_request_button");
    const spinner = document.getElementById('ai_request_spinner')
    spinner.style.display = "inline-block";
    
};