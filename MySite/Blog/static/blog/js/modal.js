  // JavaScript для открытия модального окна -->

    // Функция для открытия модального окна с изображением
    function openModal(imageUrl) {
      var modal = document.getElementById('myModal');
      var modalImg = document.getElementById('img01');

      modal.style.display = 'block';
      modalImg.src = imageUrl;
    }

    // Функция для закрытия модального окна
    function closeModal() {
      var modal = document.getElementById('myModal');
      modal.style.display = 'none';
    }

