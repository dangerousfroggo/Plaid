from ast import literal_eval
import flask
from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask import jsonify
import flask_wtf
import googlemaps
import pandas as pd  
from pprint import pprint
from openai import OpenAI
import os
import math
from flask_wtf import FlaskForm, CSRFProtect
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length
import requests