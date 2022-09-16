const initLocationFilter = () => {
  // Check we have a location fieldset on the page, if one is not on the page, we avoid running
  // later code and causing errors
  const locationWrappers = document.querySelectorAll(
    "[id='location-option-select']"
  );

  locationWrappers.forEach(() => {
    var input, listContainer, options;
    // Get the input textbox element
    input = document.getElementById("location-option-filter");
    // Show the filter text box (so its only visible if JS is enabled)
    input.classList.remove("hidden-option-filter");
    // Get the container surrounding the list of options
    listContainer = document.getElementById("location-options");
    // Get the individual elements inside the container
    options = listContainer.getElementsByTagName("input");

    // ***
    // FILTER SEARCH BAR
    // ***
    // Event triggers when new character appears in the input text box
    input.addEventListener("keyup", () => {
      // Get the value inside the input text box
      var filter = input.value.toUpperCase();
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

    // ***
    // COUNTRY NAME TAGS LIST
    // ***
    // Initialise tags array
    var countryTags = [];
    // Loop through all country checkbox options
    for (var i = 0; i < options.length; i++) {
      // Get the HTML element and make it a usable object
      const countryOption = options[i];

      // Check if option is already ticked (through returning to the page)
      if (countryOption.checked == true) {
        createCountryTag(countryOption);
      }

      // Add event listener to trigger when the input is checked or unchecked
      options[i].addEventListener("change", () => {
        // If box has been checked, add new tag
        // Else, remove tag element
        if (countryOption.checked == true) {
          createCountryTag(countryOption);
          updateTagsDisplay();
        } else {
          // Remove tag from tag array
          destroyCountryTag(countryOption);
          updateTagsDisplay();
        }
      });
    }

    // Run initial tag update to catch pre-ticked options
    updateTagsDisplay();

    // Add event listener to the window to check the tags display when resizing
    window.addEventListener("resize", () => {
      updateTagsDisplay();
    });

    function createCountryTag(countryOption) {
      // Get the name of the country from the checkbox value
      var countryName = countryOption.value.split("__")[0];
      // Create the tag using the option value
      const tag = document.createElement("div");
      tag.className = "country-selected-tag";
      //tag.className = "govuk-tag country-selected-tag";
      tag.id = "country-selected-tag-" + countryName;

      // Format country name - capitalise first letter and replace underscores with spaces
      const splitCountryName = countryName.split("_");
      for (let i = 0; i < splitCountryName.length; i++) {
        if (splitCountryName[i] != "and") {
          splitCountryName[i] =
            splitCountryName[i].charAt(0).toUpperCase() +
            splitCountryName[i].slice(1);
        }
      }
      var formattedCountryName = splitCountryName.join(" ");

      // Format the content of the tag; a cross followed by the country name
      tag.innerHTML =
        "<span class='remove-cross'>\u00D7</span>" +
        "<p class='country-tag-text'>" +
        formattedCountryName +
        "</p>";

      // Add an onclick function to the tag, so when clicked, the tag is removed
      // and the corresponding checkbox is unticked. Call function to check if we need the country overflow message.
      tag.onclick = function () {
        destroyCountryTag(countryOption);
        countryOption.checked = false;
        updateTagsDisplay();
      };

      // Add tag to tags array
      countryTags.push(tag);
    }

    function destroyCountryTag(countryOption) {
      // Get the name of the country from the checkbox value, remove tag from display
      var countryName = countryOption.value.split("__")[0];
      // Get the tag to remove
      const tagToRemove = document.getElementById(
        "country-selected-tag-" + countryName
      );
      // Identify the position of the tag in the tag array
      var indexNum = countryTags.indexOf(tagToRemove);
      // Remove tag from array and display
      countryTags.splice(indexNum, 1);
      tagToRemove.remove();
    }

    function updateTagsDisplay() {
      const tagContainer = document.getElementById("country-tag-container");
      const hiddenTagContainer = document.getElementById(
        "country-tag-long-list-container"
      );

      // Clear existing tags so they get ordered correctly on update
      tagContainer.innerHTML = "";
      hiddenTagContainer.innerHTML = "";

      // Sort tags (so if re-added they return in alphabetical order)
      countryTags = countryTags.sort(function (a, b) {
        var x = a["innerHTML"];
        var y = b["innerHTML"];
        return x < y ? -1 : x > y ? 1 : 0;
      });

      // Loop through tags array and add the tags to the correct container
      for (var i = 0; i < countryTags.length; i++) {
        // Add tag to visible container
        tagContainer.appendChild(countryTags[i]);
        // Check if adding the tag has caused overflow
        var tooManyCountryTags = checkOverflow();
        if (tooManyCountryTags == true) {
          // If there is overflow, move the tag to the overflow container
          tagContainer.removeChild(countryTags[i]);
          hiddenTagContainer.appendChild(countryTags[i]);
        }
      }

      // Once the tags are sorted and arranged, update the indicator text
      updateOverflowIndicator();
    }

    function checkOverflow() {
      const tagContainer = document.getElementById("country-tag-container");
      // Scroll height is the height of the content (tags list),
      // if the scroll height is more than the client height (the height of the container),
      // we have too many country tags
      if (tagContainer.clientHeight >= tagContainer.scrollHeight) {
        return false;
      } else {
        return true;
      }
    }

    // ***
    // COUNTRY NAME LONG TAGS LIST SHOW/HIDE
    // ***
    function updateOverflowIndicator() {
      // Identify the container for the lon-list of tags and the indicator div
      const longListTagContainer = document.getElementById(
        "country-tag-long-list-container"
      );
      const longListIndicator = document.getElementById(
        "country-tag-long-list-indicator"
      );

      // Count how many tags are in the long-list container
      var hiddenTagsCount = longListTagContainer.childElementCount;

      // By default, don't show the overflow indicator section
      var overflow = false;
      // If there are tags in the long-list container, show the overflow container
      if (hiddenTagsCount > 0) {
        overflow = true;
      }

      if (overflow == true) {
        // Display the indicator section
        longListIndicator.style.display = "inline-block";

        // Set the text in the indicator div
        const longListIndicatorText = document.getElementById(
          "country-tag-long-list-indicator-text"
        );
        longListIndicatorText.innerHTML =
          "...and " + hiddenTagsCount + " other countries";

        // Build the show/hide button and attach it to the indicator div
        const showHideButton = document.getElementById(
          "country-tag-long-list-indicator-button"
        );
        // Add an onclick listener to the show/hide button
        showHideButton.onclick = function () {
          if (showHideButton.innerHTML == "Show") {
            // If the 'show' button was clicked, hide the indicator text, display the long-list tags container and change the button text to 'hide'
            longListTagContainer.style.display = "inline-block";
            longListIndicatorText.style.display = "none";
            showHideButton.innerHTML = "Hide";
          } else {
            // If the 'hide' button was clicked, display the indicator text, hide the long-list tags container and change the button text to 'show'
            longListTagContainer.style.display = "none";
            longListIndicatorText.style.display = "inline-block";
            showHideButton.innerHTML = "Show";
          }
        };
      } else {
        // No tags in the long list, so hide the indicator
        longListIndicator.style.display = "none";
      }
    }
  });
};
export default initLocationFilter;
