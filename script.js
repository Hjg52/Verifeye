document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('verify-form');
    const resultBox = document.querySelector('.result-box');

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        let url = form.querySelector('input[name="username"]').value.trim();
        const advanced = document.getElementById('advanced-toggle-checkbox').checked;

        // Auto-prepend https:// if missing
        if (!/^https?:\/\//i.test(url)) {
            url = 'https://' + url;
        }

        resultBox.style.display = "block";
        resultBox.innerHTML = "🔍 Analyzing... Please wait.";

        try {
            const response = await fetch('/verify', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ url, advanced })
            });

            const data = await response.json();
            resultBox.innerHTML = data.result;
        } catch (error) {
            resultBox.innerHTML = "❌ Error fetching analysis. Please try again.";
            console.error(error);
        }
    });
});
