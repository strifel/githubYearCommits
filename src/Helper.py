from flask import make_response
import json


def returnError(status, message):
    resp = make_response(json.dumps({"error": message}))
    resp.headers['Content-Type'] = 'application/json'
    resp.status_code = status
    return resp

