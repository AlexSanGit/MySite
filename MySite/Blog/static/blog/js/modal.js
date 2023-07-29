// Открытие модального окна и отображение изображения
function openModal(imageUrl) {
    var modal = document.getElementById("myModal");
    var modalImage = document.getElementById("modalImage");
    modal.style.display = "block";
    modalImage.src = imageUrl;
}

// Закрытие модального окна
function closeModal() {
    var modal = document.getElementById("myModal");
    modal.style.display = "none";
}
