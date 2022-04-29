"use strict";

function CookieBanner() {
  var cookiePreferencesName = "cookie_preferences_set";
  var cookiePreferencesDurationDays = 365;

  var cookiesPolicyName = "cookies_policy";
  var cookiesPolicyDurationDays = 365;

  var cookiesAcceptedParam = "cookies-accepted";

  function setCookie(name, value, options) {
    if (typeof options === "undefined") {
      options = {};
    }
    var cookieString = name + "=" + value + "; path=/";
    if (options.days) {
      var date = new Date();
      date.setTime(date.getTime() + options.days * 24 * 60 * 60 * 1000);
      cookieString = cookieString + "; expires=" + date.toGMTString();
    }
    if (document.location.protocol === "https:") {
      cookieString = cookieString + "; Secure";
    }
    document.cookie = cookieString;
  }

  function informGTMOfCookieUpdate() {
    window.dataLayer.push({ event: "cookies" });
    window.dataLayer.push({ event: "gtm.js" });
    window.dataLayer.push({ event: "gtm.dom" });
  }

  function getCookie(name) {
    var nameEQ = name + "=";
    var cookies = document.cookie.split(";");
    for (var i = 0, len = cookies.length; i < len; i++) {
      var cookie = cookies[i];
      while (cookie.charAt(0) === " ") {
        cookie = cookie.substring(1, cookie.length);
      }
      if (cookie.indexOf(nameEQ) === 0) {
        return decodeURIComponent(cookie.substring(nameEQ.length));
      }
    }
    return null;
  }

  function getDefaultPolicy() {
    return {
      essential: true,
      settings: false,
      usage: false,
      campaigns: false,
    };
  }

  function getPolicyOrDefault() {
    var cookie = getCookie(cookiesPolicyName);
    var policy = getDefaultPolicy();
    if (!cookie) return policy;

    try {
      var parsed = JSON.parse(cookie);

      policy.campaigns = parsed.campaigns || false;
      policy.usage = parsed.usage || false;
      policy.settings = parsed.settings || false;
    } catch (e) {
      return policy;
    }

    return policy;
  }

  function createPoliciesCookie(settings, usage, campaigns) {
    var policy = getDefaultPolicy();
    policy.settings = settings || false;
    policy.usage = usage || false;
    policy.campaigns = campaigns || false;
    var json = JSON.stringify(policy);
    setCookie(cookiesPolicyName, json, { days: cookiesPolicyDurationDays });
    return policy;
  }

  function hideCookieBanner(className) {
    var banner = document.querySelector(className);
    banner.className = banner.className.replace(/app-cookie-banner--show/, "");
  }

  function bindCookieBanner(bannerClassName) {
    window.addEventListener("load", function () {
      var urlSearchParams = new URLSearchParams(window.location.search);
      var shouldDisplayCookieBanner =
        !!urlSearchParams.get(cookiesAcceptedParam);

      if (shouldDisplayCookieBanner) {
        displayCookieBanner(bannerClassName);
        displayCookieBannerAcceptAll(bannerClassName);
      }
    });
  }

  function displayCookieBannerAcceptAll(cookieBannerClassName) {
    var banner = document.querySelector(cookieBannerClassName);
    banner.className =
      banner.className + " app-cookie-banner--show__accepted-all";

    var hideButton = document.querySelector(".hide-button");
    hideButton.addEventListener(
      "click",
      function (e) {
        hideCookieBanner(cookieBannerClassName);
        e.preventDefault();
        return false;
      },
      false
    );
  }

  function displayCookieBanner(className) {
    var banner = document.querySelector(className);

    banner.className = banner.className.replace(
      /js--cookie-banner/,
      "app-cookie-banner--show"
    );
  }

  function bindAcceptAllCookiesButton(className, onClickFunction) {
    var button = document.querySelector(className);
    button.addEventListener("click", onClickFunction, false);
  }

  function setPreferencesCookie() {
    setCookie(cookiePreferencesName, "true", {
      days: cookiePreferencesDurationDays,
    });
  }

  function enableCookieBanner(bannerClassName, acceptButtonClassName) {
    displayCookieBanner(bannerClassName);
    bindAcceptAllCookiesButton(acceptButtonClassName, function () {
      createPoliciesCookie(true, true, true);

      setPreferencesCookie();
      informGTMOfCookieUpdate();
      displayCookieBannerAcceptAll(bannerClassName);

      return false;
    });
  }

  function init(bannerClassName, acceptButtonClassName, cookiesPolicyUrl) {
    if (!bannerClassName) {
      throw "Expected bannerClassName";
    }

    var preferenceCookie = getCookie(cookiePreferencesName);
    var isCookiesPage = document.URL.indexOf(cookiesPolicyUrl) !== -1;

    if (!preferenceCookie && !isCookiesPage) {
      enableCookieBanner(bannerClassName, acceptButtonClassName);
    }

    bindCookieBanner(bannerClassName);
  }

  function type(obj, showFullClass) {
    // get toPrototypeString() of obj (handles all types)
    if (showFullClass && typeof obj === "object") {
      return Object.prototype.toString.call(obj);
    }
    if (obj == null) {
      return (obj + "").toLowerCase();
    } // implicit toString() conversion

    var deepType = Object.prototype.toString
      .call(obj)
      .slice(8, -1)
      .toLowerCase();
    if (deepType === "generatorfunction") {
      return "function";
    }

    // Prevent overspecificity (for example, [object HTMLDivElement], etc).
    // Account for functionish Regexp (Android <=2.3), functionish <object> element (Chrome <=57, Firefox <=52), etc.
    // String.prototype.match is universally supported.

    return deepType.match(
      /^(array|bigint|date|error|function|generator|regexp|symbol)$/
    )
      ? deepType
      : typeof obj === "object" || typeof obj === "function"
      ? "object"
      : typeof obj;
  }

  function setRadioButtonValue(radioButtons, value) {
    if (type(radioButtons, true) === "[object HTMLCollection]") {
      for (let i = 0; i < radioButtons.length; i++) {
        const radioButton = radioButtons[i];
        if (value && radioButton.value == "on") {
          radioButton.checked = true;
        } else if (!value && radioButton.value == "off") {
          radioButton.checked = true;
        }
      }

      return;
    }
    radioButtons.value = value ? "on" : "off";
  }

  function getRadioButtonValue(radioButtons) {
    if (type(radioButtons, true) === "[object HTMLCollection]") {
      for (let i = 0; i < radioButtons.length; i++) {
        const radioButton = radioButtons[i];
        if (radioButton.checked) {
          return radioButton.value === "on";
        }
      }
    }

    return radioButtons.value === "on";
  }

  function bindCookiePolicyForm(
    formSelector,
    confirmationSelector,
    radioButtons
  ) {
    if (typeof radioButtons !== "object") {
      throw "expected an object with radio button selectors";
    }

    var form = document.querySelector(formSelector);

    if (!form) {
      throw formSelector + " was not found";
    }

    var confirmation = document.querySelector(confirmationSelector);
    if (!confirmation) {
      throw confirmationSelector + " was not found";
    }

    var policy = getPolicyOrDefault();

    setRadioButtonValue(form[radioButtons.usage], policy.usage);
    setRadioButtonValue(form[radioButtons.settings], policy.settings);
    setRadioButtonValue(form[radioButtons.campaigns], policy.campaigns);

    form.addEventListener(
      "submit",
      function (evt) {
        evt.preventDefault();
        evt.stopPropagation();

        var settings = getRadioButtonValue(form[radioButtons.settings]);
        var usage = getRadioButtonValue(form[radioButtons.usage]);
        var campaigns = getRadioButtonValue(form[radioButtons.campaigns]);

        createPoliciesCookie(settings, usage, campaigns);
        setPreferencesCookie();

        confirmation.style.display = "display:block";
        window.scrollTo(0, 0);

        return false;
      },
      false
    );
  }

  return {
    initBanner: init,
    bindForm: bindCookiePolicyForm,
  };
}

export default CookieBanner;
