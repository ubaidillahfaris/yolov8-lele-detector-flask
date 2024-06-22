def create_controller(name):
    controller_path = f"app/controllers/{name}_controller.py"
    
    controller_template = f"""from flask import Flask, jsonify, request
class {name.capitalize()}Controller:
    def index(self):
        # Code to fetch all records
        pass

    def show(self, id):
        # Code to fetch a single record by ID
        pass

    def store(self):
        # Code to store a new record
        pass

    def update(self, id):
        # Code to update a record by ID
        pass

    def delete(self, id):
        # Code to delete a record by ID
        pass
"""
    with open(controller_path, 'w') as controller_file:
        controller_file.write(controller_template)
    print(f"Controller created: {controller_path}")