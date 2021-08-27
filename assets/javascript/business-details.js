import accessibleAutocomplete from "accessible-autocomplete";

const getResults = (query, populateResults) => {
  fetch(`/api/company-search/?q=${query}`)
    .then((response) => response.json())
    .then(({ results }) => results)
    .then((companies) => populateResults(companies));
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

accessibleAutocomplete({
  element: document.querySelector("#companies-house-autocomplete-container"),
  id: "companies-house-autocomplete",
  source: getResults,
  onConfirm: populateResultValues,
  templates: {
    inputValue: getInputValue,
    suggestion: getSuggestion,
  },
});
