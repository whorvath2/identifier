import uuid


class IdCreator(object):

    def get_new_id(self) -> str:
        return str(uuid.uuid4())
