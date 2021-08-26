import accessibleAutocomplete from "accessible-autocomplete";

const companies = [
  { name: "Oscorp", postcode: "W1 2AB", companyNumber: "12345" },
  { name: "Stark Industries", postcode: "E2 3CD", companyNumber: "67890" },
  { name: "Damage Control", postcode: "S3 4EF", companyNumber: "98765" },
];

const getResults = (query, populateResults) => populateResults(companies);
const getInputValue = (selected) => (selected ? selected.name : "");
const getSuggestion = ({ name }) => name;

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
