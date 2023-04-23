import httpx
import pytest
from uuid import UUID
from httpx import Response
from dodo_is_auth.models import (
    HTML, HTTPClient, SignInOidcFormData,
    SelectRoleFormData, SelectDepartmentFormData
)
from dodo_is_auth.office_manager import OfficeManagerService


@pytest.fixture
def http_client():
    yield HTTPClient(httpx.Client(base_url='https://example.com'))


@pytest.fixture
def office_manager_service(http_client):
    yield OfficeManagerService(http_client)


def test_go_to_office_manager_domain(httpx_mock, office_manager_service):
    httpx_mock.add_response(text='<html>...')
    expected = HTML('<html>...')
    assert office_manager_service.go_to_office_manager_domain() == expected


def test_send_sign_in_oidc_form_data(httpx_mock, office_manager_service):
    httpx_mock.add_response(text='<html>...')
    form_data = SignInOidcFormData(code='123', scope='openid', state='state',
                                   session_state='session_state')
    response = office_manager_service.send_sign_in_oidc_form_data(form_data)
    assert response == HTML('<html>...')


def test_send_select_role_form_data(httpx_mock, office_manager_service):
    httpx_mock.add_response(text='<html>...')
    form_data = SelectRoleFormData(request_verification_token='token')
    response = office_manager_service.send_select_role_form_data(
        select_role_form_data=form_data,
    )
    assert response == HTML('<html>...')


def test_send_select_role_form_data_with_selected_role_id(
        httpx_mock,
        office_manager_service,
):
    httpx_mock.add_response(text='<html>...')
    form_data = SelectRoleFormData(request_verification_token='token')
    response = office_manager_service.send_select_role_form_data(
        select_role_form_data=form_data,
        selected_role_id=1,
    )
    assert response == HTML('<html>...')


def test_send_select_department_form_data(httpx_mock, office_manager_service):
    httpx_mock.add_response(text='<html>...')
    form_data = SelectDepartmentFormData(request_verification_token='token')
    response = office_manager_service.send_select_department_form_data(
        select_department_form_data=form_data,
    )
    assert response == HTML('<html>...')


def test_send_select_department_form_data_with_selected_department_uuid(
        httpx_mock,
        office_manager_service,
):
    httpx_mock.add_response(text='<html>...')
    form_data = SelectDepartmentFormData(request_verification_token='token')
    selected_department_uuid = UUID('a8098c1a-f86e-11da-bd1a-00112444be1e')
    response = office_manager_service.send_select_department_form_data(
        select_department_form_data=form_data,
        selected_department_uuid=selected_department_uuid,
    )
    assert response == HTML('<html>...')
