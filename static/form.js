// Gets a list of radio buttons with specified name and returns value of checked radio or an empty string if none checked
const getRadioVal = (form, name) => {
  let val = '';
  let radios = form.elements[name];
  
  // loops through list of radio buttons
  for (let i=0, len=radios.length; i<len; i++) {
      if (radios[i].checked) {
          val = radios[i].value;
          break;
      }
  }

  return val;
}

// Checks if all form fields are filled in and if so then enables the submit button
let manage = () => { 
  const gender = getRadioVal(document.getElementById('dietaryNeeds'), 'gender' );
  const level = getRadioVal(document.getElementById('dietaryNeeds'), 'activity' );

  let button = document.getElementById('submit-button');
    if (gender != '' && weight.value != '' && height.value != '' && age.value != '' && level != '') {
        button.disabled = false;
    }
    else {
        button.disabled = true;
    }
}