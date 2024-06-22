def create_model(name):
    model_path = f"models/{name.lower()}.py"
    
    model_template = f"""from config.base_model import Model
class {name}(Model):
    def __init__(self):
        pass

    def save(self):
        # Code to save the model to the database
        pass

    def delete(self):
        # Code to delete the model from the database
        pass

    @staticmethod
    def find_by_id(model_id):
        # Code to find a model by its ID
        pass"""

    with open(model_path, 'w') as model_file:
        model_file.write(model_template)
    print(f"Model created: {model_path}")
