from flask import Flask, render_template, request, redirect, url_for
import json
import os

app = Flask(__name__)

HISTORY_FILE = 'history.json'

GRADE_POINTS = {
    "A": 10,
    "A-": 9,
    "B": 8,
    "B-": 7,
    "C": 6,
    "C-": 5,
    "D": 4,
}

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

    total_credits = 0
    total_grade_points = 0

    # Calculate total credits and grade points
    for course, credit, grade in zip(courses, credits, grades):
        if grade in GRADE_POINTS:
            total_credits += int(credit)
            total_grade_points += int(credit) * GRADE_POINTS[grade]

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

@app.route('/about-us')
def about_us():
    return render_template('about_us.html')

@app.route('/do-or-die', methods=['GET', 'POST'])
def do_or_die_calculator():
    if request.method == 'POST':
        # Extract confirmed grades (courses, credits, grades)
        confirmed_courses = request.form.getlist('confirmed_course')
        confirmed_credits = list(map(int, request.form.getlist('confirmed_credit')))
        confirmed_grades = request.form.getlist('confirmed_grade')

        # Calculate total points from confirmed grades
        total_confirmed_points = sum(
            credit * GRADE_POINTS[grade]
            for credit, grade in zip(confirmed_credits, confirmed_grades)
        )
        total_confirmed_credits = sum(confirmed_credits)

        # Extract unknown courses (courses, credits)
        unknown_courses = request.form.getlist('unknown_course')
        unknown_credits = list(map(int, request.form.getlist('unknown_credit')))
        total_unknown_credits = sum(unknown_credits)

        # Required SGPA
        required_sgpa = float(request.form.get('required_sgpa'))

        # Calculate total points required to achieve the required SGPA
        total_credits = total_confirmed_credits + total_unknown_credits
        total_required_points = required_sgpa * total_credits

        # Calculate points still required from the unknown courses
        points_for_unknown = total_required_points - total_confirmed_points

        # Check if it's even possible to achieve the required SGPA
        max_possible_points = sum(credit * GRADE_POINTS['A'] for credit in unknown_credits)
        if points_for_unknown > max_possible_points:
            error_message = (
                "It's not possible to achieve your goal. Here are two pieces of advice:"
                "<ol>"
                "<li>Once a wise man said, 'Umeed par duniya kayam hai, dil dukha hai lekin tuta to nahi hai, umeed ka daman chuta to nahi hai.'</li>"
                "<li>You can use a popular trick to make this impossible task achievable. "
                "<a href='https://www.amazon.in/Natural-Twisted-Macrame-Camping-Wedding/dp/B08H88DY8J' target='_blank'>Follow this tutorial</a>.</li>"
            )
                
            return render_template('do_or_die_calculator.html', error_message=error_message)
        # Distribute the points across unknown courses
        required_grades = []

        for credit in unknown_credits:
            # Calculate the points per credit for this unknown course
            points_per_credit = points_for_unknown / total_unknown_credits

            # Assign the minimum grade that satisfies the SGPA requirement
            if points_per_credit >= GRADE_POINTS['A']:
                required_grades.append((credit, 'A'))
            elif points_per_credit >= GRADE_POINTS['A-']:
                required_grades.append((credit, 'A-'))
            elif points_per_credit >= GRADE_POINTS['B']:
                required_grades.append((credit, 'B'))
            elif points_per_credit >= GRADE_POINTS['B-']:
                required_grades.append((credit, 'B-'))
            elif points_per_credit >= GRADE_POINTS['C']:
                required_grades.append((credit, 'C'))
            else:
                required_grades.append((credit, 'C-'))

            # Subtract the assigned grade's points from the remaining points for unknown courses
            points_for_unknown -= (GRADE_POINTS[required_grades[-1][1]] * credit)
            total_unknown_credits -= credit

        return render_template('do_or_die_calculator.html', required_grades=required_grades)

    return render_template('do_or_die_calculator.html', required_grades=None)




if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)


