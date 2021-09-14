import accessibleAutocomplete from "accessible-autocomplete";
import debounce from "lodash.debounce";

const fetchCompanies = (query) => {
  const url = `/api/company-search/?q=${query}`;

  return fetch(url)
    .then((response) => response.json())
    .then(({ results }) => results);
};
const getInputValue = (selected) => selected?.name ?? "";
const getSuggestion = ({ name, postcode }) => {
  if (!postcode) {
    return `<div>${name}</div>`;
  }
  return `<div>${name}</div><div>${postcode}</div>`;
};

const nameEl = document.querySelector("#id_business-details-company_name");
const postcodeEl = document.querySelector(
  "#id_business-details-company_post_code"
);
const companyNumberEl = document.querySelector(
  "#id_business-details-company_registration_number"
);

const populateResultValues = (confirmed) => {
  if (!confirmed) {
    return;
  }
  const { postcode, companyNumber } = confirmed;
  postcodeEl.value = postcode;
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
accessibleAutocomplete({
  element: document.querySelector("#companies-house-autocomplete-container"),
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
