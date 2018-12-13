from ocdskingfisher.database import get_or_create_collection_id



class Store:

    def __init__(self, config):
        self.config = config
        self.collection_id = None


    def load_collection(self, collection_source, collection_data_version, collection_sample):
        self.collection_id = get_or_create_collection_id(collection_source, collection_data_version, collection_sample)



