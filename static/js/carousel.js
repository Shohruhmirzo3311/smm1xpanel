// Karuselni avtomatik o'zgartirish
document.addEventListener("DOMContentLoaded", function() {
    var carousel = document.getElementById('carouselExampleDark');
    var carouselInstance = new bootstrap.Carousel(carousel, {
        interval: 200, // Slaydlar orasidagi vaqt (milisekundlarda)
        wrap: true // Karusel tugaganidan keyin qaytadan boshlanadi
    });
});
