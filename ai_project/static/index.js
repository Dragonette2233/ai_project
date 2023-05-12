
var element = document.getElementById("ai_request_response");

if (element != null) {

  element.scrollTop = element.scrollHeight;

}

setTimeout(
  function(){
    var alerts_btn = document.querySelectorAll('.btn-close');
    alerts_btn.forEach(
      function(button){
      button.click();
    });
  }, 
  4500);

function deleteNote(noteID) {
    fetch('/delete-note', {
        method: 'POST',
        body: JSON.stringify({noteID: noteID})
    }).then((_res) => {
        window.location.href = "/";
    });
}

function displaySninner() {

    // const spinner = document.getElementById('ai_request_spinner');
    const form = document.getElementById('ai_form');
    const textAreaElement = document.getElementById('ai_request');

    var fatherElement = document.getElementById("ai_request_response");
    var targetElement = document.getElementById('response-list');
    
    // spinner.style.display = "inline-block";
    if (textAreaElement.value.length >= 3) {
      var spinnerElement = document.createElement('span')
      var newRequest = document.createElement('li');
      var newResponse = document.createElement('li');

      newRequest.textContent = textAreaElement.value;
      newResponse.textContent = 'Generating response';
      newRequest.className = 'list-group-item list-group-item-light border p-3';
      newResponse.className = 'list-group-item list-group-item-secondary';
      spinnerElement.className = 'spinner-border spinner-border-sm ml-3';
      spinnerElement.role = 'status';
      spinnerElement.ariaHidden = 'true';

      targetElement.appendChild(newRequest);
      targetElement.appendChild(newResponse);
      newResponse.appendChild(spinnerElement);

      fatherElement.scrollTop = element.scrollHeight;
      
      
    }

};