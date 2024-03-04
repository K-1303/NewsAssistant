document.getElementById('sendUrlButton').addEventListener('click', function() {
    chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
        const currentUrl = tabs[0].url;

        fetch('http://127.0.0.1:5000/summarize', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ url1: currentUrl })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            console.log('Response from backend:', data);
            // Display the summary on the popup
            document.getElementById('summary').innerText = data.summary;
        })
        .catch(error => {
            console.error('There was a problem with the fetch operation:', error);
        });
    });
});
