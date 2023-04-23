from uuid import UUID

from dodo_is_auth.models import (
    HTML,
    HTTPClient,
    SignInOidcFormData,
    SelectRoleFormData,
    SelectDepartmentFormData,
)


class OfficeManagerService:

    def __init__(self, http_client: HTTPClient):
        self._http_client = http_client

    def go_to_office_manager_domain(self) -> HTML:
        response = self._http_client.get('/')
        return HTML(response.text)

    def send_sign_in_oidc_form_data(
            self,
            sign_in_oidc_form_data: SignInOidcFormData,
    ) -> HTML:
        request_data = {
            'code': sign_in_oidc_form_data.code,
            'scope': sign_in_oidc_form_data.scope,
            'state': sign_in_oidc_form_data.state,
            'session_state': sign_in_oidc_form_data.session_state,
        }
        url = '/signin-oidc'
        response = self._http_client.post(
            url=url,
            data=request_data,
        )
        return HTML(response.text)

    def send_select_role_form_data(
            self,
            *,
            select_role_form_data: SelectRoleFormData,
            selected_role_id: int | None = None,
    ) -> HTML:
        request_data = {
            'roleId': selected_role_id,
            '__RequestVerificationToken': select_role_form_data.request_verification_token,
        }
        url = '/Infrastructure/Authenticate/SelectRole'
        response = self._http_client.post(url, data=request_data)
        return HTML(response.text)

    def send_select_department_form_data(
            self,
            *,
            select_department_form_data: SelectDepartmentFormData,
            selected_department_uuid: UUID | None = None,
    ) -> HTML:
        request_data = {
            'uuid': selected_department_uuid,
            '__RequestVerificationToken': select_department_form_data.request_verification_token,
        }
        url = '/Infrastructure/Authenticate/SelectDepartment'
        response = self._http_client.post(url, data=request_data)
        return HTML(response.text)
