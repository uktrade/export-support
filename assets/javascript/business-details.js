import accessibleAutocomplete from "accessible-autocomplete";
import debounce from "lodash.debounce";

let currentSearch = null;

const getResults = (query, populateResults) => {
  const url = `/api/company-search/?q=${query}`;
  currentSearch = url;
  fetch(url)
    .then((response) => response.json())
    .then(({ results }) => results)
    .then((companies) => {
      if (url != currentSearch) {
        return;
      }
      populateResults(companies);
    });
};
const getInputValue = (selected) => (selected ? selected.name : "");
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
  const { name, postcode, companyNumber } = confirmed;
  nameEl.value = name;
  postcodeEl.value = postcode;
  companyNumberEl.value = companyNumber;
};

const MIN_SEARCH_STRING_LENGTH = 3;

accessibleAutocomplete({
  element: document.querySelector("#companies-house-autocomplete-container"),
  id: "companies-house-autocomplete",
  source: debounce(getResults, 200, { leading: true }),
  onConfirm: populateResultValues,
  minLength: MIN_SEARCH_STRING_LENGTH,
  showNoOptionsFound: false,
  templates: {
    inputValue: getInputValue,
    suggestion: getSuggestion,
  },
});
