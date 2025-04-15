document.addEventListener('DOMContentLoaded', () => {
    const form = document.querySelector('form');
    const resultBox = document.createElement('div');
    resultBox.className = 'result-box';
    document.body.appendChild(resultBox);

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const url = form.querySelector('input[name="username"]').value;
        const advanced = document.getElementById('advanced-toggle-checkbox').checked;

        resultBox.innerHTML = "🔍 Analyzing... Please wait.";

        try {
            const response = await fetch('/verify', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ url, advanced })
            });

            const result = await response.text();
            resultBox.innerHTML = result;
        } catch (error) {
            resultBox.innerHTML = "❌ Error fetching analysis. Please try again.";
            console.error(error);
        }
    });
});
