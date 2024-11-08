from flask import Flask, render_template, request
import functions



app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/insurance_form')
def insurance_index():
    return render_template('insurance_index.html')

@app.route('/annuity_form')
def annuity_index():
    return render_template('annuity_index.html')

@app.route('/insurance_estimate',
 methods=['POST'])

def estimate_insurance():
    age = int(request.form['age'])
    sex = request.form['sex']
    sex = {'Male': 2, 'Female': 3}[sex]
    state = request.form['state']
    life_table = functions.get_life_table(state = state, sex = sex)
    amount_insured = int(request.form['amount_insured'])
    life_type = request.form['life_type']
    term_length = int(request.form['term_length']) if life_type == 'term' else None



    if life_type == 'term':
        estimate = (functions.death_benefit_value_calculator(life_table, age, period = 365, term = term_length, interest = 0.05) * amount_insured /
                    functions.annuity_calculator_2(life_table, age, term = term_length, period=12, interest=0.05) / 12)

    if life_type == 'whole':
        estimate = (functions.death_benefit_value_calculator(life_table, age, period = 365, interest = 0.05) * amount_insured /
                    functions.annuity_calculator_2(life_table, age, period=12, interest=0.05) / 12)

    estimate = f"{estimate:.2f}"

    return render_template('insurance_results.html', estimate = estimate)

@app.route('/annuity_estimate',
 methods=['POST'])

def estimate_annuity():
    age = int(request.form['age'])
    sex = request.form['sex']
    sex = {'Male': 2, 'Female': 3}[sex]
    state = request.form['state']
    life_table = functions.get_life_table(state = state, sex = sex)
    annuity_amount = int(request.form['annuity_amount'])
    life_type = request.form['life_type']
    term_length = int(request.form['term_length']) if life_type == 'term' else None
    periods = {"Yearly": 1, "Quarterly": 4, "Monthly": 12, "Bi-weekly": 26}[request.form['payment_frequency']]




    if life_type == 'term':
        estimate = (functions.annuity_calculator_2(life_table, age, term = term_length, period=periods, interest=0.05) * annuity_amount)

    if life_type == 'whole':
        estimate = (functions.annuity_calculator_2(life_table, age, period=periods, interest=0.05) * annuity_amount)

    estimate = f"{estimate:.2f}"

    return render_template('annuity_results.html', estimate = estimate)

if __name__ == '__main__':
    app.run(debug=True)