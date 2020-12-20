let buttons = document.getElementsByClassName("small-recipe-container");
let modals = document.getElementsByClassName("modal");
let spans = document.getElementsByClassName("close");
for (let i=0; i<buttons.length; i++) {
  buttons[i].onclick = () => {
    modals[i].style.display = "block";
  }
  spans[i].onclick = function() {
    modals[i].style.display = "none";
  }
  window.onclick = function(event) {
    if (event.target == modals[i]) {
      modals[i].style.display = "none";
    }
  }
}



// // Get the modal
// var modal = document.getElementById("myModal");

// // Get the button that opens the modal
// var btn = document.getElementById("myBtn");
// console.log(btn);

// // Get the <span> element that closes the modal
// var span = document.getElementsByClassName("close")[0];

// // When the user clicks on the button, open the modal
// btn.onclick = function() {
//   modal.style.display = "block";
// }

// // When the user clicks on <span> (x), close the modal
// span.onclick = function() {
//   modal.style.display = "none";
// }

// // When the user clicks anywhere outside of the modal, close it
// window.onclick = function(event) {
//   if (event.target == modal) {
//     modal.style.display = "none";
//   }
// }