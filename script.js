const safety_slider = document.getElementById("safety_range")
const safety_output = document.getElementById("safety_span")

safety_output.textContent = safety_slider.value;

safety_slider.addEventListener("input", function () {
    safety_output.textContent = this.value;
});

const lighting_slider = document.getElementById("lighting_range")
const lighting_output = document.getElementById("lighting_span")

lighting_output.textContent = lighting_slider.value;

lighting_slider.addEventListener("input", function () {
    lighting_output.textContent = this.value;
});

const green_slider = document.getElementById("green_range")
const green_output = document.getElementById("green_span")

green_output.textContent = green_slider.value;

green_slider.addEventListener("input", function () {
    green_output.textContent = this.value;
});

const crossings_slider = document.getElementById("crossings_range")
const crossings_output = document.getElementById("crossings_span")

crossings_output.textContent = crossings_slider.value;

crossings_slider.addEventListener("input", function () {
    crossings_output.textContent = this.value;
});