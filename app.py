from flask import Flask, render_template, request, jsonify
import csv
from hip_agent import HIPAgent

app = Flask(__name__)
agent = HIPAgent()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload_csv', methods=['POST'])
def upload_csv():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"})

    file = request.files['file']

    if file.filename == '':
        return jsonify({"error": "No selected file"})

    if file and allowed_file(file.filename):
        # Save the uploaded file to a temporary location
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # Parse the CSV file
        with open(file_path, "r") as csvfile:
            reader = csv.reader(csvfile, delimiter=",")
            headers = next(reader)
            data = list(reader)

        # Get the correct answers
        correct_answers = []

        # Get the user's responses
        user_responses = []
        incorrect_responses = []
        for row in data:
            answer_choices = [row[headers.index("answer_0")],
                              row[headers.index("answer_1")],
                              row[headers.index("answer_2")],
                              row[headers.index("answer_3")]]
            correct_answer = int(row[headers.index("correct")])
            correct_answers.append(correct_answer)
            response = agent.get_response(row[headers.index("question")], answer_choices)
            user_responses.append(response)
            if response != correct_answer:
                incorrect_responses.append({
                    "question": row[headers.index("question")],
                    "userResponse": response,
                    "correctAnswer": correct_answer
                })

        # Calculate the score
        score = sum(1 for i in range(len(data)) if user_responses[i] == correct_answers[i])
        total_questions = len(data)

        # Delete the temporary file
        os.remove(file_path)

        # Return only incorrect responses and overall score
        return jsonify({"score": score, "totalQuestions": total_questions, "incorrectResponses": incorrect_responses})

    else:
        return jsonify({"error": "Invalid file type"})


@app.route('/test_single_question', methods=['POST'])
def test_single_question():
    data = request.json
    question = data.get("questionInput", "")
    answer_choices = data.get("answerInput", [])
    answer_choices = answer_choices.split(",")
    correct_answer = data.get("correctAnswerInput", "")

    if len(answer_choices) < 2:
        return jsonify({"error": "Please enter at least two answer choices separated by commas."})
    if not correct_answer:
        return jsonify({"error": "Correct answer index missing."})

    if question and answer_choices:
        try:
            correct_answer_index = int(correct_answer)
            if correct_answer_index < 0 or correct_answer_index >= len(answer_choices):
                return jsonify({"error": "Correct answer index out of range."})
        except ValueError:
            return jsonify({"error": "Correct answer index must be an integer."})

        response = agent.get_response(question, answer_choices)
        print(response)
        score = 1 if response == correct_answer_index else 0
        return jsonify({"score": score, "totalQuestions": 1})
    else:
        return jsonify({"error": "Question or answer choices missing"})

if __name__ == "__main__":
    app.run(debug=True)
