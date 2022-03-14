import pytest
import logging
from datetime import datetime
import python.prohibition_web_svc.middleware.keycloak_middleware as middleware
from python.prohibition_web_svc.models import db, UserRole
from python.prohibition_web_svc.app import create_app
from python.prohibition_web_svc.config import Config


@pytest.fixture
def application():
    return create_app()


@pytest.fixture
def as_guest(application):
    application.config['TESTING'] = True
    with application.test_client() as client:
        yield client


@pytest.fixture
def database(application):
    with application.app_context():
        db.init_app(application)
        db.create_all()
        yield db
        db.drop_all()
        db.session.commit()


@pytest.fixture
def roles(database):
    today = datetime.strptime("2021-07-21", "%Y-%m-%d")
    user_role = [
        UserRole(user_guid='john@idir', role_name='officer', submitted_dt=today),
        UserRole(user_guid='larry@idir', role_name='officer', submitted_dt=today, approved_dt=today)
    ]
    db.session.bulk_save_objects(user_role)
    db.session.commit()


def test_authorized_can_get_agencies(as_guest, monkeypatch, roles):
    monkeypatch.setattr(middleware, "get_keycloak_certificates", _mock_keycloak_certificates)
    monkeypatch.setattr(middleware, "decode_keycloak_access_token", _get_authorized_user)
    resp = as_guest.get(Config.URL_PREFIX + "/api/v1/static/agencies",
                        follow_redirects=True,
                        content_type="application/json",
                        headers=_get_keycloak_auth_header(_get_keycloak_access_token()))
    assert resp.status_code == 200
    assert "2101" in resp.json


def test_unauthorized_user_cannot_get_agencies(as_guest):
    resp = as_guest.get(Config.URL_PREFIX + "/api/v1/static/agencies",
                        follow_redirects=True,
                        content_type="application/json",
                        headers=_get_keycloak_auth_header(_get_unauthorized_user()))
    assert resp.status_code == 401


def test_authorized_user_gets_impound_lot_operators(as_guest, monkeypatch, roles):
    monkeypatch.setattr(middleware, "get_keycloak_certificates", _mock_keycloak_certificates)
    monkeypatch.setattr(middleware, "decode_keycloak_access_token", _get_authorized_user)
    resp = as_guest.get(Config.URL_PREFIX + "/api/v1/static/impound_lot_operators",
                        follow_redirects=True,
                        content_type="application/json",
                        headers=_get_keycloak_auth_header(_get_keycloak_access_token()))
    assert resp.status_code == 200
    assert "24 Hour Towing" in resp.json[0]['name']


def test_unauthorized_user_cannot_get_impound_lot_operators(as_guest):
    resp = as_guest.get(Config.URL_PREFIX + "/api/v1/static/impound_lot_operators",
                        follow_redirects=True,
                        content_type="application/json",
                        headers=_get_keycloak_auth_header(_get_unauthorized_user()))
    assert resp.status_code == 401


def test_authorized_user_gets_provinces(as_guest, monkeypatch, roles):
    monkeypatch.setattr(middleware, "get_keycloak_certificates", _mock_keycloak_certificates)
    monkeypatch.setattr(middleware, "decode_keycloak_access_token", _get_authorized_user)
    resp = as_guest.get(Config.URL_PREFIX + "/api/v1/static/provinces",
                        follow_redirects=True,
                        content_type="application/json",
                        headers=_get_keycloak_auth_header(_get_keycloak_access_token()))
    assert resp.status_code == 200
    assert 'objectCd' in resp.json[2]
    assert 'objectDsc' in resp.json[2]


def test_unauthorized_user_cannot_get_provinces(as_guest):
    resp = as_guest.get(Config.URL_PREFIX + "/api/v1/static/provinces",
                        follow_redirects=True,
                        content_type="application/json")
    assert resp.status_code == 401


def test_authorized_user_gets_jurisdictions(as_guest, monkeypatch, roles):
    monkeypatch.setattr(middleware, "get_keycloak_certificates", _mock_keycloak_certificates)
    monkeypatch.setattr(middleware, "decode_keycloak_access_token", _get_authorized_user)
    resp = as_guest.get(Config.URL_PREFIX + "/api/v1/static/jurisdictions",
                        follow_redirects=True,
                        content_type="application/json",
                        headers=_get_keycloak_auth_header(_get_keycloak_access_token()))
    assert resp.status_code == 200
    assert "AB" in resp.json[2]['objectCd']
    assert "Alberta" in resp.json[2]['objectDsc']


def test_unauthorized_user_cannot_get_jurisdictions(as_guest):
    resp = as_guest.get(Config.URL_PREFIX + "/api/v1/static/jurisdictions",
                        follow_redirects=True,
                        content_type="application/json")
    assert resp.status_code == 401


def test_authorized_user_can_get_countries(as_guest, monkeypatch, roles):
    monkeypatch.setattr(middleware, "get_keycloak_certificates", _mock_keycloak_certificates)
    monkeypatch.setattr(middleware, "decode_keycloak_access_token", _get_authorized_user)
    resp = as_guest.get(Config.URL_PREFIX + "/api/v1/static/countries",
                        follow_redirects=True,
                        content_type="application/json",
                        headers=_get_keycloak_auth_header(_get_keycloak_access_token()))
    assert resp.status_code == 200
    assert 'objectCd' in resp.json[2]
    assert 'objectDsc' in resp.json[2]


def test_unauthorized_user_cannot_get_countries(as_guest):
    resp = as_guest.get(Config.URL_PREFIX + "/api/v1/static/countries",
                        follow_redirects=True,
                        content_type="application/json")
    assert resp.status_code == 401


def test_authorized_user_gets_cities(as_guest, monkeypatch, roles):
    monkeypatch.setattr(middleware, "get_keycloak_certificates", _mock_keycloak_certificates)
    monkeypatch.setattr(middleware, "decode_keycloak_access_token", _get_authorized_user)
    resp = as_guest.get(Config.URL_PREFIX + "/api/v1/static/cities",
                        follow_redirects=True,
                        content_type="application/json",
                        headers=_get_keycloak_auth_header(_get_keycloak_access_token()))
    assert resp.status_code == 200
    assert "VICTORIA" in resp.json
    assert "100 MILE HOUSE" in resp.json


def test_unauthorized_user_cannot_get_cities(as_guest):
    resp = as_guest.get(Config.URL_PREFIX + "/api/v1/static/cities",
                        follow_redirects=True,
                        content_type="application/json")
    assert resp.status_code == 401


def test_authorized_user_gets_car_colors(as_guest, monkeypatch, roles):
    monkeypatch.setattr(middleware, "get_keycloak_certificates", _mock_keycloak_certificates)
    monkeypatch.setattr(middleware, "decode_keycloak_access_token", _get_authorized_user)
    resp = as_guest.get(Config.URL_PREFIX + "/api/v1/static/colors",
                        follow_redirects=True,
                        content_type="application/json",
                        headers=_get_keycloak_auth_header(_get_keycloak_access_token()))
    assert resp.status_code == 200
    assert "BLU" in resp.json


def test_unauthorized_user_cannot_get_car_colors(as_guest):
    resp = as_guest.get(Config.URL_PREFIX + "/api/v1/static/colors",
                        follow_redirects=True,
                        content_type="application/json")
    assert resp.status_code == 401


def test_authorized_user_can_get_vehicles(as_guest, monkeypatch, roles):
    monkeypatch.setattr(middleware, "get_keycloak_certificates", _mock_keycloak_certificates)
    monkeypatch.setattr(middleware, "decode_keycloak_access_token", _get_authorized_user)
    resp = as_guest.get(Config.URL_PREFIX + "/api/v1/static/vehicles",
                        follow_redirects=True,
                        content_type="application/json",
                        headers=_get_keycloak_auth_header(_get_keycloak_access_token()))
    assert resp.status_code == 200
    assert "AC" == resp.json[0]['make']
    assert "300" == resp.json[0]['model']


def test_unauthorized_cannot_get_vehicles(as_guest):
    resp = as_guest.get(Config.URL_PREFIX + "/api/v1/static/vehicles",
                        follow_redirects=True,
                        content_type="application/json")
    assert resp.status_code == 401


def test_authorized_user_can_get_vehicle_styles(as_guest, monkeypatch, roles):
    monkeypatch.setattr(middleware, "get_keycloak_certificates", _mock_keycloak_certificates)
    monkeypatch.setattr(middleware, "decode_keycloak_access_token", _get_authorized_user)
    resp = as_guest.get(Config.URL_PREFIX + "/api/v1/static/vehicle_styles",
                        follow_redirects=True,
                        content_type="application/json",
                        headers=_get_keycloak_auth_header(_get_keycloak_access_token()))
    assert resp.status_code == 200
    assert "2DR" == resp.json[0]


def test_unauthorized_user_cannot_get_vehicle_styles(as_guest):
    resp = as_guest.get(Config.URL_PREFIX + "/api/v1/static/vehicle_styles",
                        follow_redirects=True,
                        content_type="application/json")
    assert resp.status_code == 401


def test_unauthorized_user_can_get_keycloak_config(as_guest):
    resp = as_guest.get(Config.URL_PREFIX + "/api/v1/static/keycloak",
                        follow_redirects=True,
                        content_type="application/json")
    assert resp.status_code == 200
    assert 'realm' in resp.json
    assert 'url' in resp.json
    assert 'clientId' in resp.json


def test_authorized_user_can_get_keycloak_config(as_guest, monkeypatch, roles):
    monkeypatch.setattr(middleware, "get_keycloak_certificates", _mock_keycloak_certificates)
    monkeypatch.setattr(middleware, "decode_keycloak_access_token", _get_authorized_user)
    resp = as_guest.get(Config.URL_PREFIX + "/api/v1/static/keycloak",
                        follow_redirects=True,
                        content_type="application/json",
                        headers=_get_keycloak_auth_header(_get_keycloak_access_token()))
    assert resp.status_code == 200
    assert 'realm' in resp.json
    assert 'url' in resp.json
    assert 'clientId' in resp.json



def _get_unauthorized_user(**kwargs) -> tuple:
    logging.warning("inside _get_unauthorized_user()")
    kwargs['decoded_access_token'] = {'preferred_username': 'john@idir'}  # keycloak username
    return True, kwargs


def _get_authorized_user(**kwargs) -> tuple:
    logging.warning("inside _get_authorized_user()")
    kwargs['decoded_access_token'] = {'preferred_username': 'larry@idir'}  # keycloak username
    return True, kwargs


def _get_keycloak_access_token() -> str:
    return 'some-secret-access-token'


def _get_keycloak_auth_header(access_token) -> dict:
    return dict({
        'Authorization': 'Bearer {}'.format(access_token)
    })


def _mock_keycloak_certificates(**kwargs) -> tuple:
    logging.warning("inside _mock_keycloak_certificates()")
    return True, kwargs