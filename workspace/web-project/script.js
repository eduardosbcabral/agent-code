// JavaScript with intentional bugs for testing

function showMessage() {
    // Missing semicolon and incorrect syntax
    alert("Hello from the website!")
    console.log("Button clicked")
}

// Function with syntax error
function calculateSum(a, b) {
    return a + b
}

// Missing event listener
document.addEventListener('DOMContentLoaded', function() {
    console.log('Page loaded')
    
    // Code with bugs
    const buttons = document.querySelectorAll('button')
    for (let i = 0; i < buttons.length; i++) {
        buttons[i].addEventListener('click', function() {
            // Missing function implementation
        })
    }
})

// Incomplete navigation functionality
function navigateTo(section) {
    // Should scroll to section smoothly
    document.getElementById(section).scrollIntoView()
}

// Form validation function (incomplete)
function validateForm(formData) {
    // Add validation logic here
    return true
}
