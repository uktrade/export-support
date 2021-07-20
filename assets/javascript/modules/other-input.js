const toggleInputWrapper = (checkbox, wrapper) => {
  const isChecked = checkbox.checked;

  wrapper.classList.toggle("other-form-option__text-input--visible", isChecked);
  wrapper.classList.toggle(
    "other-form-option__text-input--not-visible",
    !isChecked
  );
};

const initOtherInput = () => {
  const otherInputWrappers = document.querySelectorAll(
    "[data-module=other-input]"
  );

  otherInputWrappers.forEach((otherInputWrapper) => {
    const checkboxId = otherInputWrapper.getAttribute(
      "data-other-input-checkbox-id"
    );
    const checkbox = document.querySelector(`#${checkboxId}`);

    const textInputWrapperId = otherInputWrapper.getAttribute(
      "data-other-input-text-input-wrapper-id"
    );
    const textInputWrapper = document.querySelector(`#${textInputWrapperId}`);

    toggleInputWrapper(checkbox, textInputWrapper);

    checkbox.addEventListener("change", (evt) => {
      toggleInputWrapper(checkbox, textInputWrapper);
    });
  });
};

export default initOtherInput;
