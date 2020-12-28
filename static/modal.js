// Get the buttons, modals and closing <span> element
let buttons = document.getElementsByClassName("small-recipe-container");
let modals = document.getElementsByClassName("modal");
let spans = document.getElementsByClassName("close");

// For each specific button clicked, do the following
for (let i=0; i<buttons.length; i++) {
  // When the user clicks on the button, open the modal
  buttons[i].onclick = () => {
    modals[i].style.display = "block";
  }
  // When the user clicks on <span> (x), close the modal
  spans[i].onclick = function() {
    modals[i].style.display = "none";
  }
  // When the user clicks anywhere outside of the modal, close it
  window.onclick = function(event) {
    if (event.target == modals[i]) {
      modals[i].style.display = "none";
    }
  }
}

// let show_saved = document.getElementById("show-saved");

// show_saved.onclick = () => {

// }