/*
 * This function toggles the disabled state of both fields.
 * If a user has selected an option from the drop-down menu,
 * the text field is disabled. If the user has typed in the text field,
 * the drop-down menu becomes disabled.
 */
function toggleFields() {
    const selectTopic = document.getElementById('topic');
    const customTopic = document.getElementById('custom-topic');

    // If the drop-down has a valid choice (not empty), disable the text field
    if (selectTopic.value !== "") {
        customTopic.disabled = true;
    } else {
        customTopic.disabled = false;
    }

    // If the text field has content, disable the drop-down
    if (customTopic.value.trim() !== "") {
        selectTopic.disabled = true;
    } else {
        selectTopic.disabled = false;
    }
}