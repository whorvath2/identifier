from api.services.IdCreator import IdCreator


def test_get_new_id(mock_id_repository_writer):
    creator = IdCreator(id_repository=mock_id_repository_writer)
    new_id = creator.get_new_id()
    assert new_id is not None
