from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('test.html', message="Hello from Flask!")

@app.route('/test')
def test():
    return "Simple Flask test works!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5004)