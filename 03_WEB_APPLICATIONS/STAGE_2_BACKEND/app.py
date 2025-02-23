from flask import Flask, request

app = Flask(__name__)

@app.route('/append_hello', methods=['POST'])
def append_hello():
    text = request.form.get('text', '')
    result = text + "Hello"
    return result

if __name__ == '__main__':
    app.run(debug=True)