import accessibleAutocomplete from "accessible-autocomplete";
import debounce from "lodash.debounce";

(() => {
  // If the browser doesn't support the template element then we just don't
  // progressively enhance and we also need to stop the template from rendering
  const hasTemplate = typeof HTMLTemplateElement !== "undefined";
  if (!hasTemplate) {
    const template = document.querySelector(
      "#companies-house-autocomplete-template"
    );
    template.style.display = "none;";
    return;
  }

  const nameEl = document.querySelector("#id_business-details-company_name");

  const replaceCompanyNameFormGroup = () => {
    const companiesHouseAutocompleteTemplate = document.querySelector(
      "#companies-house-autocomplete-template"
    );
    const companyNameFormGroupId =
      companiesHouseAutocompleteTemplate.dataset.formGroupId;
    const companyNameFormGroupEl = document.querySelector(
      `#${companyNameFormGroupId}`
    );
    const autocompleteFormGroup =
      companiesHouseAutocompleteTemplate.content.firstElementChild.cloneNode(
        true
      );
    const parent = companyNameFormGroupEl.parentNode;
    parent.insertBefore(autocompleteFormGroup, companyNameFormGroupEl);
    companyNameFormGroupEl.remove();
  };
  replaceCompanyNameFormGroup();

  const fetchCompanies = (query) => {
    const url = `/api/company-search/?q=${query}`;

    return fetch(url)
      .then((response) => response.json())
      .then(({ results }) => results);
  };
  const getInputValue = (selected) => {
    if (typeof selected == "string") {
      return selected;
    }
    return selected?.name ?? "";
  };
  const getSuggestion = (suggestion) => {
    let { name, postcode } = suggestion;
    if (typeof suggestion == "string") {
      name = suggestion;
    }
    if (!postcode) {
      return `<div>${name}</div>`;
    }
    return `<div>${name}</div><div>${postcode}</div>`;
  };

  const companyNumberEl = document.querySelector(
    "#id_business-details-company_registration_number"
  );

  const populateResultValues = (confirmed) => {
    if (!confirmed) {
      return;
    }
    const { companyNumber } = confirmed;
    companyNumberEl.value = companyNumber;
  };

  const MIN_SEARCH_STRING_LENGTH = 3;

  let currentSearch = null;

  const searchCompanies = (query, populateResults) => {
    currentSearch = query;
    fetchCompanies(query).then((companies) => {
      if (currentSearch == query) {
        populateResults(companies);
      }
      return companies;
    });
  };

  const autocompleteId = "companies-house-autocomplete";
  const container = document.querySelector(
    "#companies-house-autocomplete-container"
  );
  accessibleAutocomplete({
    defaultValue: container.dataset["defaultValue"],
    element: container,
    id: autocompleteId,
    source: debounce(searchCompanies, 200, { leading: true }),
    onConfirm: populateResultValues,
    minLength: MIN_SEARCH_STRING_LENGTH,
    name: nameEl.name,
    showNoOptionsFound: false,
    templates: {
      inputValue: getInputValue,
      suggestion: getSuggestion,
    },
  });

  let have_you_exported_before_element = document.getElementById("form-group-business-details-have_you_exported_before")
  let do_you_have_product_element = document.getElementById("form-group-business-details-do_you_have_a_product_you_want_to_export")

  have_you_exported_before_element.addEventListener(
      'change',
      function() {
          let chosen_value = document.querySelector("input[name='business-details-have_you_exported_before']:checked").value;
          if (chosen_value === 'not_exported__ess_experience')
              do_you_have_product_element.style.display = 'block';
          else
              do_you_have_product_element.style.display = 'none';
      },
      false
  );
  do_you_have_product_element.style.display = 'none';


})();
