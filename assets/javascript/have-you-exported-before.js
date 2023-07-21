document.addEventListener("DOMContentLoaded", function () {
  // Show-hide for the "Have you exported before question?"
  let have_you_exported_before_element = document.querySelector(
    ".have_you_exported_before_form_group"
  );
  let do_you_have_product_element = document.querySelector(
    ".do_you_have_a_product_you_want_to_export_form_group"
  );

  have_you_exported_before_element.addEventListener(
    "change",
    function () {
      let chosen_value = document.querySelector(
        "input[name$='have_you_exported_before']:checked"
      ).value;
      if (chosen_value === "not_exported__ess_experience") {
        // Answer is "No" - show the "Do you have a product you want to export?" question
        do_you_have_product_element.style.display = "block";
      } else {
        // Otherwise, hide the question and set radio button to null so it isn't passed to zendesk
        do_you_have_product_element.style.display = "none";
        document.querySelector(
          "input[name$='do_you_have_a_product_you_want_to_export']:checked"
        ).checked = false;
      }
    },
    false
  );

  // ON page load, hide the "Do you have a product you want to export?" question
  do_you_have_product_element.style.display = "none";

  // On page load, if the answer to "Have you exported before?" is "No", show the "Do you have a product you want to export?" question
  if (
    document.querySelector("input[name$='have_you_exported_before']:checked")
      .value === "not_exported__ess_experience"
  ) {
    do_you_have_product_element.style.display = "block";
  }
});
