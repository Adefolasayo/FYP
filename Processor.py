from flask import Flask, request, jsonify
import os
print(os.urandom(24))

app = Flask(__name__)

