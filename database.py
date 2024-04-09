# Copyright 2024 Jacques Berger
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


import sqlite3


def _build_entreprise(result_set_item):
    entreprise = {}
    entreprise["id"] = result_set_item[0]
    entreprise["nom"] = result_set_item[1]
    return entreprise

def _build_interaction(result_set_item):
    interaction = {}
    interaction["id"] = result_set_item[0]
    interaction["moment"] = result_set_item[1]
    interaction["description"] = result_set_item[2]
    return interaction


class Database:
    def __init__(self):
        self.connection = None

    def get_connection(self):
        if self.connection is None:
            self.connection = sqlite3.connect('db/minimal.db')
        return self.connection

    def disconnect(self):
        if self.connection is not None:
            self.connection.close()

    def get_entreprises(self):
        cursor = self.get_connection().cursor()
        query = ("select id, nom from entreprise")
        cursor.execute(query)
        all_data = cursor.fetchall()
        return [_build_entreprise(item) for item in all_data]

    def get_entreprise(self, entreprise_id):
        cursor = self.get_connection().cursor()
        query = ("select id, nom from entreprise where id = ?")
        cursor.execute(query, (entreprise_id,))
        item = cursor.fetchone()
        if item is None:
            return item
        else:
            return _build_entreprise(item)

    def add_entreprise(self, nom):
        connection = self.get_connection()
        query = ("insert into entreprise(nom) values(?)")
        connection.execute(query, (nom,))
        cursor = connection.cursor()
        cursor.execute("select last_insert_rowid()")
        lastId = cursor.fetchone()[0]
        connection.commit()
        return lastId

    def get_interactions(self, entreprise_id):
        cursor = self.get_connection().cursor()
        query = ("select id, moment, description from interaction where entreprise_id = ?")
        cursor.execute(query, (entreprise_id,))
        all_data = cursor.fetchall()
        return [_build_interaction(item) for item in all_data]

    def add_interaction(self, moment, description, entreprise_id):
        connection = self.get_connection()
        query = ("insert into interaction(moment, description, entreprise_id) values(?,?,?)")
        connection.execute(query, (moment, description, entreprise_id,))
        cursor = connection.cursor()
        cursor.execute("select last_insert_rowid()")
        lastId = cursor.fetchone()[0]
        connection.commit()
        return lastId
