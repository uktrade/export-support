"use strict";

function CookieBanner() {
  var cookiePreferencesName = "cookie_preferences_set";
  var cookiePreferencesDurationDays = 31;

  var cookiesPolicyName = "cookies_policy";
  var cookiesPolicyDurationDays = 365;

  function setCookie(name, value, options) {
    console.log("setCookie", name, value, options);
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
    window.dataLayer.push({ event: "cookies" });
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

  function displayCookieBannerAcceptAll(cookieBannerClassName) {
    var banner = document.querySelector(cookieBannerClassName);
    banner.className =
      banner.className + " app-cookie-banner--show__accepted-all";

    var hideButton = document.querySelector(".hide-button");
    if (hideButton.attachEvent) {
      hideButton.attachEvent("click", function () {
        hideCookieBanner(cookieBannerClassName);
      });
    } else {
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
    if (button.attachEvent) {
      button.attachEvent("onclick", onClickFunction);
    } else {
      button.addEventListener("click", onClickFunction, false);
    }
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

    form[radioButtons.usage].value = policy.usage ? "on" : "off";
    form[radioButtons.settings].value = policy.settings ? "on" : "off";
    form[radioButtons.campaigns].value = policy.campaigns ? "on" : "off";

    var attachEventMethod = form.attachEvent || form.addEventListener;
    attachEventMethod(
      "submit",
      function (e) {
        var settings = form[radioButtons.settings].value === "on";
        var usage = form[radioButtons.usage].value === "on";
        var campaigns = form[radioButtons.campaigns].value === "on";

        createPoliciesCookie(settings, usage, campaigns);
        setPreferencesCookie();

        confirmation.style = "display:block;";
        window.scrollTo(0, 0);

        e.preventDefault();
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

module.exports = CookieBanner;
