document.addEventListener("DOMContentLoaded", function() {
    const year = document.getElementById("copyright")
    const date = new Date()
    year.textContent = date.getFullYear()
})
