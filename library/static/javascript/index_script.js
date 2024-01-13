let slideIndex = 1;

document.addEventListener("DOMContentLoaded", function() {
    const images = document.querySelectorAll(".image_gallery img");
    const gallery = document.querySelector(".image_gallery");
    let index = 0;

    function changeImage() {
        images.forEach(img => img.classList.remove("active"));
        images[index].classList.add("active");
        index = (index + 1) % images.length;
    }

    function adjustGalleryHeight() {
        gallery.style.height = images[index].clientHeight + "px";
    }
    setInterval(changeImage, 4000);
    setInterval(adjustGalleryHeight, 1);

    gallery.style.height = images[0].clientHeight + "px";
    images[0].classList.add("active");
    index += 1;

    showSlides(1);

});

function showSlides(n) {
    let i;
    let slides = document.getElementsByClassName("slides");
    let dots = document.getElementsByClassName("dot");
    if (n > slides.length) {slideIndex = 1}
    if (n < 1) {slideIndex = slides.length}
    for (i = 0; i < slides.length; i++) {
        slides[i].style.display = "none";
    }
    for (i = 0; i < dots.length; i++) {
        dots[i].className = dots[i].className.replace(" active", "");
    }
    slides[slideIndex-1].style.display = "block";
    dots[slideIndex-1].className += " active";
}

function plusSlides(n) {
    showSlides(slideIndex += n);
}

function currentSlide(n) {
    showSlides(slideIndex = n);
}

