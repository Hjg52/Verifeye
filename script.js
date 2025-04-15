document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('verify-form');
    const resultBox = document.querySelector('.result-box');

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const url = form.querySelector('input[name="username"]').value;
        const advanced = document.getElementById('advanced-toggle-checkbox').checked;

        resultBox.style.display = "block"; // Show result box on submit
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
