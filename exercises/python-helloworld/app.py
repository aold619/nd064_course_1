from flask import Flask, json, request
import logging

app = Flask(__name__)


@app.route("/")
def hello():
    return "Hello World!"


@app.route("/status")
def status():
    response = app.response_class(
        response=json.dumps({"result": "OK - healthy"}),
        status=200,
        mimetype="application/json"
    )

    app.logger.info("Status request successfull")

    return response


@app.route("/metrics")
def metrics():
    response = app.response_class(
        response=json.dumps({"status": "success", "code": 0, \
            "data": {"UserCount": 140, "UserCountActive": 23}}),
        status=200,
        mimetype="application/json"
    )

    app.logger.info("Metrics request successfull")
    
    return response


@app.errorhandler(404)
def page_not_found(e):
    app.logger.warning("Error Access: {path}".format(path=request.path))
    return "404 PAGE NOT FOUND"


if __name__ == "__main__":
    logging.basicConfig(filename="app.log", level=logging.DEBUG)
    app.run(host='0.0.0.0', debug=True)

