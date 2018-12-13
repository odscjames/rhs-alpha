
class Store:

    def __init__(self, config, database):
        self.config = config
        self.collection_id = None
        self.database = database


    def load_collection(self, collection_source, collection_data_version, collection_sample):
        self.collection_id = self.database.get_or_create_collection_id(collection_source, collection_data_version, collection_sample)



