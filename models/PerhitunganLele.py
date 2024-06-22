from config.base_model import Model
class PerhitunganLele(Model):
    def __init__(self):
        pass

    @classmethod
    def save(cls, data):
        cls.create(data)
    
    @classmethod
    def delete(cls, id):
        cls.create(id)

    @classmethod
    def delete_all(cls):
        cls.truncate()
    
    @classmethod
    def show_all(cls, arg=None):
        if arg is not None:
           return cls.show(where=arg)
        else:
           return cls.show()