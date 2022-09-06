import common from "govuk-frontend/govuk/common";
import Button from "govuk-frontend/govuk/components/button/button";
import ErrorSummary from "govuk-frontend/govuk/components/error-summary/error-summary";
import Radios from "govuk-frontend/govuk/components/radios/radios";

import Accordion from "./modules/accordion";

import initSelectAll from "./modules/select-all";
import initLocationFilter from "./modules/location-filter";
import CookiePolicy from "./modules/cookie-banner";

var cookiePolicy = new CookiePolicy();
cookiePolicy.initBanner(".app-cookie-banner", ".js-accept-cookie", "cookies");

var nodeListForEach = common.nodeListForEach;

// accessibility feature
var $buttons = document.querySelectorAll('[data-module="govuk-button"]');
nodeListForEach($buttons, function ($button) {
  new Button($button).init();
});

var $accordions = document.querySelectorAll('[data-module="govuk-accordion"]');
nodeListForEach($accordions, function ($accordion) {
  new Accordion($accordion).init();
});

var $radios = document.querySelectorAll('[data-module="govuk-radios"]');
nodeListForEach($radios, function ($radio) {
  new Radios($radio).init();
});

var $errorSummaries = document.querySelectorAll(
  '[data-module="govuk-error-summary"]'
);
nodeListForEach($errorSummaries, function ($errorSummary) {
  var errorSummary = new ErrorSummary($errorSummary);
  errorSummary.init = function () {
    this.$module.addEventListener(
      "click",
      ErrorSummary.prototype.handleClick.bind(this)
    );
  };
  errorSummary.init();
});

initSelectAll();
initLocationFilter();
