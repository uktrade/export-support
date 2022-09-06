const initLocationFilter = () => {
  // Check we have a location fieldset on the page, if one is not on the page, we avoid running
  // later code and causing errors
  const locationWrappers = document.querySelectorAll(
    "[id='location-fieldset']"
  );

  locationWrappers.forEach(() => {
    var input, filter, listContainer, options;
    // Get the input textbox element
    input = document.getElementById("location-option-filter");
    // Show the filter text box (so its only visible if JS is enabled)
    input.style.display = "";
    // Get the container surrounding the list of options
    listContainer = document.getElementById("location-options");
    // Get the individual elements inside the container
    options = listContainer.getElementsByTagName("input");

    // Event triggers when new character appears in the input text box
    input.addEventListener("keyup", () => {
      // Get the value inside the input text box
      filter = input.value.toUpperCase();
      // Loop through list of individual elements
      for (var i = 0; i < options.length; i++) {
        // Get the name of the country in the element list
        // will be in the form <<country_name>>__ess_export so need to split the value
        var countryChoice = options[i].value.split("__")[0];
        // If the choice does not contain the characters in the input,
        // set the display style to none for the parent (to catch the select box and its label)
        if (countryChoice.toUpperCase().indexOf(filter) > -1) {
          options[i].parentNode.style.display = "";
        } else {
          options[i].parentNode.style.display = "none";
        }
      }
    });
  });
};
export default initLocationFilter;
