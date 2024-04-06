# Copyright 2024 <Votre nom et code permanent>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from flask import Flask
from flask import redirect
from flask import render_template
from flask import request
from flask import g
from .database import Database

app = Flask(__name__, static_url_path="", static_folder="static")


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        g._database = Database()
    return g._database


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.disconnect()


@app.route('/')
def landing_page():
    return redirect('/entreprises')


@app.route('/entreprises')
def entreprises_liste():
    all_entreprises = get_db().get_entreprises()
    all_entreprises.sort(key=sort_entreprises)
    return render_template('entreprises.html', entreprises=all_entreprises)


@app.route('/nouvelle-entreprise', methods=["GET", "POST"])
def entreprise_add():
    if request.method == "GET":
        return render_template('entreprise-edit.html')
    else:
        validation_result = validate_entreprise(request.form)
        if validation_result["is_valid"]:
            get_db().add_entreprise(request.form["nom"])
            return redirect('/entreprises')
        else:
            return render_template('entreprise-edit.html', result=validation_result)


def sort_entreprises(properties):
    return properties["nom"]


def validate_entreprise(entreprise):
    result = {}
    result["is_valid"] = True
    result["global_errors"] = []
    
    if "nom" not in entreprise or len(entreprise["nom"]) == 0:
        result["is_valid"] = False
        result["global_errors"].append("Le nom d'entreprise est obligatoire.")

    return result
