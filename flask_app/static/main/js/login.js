let failedAttempts = 0;
    
    $("#login-form").on("submit", function(event) {
        event.preventDefault(); // Prevent default form submission behavior

        const data = {
            email: $("#email").val(),
            password: $("#password").val()
        };

        $.ajax({
            url: "/processlogin",
            type: "POST",
            data: data,
            success: function(response) {
                const result = JSON.parse(response);

                if (result.success) {
                    // Redirect to /home if login is successful
                    window.location.href = "/home";
                } else {
                    // Increment failed attempts and show the error message
                    failedAttempts++;
                    $("#attempt-count").text(failedAttempts);
                    $("#error-message").removeClass("hidden");
                }
            },
            error: function(xhr, status, error) {
                console.error("Error during AJAX request:", error);
            }
        });
    });

    // Change this to click event on the signup button
    $(".signup-button").on("click", function(event) {
        event.preventDefault(); // Prevent default form submission behavior

        const data = {
            email: $("#email").val(),
            password: $("#password").val()
        };

        $.ajax({
            url: "/processsignup",
            type: "POST",
            data: data,
            success: function(response) {
                const result = JSON.parse(response);

                if (result.success) {
                    // Let user know user has been created
                    alert("User Created");
                    window.location.href = "/login";
                } else {
                    // Let user know user has NOT been created
                    console.log("RESULT: ", result);
                    alert(result.message);
                }
            },
            error: function(xhr, status, error) {
                console.error("Error during AJAX request:", error);
            }
        });
    });