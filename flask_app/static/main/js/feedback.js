document.addEventListener("DOMContentLoaded", function() {
    const toggleFeedbackButton = document.getElementById("toggle-feedback-button");
    const feedbackFormContainer = document.getElementById("feedback-form-container");
  
    toggleFeedbackButton.addEventListener("click", function() { // click event
      feedbackFormContainer.classList.toggle("hidden");
    });
  });
  