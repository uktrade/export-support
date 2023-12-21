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
        // Get the name of the market in the element list
        // will be in the form <<market_name>>__ess_export so need to split the value
        var marketChoice = options[i].value.split("__")[0];
        // If the choice does not contain the characters in the input,
        // set the display style to none for the parent (to catch the select box and its label)
        if (marketChoice.toUpperCase().indexOf(filter) > -1) {
          options[i].parentNode.style.display = "";
        } else {
          options[i].parentNode.style.display = "none";
        }
      }
    });

    // ***
    // MARKET NAME TAGS LIST
    // ***
    // Initialise tags array
    var marketTags = [];
    // Loop through all market checkbox options
    for (var i = 0; i < options.length; i++) {
      // Get the HTML element and make it a usable object
      const marketOption = options[i];

      // Check if option is already ticked (through returning to the page)
      if (marketOption.checked == true) {
        createMarketTag(marketOption);
      }

      // Add event listener to trigger when the input is checked or unchecked
      options[i].addEventListener("change", () => {
        // If box has been checked, add new tag
        // Else, remove tag element
        if (marketOption.checked == true) {
          createMarketTag(marketOption);
          updateTagsDisplay();
        } else {
          // Remove tag from tag array
          destroyMarketTag(marketOption);
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

    function createMarketTag(marketOption) {
      // Get the backend name of the market from the checkbox value
      var marketName = marketOption.value.split("__")[0];
      // Create the tag using the option value
      const tag = document.createElement("div");
      tag.className = "market-selected-tag";
      //tag.className = "govuk-tag market-selected-tag";
      tag.id = "market-selected-tag-" + marketName;

      // Get the market name as it appears on the checkbox label
      var formattedMarketName = marketOption.labels[0].innerText;

      // Format the content of the tag; a cross followed by the market name
      tag.innerHTML =
        "<span class='remove-cross'>\u00D7</span>" +
        "<p class='market-tag-text'>" +
        formattedMarketName +
        "</p>";

      // Add an onclick function to the tag, so when clicked, the tag is removed
      // and the corresponding checkbox is unticked. Call function to check if we need the market overflow message.
      tag.onclick = function () {
        destroyMarketTag(marketOption);
        marketOption.checked = false;
        updateTagsDisplay();
      };

      // Add tag to tags array
      marketTags.push(tag);
    }

    function destroyMarketTag(marketOption) {
      // Get the name of the market from the checkbox value, remove tag from display
      var marketName = marketOption.value.split("__")[0];
      // Get the tag to remove
      const tagToRemove = document.getElementById(
        "market-selected-tag-" + marketName
      );
      // Identify the position of the tag in the tag array
      var indexNum = marketTags.indexOf(tagToRemove);
      // Remove tag from array and display
      marketTags.splice(indexNum, 1);
      tagToRemove.remove();
    }

    function updateTagsDisplay() {
      const tagContainer = document.getElementById("market-tag-container");
      const hiddenTagContainer = document.getElementById(
        "market-tag-long-list-container"
      );

      // Clear existing tags so they get ordered correctly on update
      tagContainer.innerHTML = "";
      hiddenTagContainer.innerHTML = "";

      // Sort tags (so if re-added they return in alphabetical order)
      marketTags = marketTags.sort(function (a, b) {
        var x = a["innerHTML"];
        var y = b["innerHTML"];
        return x < y ? -1 : x > y ? 1 : 0;
      });

      // Loop through tags array and add the tags to the correct container
      for (var i = 0; i < marketTags.length; i++) {
        // Add tag to visible container
        tagContainer.appendChild(marketTags[i]);
        // Check if adding the tag has caused overflow
        var tooManyMarketTags = checkOverflow();
        if (tooManyMarketTags == true) {
          // If there is overflow, move the tag to the overflow container
          tagContainer.removeChild(marketTags[i]);
          hiddenTagContainer.appendChild(marketTags[i]);
        }
      }

      // Once the tags are sorted and arranged, update the indicator text
      updateOverflowIndicator();
    }

    function checkOverflow() {
      // Get the container for the scroll height
      const tagContainer = document.getElementById("market-tag-container");
      // Get a tag so we can determine the height of one tag row
      // No JS method exists for height including margins, so will need to work this out
      const tagList = document.getElementsByClassName("market-selected-tag");
      var tagStyle = getComputedStyle(tagList[0]);
      var tagHeight =
        parseInt(tagList[0].offsetHeight) +
        parseInt(tagStyle.marginTop) +
        parseInt(tagStyle.marginBottom);
      // Scroll height is the height of the content (tags list),
      // if the scroll height is more than the height of one tag,
      // we have too many market tags
      if (tagHeight >= tagContainer.scrollHeight) {
        return false;
      } else {
        return true;
      }
    }

    // ***
    // MARKET NAME LONG TAGS LIST SHOW/HIDE
    // ***
    function updateOverflowIndicator() {
      // Identify the container for the lon-list of tags and the indicator div
      const longListTagContainer = document.getElementById(
        "market-tag-long-list-container"
      );
      const longListIndicator = document.getElementById(
        "market-tag-long-list-indicator"
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
          "market-tag-long-list-indicator-text"
        );
        longListIndicatorText.innerHTML =
          "...and " + hiddenTagsCount + " other markets";

        // Build the show/hide button and attach it to the indicator div
        const showHideButton = document.getElementById(
          "market-tag-long-list-indicator-button"
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
