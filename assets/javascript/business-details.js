import accessibleAutocomplete from "accessible-autocomplete";

const companies = ["Oscorp", "Stark Industries", "Damage Control"];

accessibleAutocomplete({
  element: document.querySelector("#companies-house-autocomplete-container"),
  id: "companies-house-autocomplete",
  source: companies,
});
