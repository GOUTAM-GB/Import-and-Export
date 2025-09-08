function allowOnlyTextAndUppercase(selector) {
    $(selector).on("input", function () {
      let value = $(this).val();
      value = value.replace(/[0-9]/g, "");
      $(this).val(value.toUpperCase());
    });
  }
  allowOnlyTextAndUppercase("#name");
