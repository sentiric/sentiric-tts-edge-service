document.addEventListener('DOMContentLoaded', () => {
    const ttsForm = document.getElementById('tts-form');
    ttsForm.addEventListener('submit', async function(event) {
        event.preventDefault();

        const form = event.target;
        const formData = new FormData(form);
        
        const resultContainer = document.getElementById('result-container');
        const audioPlayer = document.getElementById('audio-player');
        const errorMessage = document.getElementById('error-message');
        const spinner = document.getElementById('spinner');
        const submitBtn = document.getElementById('submit-btn');

        resultContainer.classList.remove('hidden');
        audioPlayer.src = '';
        audioPlayer.classList.add('hidden');
        errorMessage.classList.add('hidden');
        spinner.classList.remove('hidden');
        submitBtn.disabled = true;
        submitBtn.textContent = 'Sentezleniyor...';

        try {
            // FormData'yı doğrudan gönderiyoruz
            const response = await fetch('/api/v1/synthesize', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`HTTP hatası! Durum: ${response.status} - ${errorText}`);
            }
            
            const audioBlob = await response.blob();
            const audioUrl = URL.createObjectURL(audioBlob);
            audioPlayer.src = audioUrl;
            audioPlayer.classList.remove('hidden');
            audioPlayer.play();
            
        } catch (error) {
            console.error('Sentezleme hatası:', error);
            errorMessage.textContent = `Hata: ${error.message}`;
            errorMessage.classList.remove('hidden');
        } finally {
            spinner.classList.add('hidden');
            submitBtn.disabled = false;
            submitBtn.textContent = 'Sesi Sentezle ve Dinle';
        }
    });
});