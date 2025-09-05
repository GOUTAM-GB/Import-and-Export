
function allowOnlyTextAndUppercase(selector) {
  $(selector).on("input", function () {
    let value = $(this).val();
    value = value.replace(/[0-9]/g, "");
    // Convert to uppercase
    $(this).val(value.toUpperCase());
  });
}
allowOnlyTextAndUppercase("#name");
allowOnlyTextAndUppercase("#address");


$.validator.addMethod('filesize', function (value, element, param) {
  // param = size (en bytes) 
  // element = element to validate (<input>)
  // value = value of the element (file name)
  return this.optional(element) || (element.files[0].size <= param)
});

$.validator.addMethod("email_valid", function (value, element) {
  // Regex to check gmail with at least 2 chars after the dot
  return this.optional(element) || /^[a-zA-Z0-9._%+-]+@gmail\.[a-zA-Z]{2,}$/.test(value);
}, "Please enter a valid Gmail address (e.g., example@gmail.com).");



$("#addStudentForm").validate({


  errorElement: 'label',
  rules: {
    name: {
      required: true,
      minlength: 2,
      maxlength: 30
    },
    email: {
      required: true,
      email: true,
      email_valid: true,
      remote: {
        url: checkEmailUrl,
        type: "get",
        data: {
          email: function () {
            return $('#email').val();
          }
        }
      }
    },

    contactNo: {
      required: true,
      minlength: 10,
      maxlength: 10,
      remote: {
        url: checkContactUrl,
        type: "get",
        data: {
          contactNo: function () {
            return $('#contactNo').val();
          }
        }
      }
    },
    college: {
      required: true
    },
    branch: {
      required: true
    },
    address: {
      required: true
    },
    gender: {
      required: true
    },

    profilepic: {
      required: true,
      extension: "jpeg|png|jpg",
      filesize: 2097152 // 1048576 means 1 MB
    },

  },
  messages: {
    name: {
      required: "Please enter your name!",
      minlength: "Please give minimum 2 characters",
      maxlength: "max it should be 30 characters"
    },
    email: {
      required: "Please enter an email!",
      email: "Please enter valid email address.",
      email_valid: "Email must be a Gmail address with a valid domain.",
      remote: "This email is alredy exist."
    },

    contactNo: {
      required: "Please enter mobile number.",
      remote: "This number is alredy there."
    },
    college: {
      required: "Please select college"
    },
    branch: {
      required: "Please select branch"
    },
    address: {
      required: "Please enter your address.."
    },
    gender: {
      required: "You must select a gender."
    },


    profilepic: {
      required: "Please select JPG, PNG, or JPEG.",
      extension: "File must be JPG, PNG, or JPEG not other file allowed",
      filesize: "File size must be less than 2 MB."
    },

  },

  errorPlacement: function (error, element) {
    var fieldName = element.attr("name");
    var $small = $("#" + fieldName + "Error");
    if ($small.length) {

      $small.text(error.text());
    } else {
      error.insertAfter(element);
    }

  }

});
