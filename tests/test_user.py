from datetime import datetime

import mock
import pytest
from dmutils.user import user_has_role, user_logging_string, User


@pytest.fixture
def user():
    return User(123, 'test@example.com', 321, 'test supplier', False, True, 'Name', 'supplier', datetime(2016, 1, 1), 5)


@pytest.fixture
def user_json():
    return {
        "users": {
            "id": 123,
            "emailAddress": "test@example.com",
            "name": "name",
            "role": "supplier",
            "locked": False,
            "active": True,
            "supplier": {
                "supplierCode": 321,
                "name": "test supplier",
            },
            "termsAcceptedAt": "2016-01-01T01:00:00.0+00:00",
            "application": {
                "application_id": 5
            }
        }
    }


def test_logging_string(user):
    result = user_logging_string(user)
    assert result
    assert 'id=123' in result
    assert 'role=supplier' in result


def test_user_has_role():
    assert user_has_role({'users': {'role': 'admin'}}, 'admin')


def test_user_has_role_returns_false_on_invalid_json():
    assert not user_has_role({'in': 'valid'}, 'admin')


def test_user_has_role_returns_false_on_none():
    assert not user_has_role(None, 'admin')


def test_user_has_role_returns_false_on_non_matching_role():
    assert not user_has_role({'users': {'role': 'admin'}}, 'supplier')


def test_User_from_json():
    user = User.from_json({'users': {
        'id': 123,
        'emailAddress': 'test@example.com',
        'locked': False,
        'active': True,
        'name': 'Name',
        'role': 'admin',
        'termsAcceptedAt': '2016-01-01T01:00:00.0Z',
    }})

    assert user.id == 123
    assert user.name == 'Name'
    assert user.role == 'admin'
    assert user.email_address == 'test@example.com'
    assert not user.is_locked
    assert user.is_active


def test_User_from_json_with_supplier():
    user = User.from_json({'users': {
        'id': 123,
        'name': 'Name',
        'role': 'supplier',
        'emailAddress': 'test@example.com',
        'locked': False,
        'active': True,
        'supplier': {
            'supplierCode': 321,
            'name': 'test supplier',
        },
        'termsAcceptedAt': '2016-01-01T01:00:00.0Z',
    }})
    assert user.id == 123
    assert user.name == 'Name'
    assert user.role == 'supplier'
    assert user.email_address == 'test@example.com'
    assert user.supplier_code == 321
    assert user.supplier_name == 'test supplier'


def test_User_from_json_with_application():
    user = User.from_json({'users': {
        'id': 123,
        'name': 'Name',
        'role': 'applicant',
        'emailAddress': 'test@example.com',
        'locked': False,
        'active': True,
        'application': {
            'id': 5,
        },
        'termsAcceptedAt': '2016-01-01T01:00:00.0Z',
    }})
    assert user.id == 123
    assert user.name == 'Name'
    assert user.role == 'applicant'
    assert user.email_address == 'test@example.com'
    assert user.application_id == 5


def test_User_from_json_without_supplier():
    user = User.from_json({'users': {
        'id': 123,
        'name': 'Name',
        'role': 'applicant',
        'emailAddress': 'test@example.com',
        'locked': False,
        'active': True,
        'supplier': None,
        'termsAcceptedAt': '2016-01-01T01:00:00.0Z',
    }})
    assert user.id == 123
    assert user.name == 'Name'
    assert user.role == 'applicant'
    assert user.email_address == 'test@example.com'
    assert user.supplier_code is None
    assert user.supplier_name is None


def test_User_has_role(user_json):
    user = User.from_json(user_json)
    assert user.has_role('supplier')
    assert not user.has_role('admin')


def test_User_has_any_role(user_json):
    user = User.from_json(user_json)
    assert user.has_any_role('supplier', 'other')
    assert user.has_any_role('other', 'supplier')
    assert not user.has_any_role('other', 'admin')


def test_User_is_part_of_team():
    user = User.from_json({
        "users": {
            "id": 123,
            "emailAddress": "test@example.com",
            "name": "name",
            "role": "buyer",
            "locked": False,
            "active": True,
            "teams": [{
                "permissions": [],
                "name": "team name",
            }],
            'termsAcceptedAt': '2016-01-01T01:00:00.0Z',
        }
    })
    assert user.is_part_of_team()


def test_User_is_not_part_of_team():
    user = User.from_json({
        "users": {
            "id": 123,
            "emailAddress": "test@example.com",
            "name": "name",
            "role": "buyer",
            "locked": False,
            "active": True,
            "teams": [],
            'termsAcceptedAt': '2016-01-01T01:00:00.0Z',
        }
    })
    assert not user.is_part_of_team()


def test_User_has_permission():
    user = User.from_json({
        "users": {
            "id": 123,
            "emailAddress": "test@example.com",
            "name": "name",
            "role": "buyer",
            "locked": False,
            "active": True,
            "teams": [{
                "is_team_lead": False,
                "permissions": ['a'],
                "name": "team name",
            }],
            'termsAcceptedAt': '2016-01-01T01:00:00.0Z',
        }
    })
    assert user.has_permission('a')


def test_User_has_no_permission():
    user = User.from_json({
        "users": {
            "id": 123,
            "emailAddress": "test@example.com",
            "name": "name",
            "role": "buyer",
            "locked": False,
            "active": True,
            "teams": [{
                "is_team_lead": False,
                "permissions": ['foo'],
                "name": "team name",
            }],
            'termsAcceptedAt': '2016-01-01T01:00:00.0Z',
        }
    })
    assert not user.has_permission('bar')


def test_User_has_permission_when_team_lead():
    user = User.from_json({
        "users": {
            "id": 123,
            "emailAddress": "test@example.com",
            "name": "name",
            "role": "buyer",
            "locked": False,
            "active": True,
            "teams": [{
                "is_team_lead": True,
                "permissions": [],
                "name": "team name",
            }],
            'termsAcceptedAt': '2016-01-01T01:00:00.0Z',
        }
    })
    assert user.has_permission('bar')


def test_when_user_is_part_of_one_team():
    user = User.from_json({
        "users": {
            "id": 123,
            "emailAddress": "test@example.com",
            "name": "name",
            "role": "buyer",
            "locked": False,
            "active": True,
            "teams": [{
                "is_team_lead": True,
                "permissions": [],
                "name": "team name",
            }],
            'termsAcceptedAt': '2016-01-01T01:00:00.0Z',
        }
    })
    team = user.get_team()
    assert team['name'] == 'team name'


def test_when_user_is_part_of_two_teams():
    user = User.from_json({
        "users": {
            "id": 123,
            "emailAddress": "test@example.com",
            "name": "name",
            "role": "buyer",
            "locked": False,
            "active": True,
            "teams": [{
                "is_team_lead": True,
                "permissions": [],
                "name": "team name 1",
            }, {
                "is_team_lead": True,
                "permissions": [],
                "name": "team name 2",
            }],
            'termsAcceptedAt': '2016-01-01T01:00:00.0Z',
        }
    })
    team = user.get_team()
    assert team['name'] == 'team name 1'


def test_when_user_is_part_of_two_teams_has_no_permissions():
    user = User.from_json({
        "users": {
            "id": 123,
            "emailAddress": "test@example.com",
            "name": "name",
            "role": "buyer",
            "locked": False,
            "active": True,
            "teams": [{
                "is_team_lead": False,
                "permissions": ['a'],
                "name": "team name 1",
            }, {
                "is_team_lead": False,
                "permissions": ['b'],
                "name": "team name 2",
            }],
            'termsAcceptedAt': '2016-01-01T01:00:00.0Z',
        }
    })
    assert not user.has_permission('a')


def test_when_user_is_part_of_two_teams_has_no_permission_because_team_leads():
    user = User.from_json({
        "users": {
            "id": 123,
            "emailAddress": "test@example.com",
            "name": "name",
            "role": "buyer",
            "locked": False,
            "active": True,
            "teams": [{
                "is_team_lead": True,
                "permissions": ['a'],
                "name": "team name 1",
            }, {
                "is_team_lead": False,
                "permissions": ['b'],
                "name": "team name 2",
            }],
            'termsAcceptedAt': '2016-01-01T01:00:00.0Z',
        }
    })
    assert not user.has_permission('a')


def test_when_user_is_part_of_two_teams_has_permission_because_team_leads():
    user = User.from_json({
        "users": {
            "id": 123,
            "emailAddress": "test@example.com",
            "name": "name",
            "role": "buyer",
            "locked": False,
            "active": True,
            "teams": [{
                "is_team_lead": True,
                "permissions": ['a'],
                "name": "team name 1",
            }, {
                "is_team_lead": True,
                "permissions": ['b'],
                "name": "team name 2",
            }],
            'termsAcceptedAt': '2016-01-01T01:00:00.0Z',
        }
    })
    assert user.has_permission('a')


def test_when_user_is_part_of_two_teams_has_permissions():
    user = User.from_json({
        "users": {
            "id": 123,
            "emailAddress": "test@example.com",
            "name": "name",
            "role": "buyer",
            "locked": False,
            "active": True,
            "teams": [{
                "is_team_lead": False,
                "permissions": ['a'],
                "name": "team name 1",
            }, {
                "is_team_lead": False,
                "permissions": ['a'],
                "name": "team name 2",
            }],
            'termsAcceptedAt': '2016-01-01T01:00:00.0Z',
        }
    })
    assert user.has_permission('a')


def test_when_user_is_part_of_two_teams_has_permissions_when_team_id_is_given():
    user = User.from_json({
        "users": {
            "id": 123,
            "emailAddress": "test@example.com",
            "name": "name",
            "role": "buyer",
            "locked": False,
            "active": True,
            "teams": [{
                "id": 1,
                "is_team_lead": False,
                "permissions": ['a'],
                "name": "team name 1",
            }, {
                "id": 2,
                "is_team_lead": False,
                "permissions": ['b'],
                "name": "team name 2",
            }, {
                "id": 3,
                "is_team_lead": True,
                "permissions": [],
                "name": "team name 3",
            }],
            'termsAcceptedAt': '2016-01-01T01:00:00.0Z',
        }
    })
    assert user.has_permission('a', 1)
    assert not user.has_permission('d', 1)
    assert user.has_permission('b', 2)
    assert not user.has_permission('d', 2)
    assert user.has_permission('c', 3)


def test_when_user_is_not_part_of_a_team():
    user = User.from_json({
        "users": {
            "id": 123,
            "emailAddress": "test@example.com",
            "name": "name",
            "role": "buyer",
            "locked": False,
            "active": True,
            "teams": [],
            'termsAcceptedAt': '2016-01-01T01:00:00.0Z',
        }
    })
    assert user.get_team() is None


def test_User_load_user(user_json):
    data_api_client = mock.Mock()
    data_api_client.get_user.return_value = user_json

    user = User.load_user(data_api_client, 123)

    data_api_client.get_user.assert_called_once_with(user_id=123)
    assert user is not None
    assert user.id == 123


def test_User_load_user_raises_ValueError_on_non_integer_user_id():
    with pytest.raises(ValueError):
        data_api_client = mock.Mock()
        data_api_client.get_user.return_value = None

        User.load_user(data_api_client, 'foo')

    assert not data_api_client.get_user.called


def test_User_load_user_returns_None_if_no_user_is_found():
    data_api_client = mock.Mock()
    data_api_client.get_user.return_value = None

    loaded_user = User.load_user(data_api_client, 123)

    assert loaded_user is None


def test_User_load_user_returns_None_if_user_is_not_active(user_json):
    user_json['users']['active'] = False
    data_api_client = mock.Mock()
    data_api_client.get_user.return_value = user_json

    loaded_user = User.load_user(data_api_client, 123)

    assert loaded_user is None


def test_user_is_active(user):
    user.active = True
    user.locked = False

    assert user.is_active


def test_user_is_not_active_if_locked(user):
    user.active = True
    user.locked = True

    assert not user.is_active


def test_user_is_authenticated(user):
    user.active = True
    user.locked = False

    assert user.is_authenticated


def test_user_is_not_authenticated_if_not_active(user):
    user.active = False
    user.locked = False

    assert not user.is_authenticated


def test_user_is_not_authenticated_if_locked(user):
    user.active = True
    user.locked = True

    assert not user.is_authenticated
