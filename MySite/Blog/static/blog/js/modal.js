// Открытие модального окна и отображение изображения
//function openModal(imageUrl) {
//    var modal = document.getElementById("myModal");
//    var modalImage = document.getElementById("img01");
//    modal.style.display = "block";
//    modalImage.src = imageUrl;
//}
//
//// Закрытие модального окна
//function closeModal() {
//    var modal = document.getElementById("myModal");
//    modal.style.display = "none";
//}
//
//// Обработчик события "click" на документе
//document.addEventListener("click", function(event) {
//    var modal = document.getElementById("myModal");
//    var modalContent = document.querySelector(".modal-content");
//    // Проверяем, произошел ли клик вне модального окна
//    if (event.target === modal && event.target !== modalContent) {
//        closeModal();
//    }
//});

    var currentSlide = 0;

function openModal(imageUrl) {
    currentSlide = 0;
    document.getElementById('myModal').style.display = 'block';
    showSlide(currentSlide, imageUrl);
}

// Закрытие модального окна
function closeModal() {
    var modal = document.getElementById("myModal");
    modal.style.display = "none";
    }

    // Обработчик события "click" на документе
document.addEventListener("click", function(event) {
    var modal = document.getElementById("myModal");
    var modalContent = document.querySelector(".modal-content");
    // Проверяем, произошел ли клик вне модального окна
    if (event.target === modal && event.target !== modalContent) {
        closeModal();
    }
});

function prevSlide() {
    currentSlide--;
    showSlide(currentSlide);
}

function nextSlide() {
    currentSlide++;
    showSlide(currentSlide);
}

function showSlide(index, imageUrl) {
    var slides = document.querySelectorAll('.slider-content img');
    if (index < 0) {
        currentSlide = slides.length - 1;
    } else if (index >= slides.length) {
        currentSlide = 0;
    }
    for (var i = 0; i < slides.length; i++) {
        slides[i].style.display = 'none';
    }
    slides[currentSlide].style.display = 'block';

    // Если imageUrl определено, используйте его
    if (imageUrl) {
        slides[currentSlide].src = imageUrl;
    }
}