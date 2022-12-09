const bottleEditButton = document.querySelector('#bottleEditButton');
const bottleEdit = document.querySelector('#bottleEdit');
const bottleEditStep1 = document.querySelector('#bottleEditStep1');
const bottleEditStep2 = document.querySelector('#bottleEditStep2');
const yearEditButtons = document.querySelectorAll('.yearEditButton');
const yearEdit = document.querySelector('#yearEdit');
const cancelButtons = document.querySelectorAll('.secondaryButton');
const yearEditSend = yearEdit.querySelector('button[type="submit"]');
const videoFileInput = document.querySelector('#videoFileInput');

videoFileInput.addEventListener('change', () => {
    if (videoFileInput.files.length > 0){
        yearEdit.querySelector('button[type="submit"]').disabled = false;
    }else{
        yearEdit.querySelector('button[type="submit"]').disabled = true;
    }
});

yearEditSend.addEventListener('click', e => {
    e.preventDefault();
    let xhr = new XMLHttpRequest();
    xhr.onload = () => {
        if (xhr.readyState === xhr.DONE) {
            if (xhr.status === 200) {
                location.reload(true);

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

bottleEdit.querySelector("button[type='submit']").addEventListener('click', e => {
    e.preventDefault();
    let xhr = new XMLHttpRequest();
    xhr.onload = () => {
        if (xhr.readyState === xhr.DONE) {
            if (xhr.status === 200) {
                location.reload(true);
            }else{
                bottleEdit.querySelector('.loader').classList.add('hidden');
                bottleEdit.querySelector('.error_container').textContent = xhr.response;
                bottleEdit.querySelector('.error_container').classList.remove('hidden');
            }
        }
    }
    xhr.open('post', '/registerCard', true)
    var formData = new FormData();
    formData.append('id', bottleEdit.querySelector('#unregisteredBottleId').value);
    formData.append('year', bottleEdit.querySelector('#unregisteredBottleYear').value);
    bottleEdit.querySelector('.loader').classList.remove('hidden');
    xhr.send(formData);
});

bottleEditButton.addEventListener('click', () => {
    bottleEdit.classList.remove('hidden');
    bottleEditStep1.classList.remove('hidden');
    let request = new XMLHttpRequest();
    request.open('post', '/reqeustForUnregisteredCard', true)
    request.send();
    requestInterval = setInterval(() => {
        let ack = new XMLHttpRequest();
        ack.open('post', '/unregisteredPoll', true)
        ack.onload = () => {
            if (ack.readyState === ack.DONE) {
                if (ack.status === 200) {
                    document.querySelector("#unregisteredBottleId").value = ack.response;
                    bottleEditStep1.classList.add('hidden');
                    bottleEditStep2.classList.remove('hidden');
                    clearInterval(requestInterval)
                }
            }
        };
        ack.send()
    }, 1000);
    bottleEditStep2.classList.add('hidden');
});
yearEditButtons.forEach(year => {
    year.addEventListener('click', () => {
        yearEdit.classList.toggle('hidden');
        if (year.getAttribute('data-year') !== null){
            yearEdit.querySelector('input[type="number"]').value = year.getAttribute('data-year');
            yearEdit.querySelector('#yearWrapper').classList.add('hidden');
        }else{
            yearEdit.querySelector('input[type="number"]').value = '';
            yearEdit.querySelector('#yearWrapper').classList.remove('hidden');
        }
        yearEdit.querySelector('button[type="submit"]').disabled = true;
        yearEdit.querySelector('input[type="file"]').value = '';
    });
})