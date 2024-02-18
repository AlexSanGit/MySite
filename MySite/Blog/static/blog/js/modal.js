    var currentSlide = 0;

function openModal(imageUrl, index) {
    currentSlide = index;
    document.getElementById('myModal').style.display = 'block';
    showSlide(currentSlide, imageUrl);
}

// Закрытие модального окна
function closeModal() {
    var modal = document.getElementById("myModal");
    modal.style.display = "none";
    console.log("Closing modal...");
    }

// Обработчик события "click" на документе
document.addEventListener("click", function(event) {
    var modal = document.getElementById("myModal");
    var modalContent = document.querySelector(".modal-content");
    var sliderContent = document.querySelector(".slider-content");

    console.log("Clicked target:", event.target);

    // Проверяем, произошел ли клик вне модального окна и не на изображении или кнопках переключения
    if (event.target === modal && event.target !== modalContent && event.target !== sliderContent && !event.target.closest('.slider-controls') && !event.target.closest('.slider-content')) {
        console.log("Closing modal...");
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