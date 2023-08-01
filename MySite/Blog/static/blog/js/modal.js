// Открытие модального окна и отображение изображения
function openModal(imageUrl) {
    var modal = document.getElementById("myModal");
    var modalImage = document.getElementById("img01");
    modal.style.display = "block";
    modalImage.src = imageUrl;
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
