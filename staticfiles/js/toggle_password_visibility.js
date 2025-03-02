function PasswordVisibility() {
  var passwordFields = ["id_password", "id_password_repeat"]; // IDs of password input fields

  passwordFields.forEach(function (fieldId) {
    var inputField = document.getElementById(fieldId);
    if (inputField) {
      // if the input field is available (id_password_repeat doesn't exist in login.html)
      inputField.type = inputField.type === "password" ? "text" : "password";
    }
  });
}
