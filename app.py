from flask import Flask, render_template, redirect, request, url_for
from imgpred.fbscraper.webscraper import run_web_scraper
from imgpred.prediction import img_predictions

app = Flask(__name__)


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/fbscraper', methods=['POST', 'GET'])
def fbscraper():
    if request.method == 'POST':
        email = request.form['fbemail']
        password = request.form['fbpassword']
        return redirect(url_for('scrape', fbemail=email, fbpassword=password))
    return render_template('fbscraper_login.html')


@app.route('/scrape')
def scrape():
    email = request.args.get('fbemail')
    password = request.args.get('fbpassword')
    result = run_web_scraper(email, password)
    return redirect(url_for('predictions'))


# @app.route('/predictions')
# def predictions():
#     result = img_predictions()
#     return result

@app.route('/predictions')
def predictions():
    result = img_predictions()
    return render_template('result.html', result=result)


if __name__ == '__main__':
    app.run(debug=True)
