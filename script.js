const safety_slider = document.getElementById("safety_range")
const safety_output = document.getElementById("safety_span")

safety_output.textContent = safety_slider.value;

safety_slider.addEventListener("input", function () {
    safety_output.textContent = this.value;
});