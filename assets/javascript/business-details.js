import accessibleAutocomplete from "accessible-autocomplete";
import debounce from "lodash.debounce";

const companiesHouseAutocompleteTemplate = document.querySelector(
  "#companies-house-autocomplete-template"
);
const companyNameFormGroupId =
  companiesHouseAutocompleteTemplate.dataset.formGroupId;
const companyNameFormGroupEl = document.querySelector(
  `#${companyNameFormGroupId}`
);
const autocompleteFormGroup =
  companiesHouseAutocompleteTemplate.content.firstElementChild.cloneNode(true);
const parent = companyNameFormGroupEl.parentNode;
parent.insertBefore(autocompleteFormGroup, companyNameFormGroupEl);
companyNameFormGroupEl.style.display = "none";

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

const nameEl = document.querySelector("#id_business-details-company_name");
const companyNumberEl = document.querySelector(
  "#id_business-details-company_registration_number"
);

const populateResultValues = (confirmed) => {
  if (!confirmed) {
    return;
  }
  if (typeof confirmed == "string") {
    nameEl.value = confirmed;
    return;
  }
  const { name, companyNumber } = confirmed;
  nameEl.value = name;
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
  showNoOptionsFound: false,
  templates: {
    inputValue: getInputValue,
    suggestion: getSuggestion,
  },
});

const autocompleteEl = document.querySelector(`#${autocompleteId}`);
autocompleteEl.addEventListener("change", () => {
  nameEl.value = autocompleteEl.value;
});
