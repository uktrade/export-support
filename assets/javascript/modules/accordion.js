import GDSAccordion from "govuk-frontend/govuk/components/accordion/accordion";

class Accordion extends GDSAccordion {
  constructor($module) {
    super($module);
    this.openAllSectionDescription = $module.dataset.openAllSectionDescription;
  }

  updateOpenAllButton(expanded) {
    var newButtonText = expanded ? "Close all" : "Open all";
    var sectionsText = this.openAllSectionDescription
      ? ` on ${this.openAllSectionDescription}`
      : "";
    newButtonText += `<span class="govuk-visually-hidden"> sections${sectionsText}</span>`;
    this.$openAllButton.setAttribute("aria-expanded", expanded);
    this.$openAllButton.innerHTML = newButtonText;
  }
}

export default Accordion;
