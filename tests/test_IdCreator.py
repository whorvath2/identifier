from api.services.IdCreator import IdCreator


def test_get_new_id():
    creator = IdCreator()
    new_id = creator.get_new_id()
    assert new_id is not None
