async function submitSingleQuestion() {
    const question = document.getElementById("questionInput").value;
    const answerChoices = document.getElementById("answerInput").value.split(",").map(choice => choice.trim()); // Split by comma and trim spaces
    const correctAnswer = parseInt(document.getElementById("correctAnswerInput").value);

    if (answerChoices.length < 2) {
        document.getElementById("instruction").innerText = "Please enter at least two answer choices separated by commas.";
        return;
    }

    const response = await fetch('/test_single_question', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ question, answerChoices, correctAnswer })
    });

    const data = await response.json();
    console.log(data);
    document.getElementById("result").innerText = `Score: ${data.score}/${data.totalQuestions}`;
}

async function handleFileUpload(file) {
    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch('/upload_csv', {
            method: 'POST',
            body: formData
        });
        const data = await response.json();
        console.log(data);

        let resultHTML = '';
        if (data.incorrectResponses && data.incorrectResponses.length > 0) {
            resultHTML += '<h3>Incorrect Responses:</h3>';
            data.incorrectResponses.forEach(response => {
                resultHTML += `<p>Question: ${response.question}</p>`;
                resultHTML += `<p>Your Response: ${response.userResponse}</p>`;
                resultHTML += `<p>Correct Answer: ${response.correctAnswer}</p>`;
            });
        }
        resultHTML += `<h3>Overall Score: ${data.score}/${data.totalQuestions}</h3>`;
        document.getElementById("result").innerHTML = resultHTML;
    } catch (error) {
        console.error('Error uploading file:', error);
    }
}

function handleFileInputChange(event) {
    const file = event.target.files[0];
    if (file) {
        handleFileUpload(file);
    }
}
document.getElementById('fileInput').addEventListener('change', handleFileInputChange);
