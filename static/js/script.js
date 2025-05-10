document.addEventListener('DOMContentLoaded', function() {
    console.log('Скрипт загружен');
    
    
    const inputMethodRadios = document.querySelectorAll('input[name="input_method"]');
    const csvInputSection = document.getElementById('csv-input');
    const manualInputSection = document.getElementById('manual-input');
    
    inputMethodRadios.forEach(radio => {
        radio.addEventListener('change', function() {
            console.log('Выбран метод ввода:', this.value);
            if (this.value === 'csv') {
                csvInputSection.style.display = 'block';
                manualInputSection.style.display = 'none';
                document.getElementById('file').setAttribute('required', 'required');
            } else {
                csvInputSection.style.display = 'none';
                manualInputSection.style.display = 'block';
                document.getElementById('file').removeAttribute('required');
            }
        });
    });

    
    const form = document.getElementById('prediction-form');
    form.addEventListener('submit', function(event) {
        console.log('Попытка отправки формы');
        const inputMethod = document.querySelector('input[name="input_method"]:checked').value;
        
        if (inputMethod === 'csv') {
            const fileInput = document.getElementById('file');
            if (!fileInput.files.length) {
                event.preventDefault();
                alert('Пожалуйста, выберите CSV-файл');
                fileInput.focus();
                console.log('Ошибка: Файл не выбран');
                return;
            }
            console.log('Файл выбран:', fileInput.files[0].name);
        } else {
            console.log('Ручной ввод выбран');
            
            const inputs = manualInputSection.querySelectorAll('input');
            let valid = true;
            inputs.forEach(input => {
                if (!input.value) {
                    valid = false;
                    input.style.borderColor = '#e74c3c';
                    input.focus();
                    console.log(`Ошибка в поле ${input.name}: пустое значение`);
                } else {
                    input.style.borderColor = '#ddd';
                }
            });
            if (!valid) {
                event.preventDefault();
                alert('Пожалуйста, заполните все поля');
                console.log('Ошибка: Некорректные данные в ручном вводе');
            }
        }
    });
});