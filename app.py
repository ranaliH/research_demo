from flask import Flask, render_template, redirect, request, url_for
from imgpred.fbscraper.webscraper import run_web_scraper
from imgpred.igscraper.ig_scraper import scrape_instagram_and_upload_to_blob
from imgpred.prediction import img_predictions, connection_string, container_name

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


@app.route('/scrape', methods=['POST', 'GET'])
def scrape_fb():
    email = request.args.get('fbemail')
    password = request.args.get('fbpassword')
    result = run_web_scraper(email, password)
    return redirect(url_for('predictions'))


@app.route('/predictions')
def predictions_fb():
    result = img_predictions()
    return render_template('result.html', result=result)


@app.route('/igscraper', methods=['POST', 'GET'])
def igscraper():
    if request.method == 'POST':
        username = request.form['igusername']
        password = request.form['igpassword']
        return redirect(url_for('scrapeig', igusername=username, igpassword=password))
    return render_template('igscraper_login.html')


@app.route('/scrapeig', methods=['POST', 'GET'])
def scrapeig():
    username = request.args.get('igusername')
    password = request.args.get('igpassword')
    result = scrape_instagram_and_upload_to_blob(username, password)
    return redirect(url_for('predictions_ig'))


@app.route('/predictions_ig')
def predictions_ig():
    result = img_predictions()
    return render_template('result.html', result=result)


if __name__ == '__main__':
    app.run(debug=True)
