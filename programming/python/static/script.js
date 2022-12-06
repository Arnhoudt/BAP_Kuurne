const bottleEditButton = document.querySelector('#bottleEditButton');
const bottleEdit = document.querySelector('#bottleEdit');
const bottleEditStep1 = document.querySelector('#bottleEditStep1');
const bottleEditStep2 = document.querySelector('#bottleEditStep2');
const yearEditButtons = document.querySelectorAll('.yearEditButton');
const yearEdit = document.querySelector('#yearEdit');
const cancelButtons = document.querySelectorAll('.secondaryButton');
const yearEditSend = yearEdit.querySelector('input[type="submit"]');
yearEditSend.addEventListener('click', e => {
    e.preventDefault();
    let xhr = new XMLHttpRequest();
    xhr.onload = () => {
        if (xhr.readyState === xhr.DONE) {
            if (xhr.status === 200) {
                console.log(xhr.response);
                yearEdit.querySelector('.loader').classList.add('hidden');
                yearEdit.classList.add('hidden');
            }else{
                yearEdit.querySelector('.loader').classList.add('hidden');
                yearEdit.querySelector('.error_container').textContent = xhr.response;
                yearEdit.querySelector('.error_container').classList.remove('hidden');
            }
        }
    };
    xhr.open('post', '/video', true)
    var formData = new FormData();
    formData.append('year', yearEdit.querySelector('input[type="number"]').value);
    formData.append('file', yearEdit.querySelector('input[type="file"]').files[0]);
    yearEdit.querySelector('.loader').classList.remove('hidden');
    xhr.send(formData);
});
cancelButtons.forEach(button => {
    button.addEventListener('click', e => {
        e.preventDefault()
        document.querySelectorAll('.popup').forEach(popup => {
            if (popup.querySelector('.secondaryButton') === button){
                popup.classList.add('hidden');
            }
        });
    });
});
bottleEditButton.addEventListener('click', () => {
    bottleEdit.classList.toggle('hidden');
    bottleEditStep1.classList.toggle('hidden');
    bottleEditStep2.classList.toggle('hidden');
});
yearEditButtons.forEach(year => {
    year.addEventListener('click', () => {
        yearEdit.classList.toggle('hidden');
    });
})