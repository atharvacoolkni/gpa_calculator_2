from flask import Flask, render_template, request, redirect, url_for
import json
import os

app = Flask(__name__)

HISTORY_FILE = 'history.json'


# Utility functions to load and save history
def load_history():
    if not os.path.exists(HISTORY_FILE):
        return []  # Return empty list if file doesn't exist
    with open(HISTORY_FILE, 'r') as file:
        return json.load(file)


def save_history(data):
    with open(HISTORY_FILE, 'w') as file:
        json.dump(data, file, indent=4)


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/calculate', methods=['POST'])
def calculate():
    courses = request.form.getlist("course")
    credits = request.form.getlist("credit")
    grades = request.form.getlist("grade")

    # Grade point mapping
    grade_points = {'A': 10, 'A-': 9, 'B': 8, 'B-': 7, 'C': 6, 'C-': 5, 'D': 4}

    total_credits = 0
    total_grade_points = 0

    # Calculate total credits and grade points
    for course, credit, grade in zip(courses, credits, grades):
        total_credits += int(credit)
        total_grade_points += int(credit) * grade_points.get(grade, 0)

    # Calculate SGPA
    sgpa = total_grade_points / total_credits if total_credits != 0 else 0
    sgpa = round(sgpa, 2)

    # Save to history
    course_data = {
        'courses': [{'course': course, 'credit': credit, 'grade': grade} for course, credit, grade in zip(courses, credits, grades)],
        'sgpa': sgpa
    }
    history_data = load_history()
    history_data.append(course_data)
    history_data = history_data[-3:]  # Keep only the last 3 entries
    save_history(history_data)

    return render_template("index.html", sgpa=sgpa)


@app.route('/history')
def history():
    history_data = load_history()
    return render_template("history.html", history=history_data)


if __name__ == '__main__':
 



    


    app.run(host = '0.0.0.0' , debug=True)

