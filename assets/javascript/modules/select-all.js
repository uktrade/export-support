const allChecked = (inputs) => inputs.every((input) => input.checked);

const initSelectAll = () => {
  const selectAllWrappers = document.querySelectorAll(
    "[data-module=select-all]"
  );

  selectAllWrappers.forEach((selectAllWrapper) => {
    const selectAllID = selectAllWrapper.getAttribute("data-select-all-id");
    const selectAllInput = selectAllWrapper.querySelector(`#${selectAllID}`);

    const allInputs = selectAllWrapper.querySelectorAll("input[type=checkbox]");
    const otherInputs = Array.from(allInputs).filter(
      (input) => input != selectAllInput
    );

    selectAllInput.checked = allChecked(otherInputs);

    selectAllInput.addEventListener("change", () => {
      otherInputs.forEach((input) => {
        input.checked = selectAllInput.checked;
      });
    });

    otherInputs.forEach((otherInput) => {
      otherInput.addEventListener("change", () => {
        selectAllInput.checked = allChecked(otherInputs);
      });
    });
  });
};

export default initSelectAll;
