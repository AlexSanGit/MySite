
    // Функция для обработки клика на родительскую категорию
    function toggleChildren(categoryId) {
        var childrenList = document.getElementById('children-list-' + categoryId);
        if (childrenList.style.display === 'none') {
            childrenList.style.display = 'block';
        } else {
            childrenList.style.display = 'none';
        }
    }




