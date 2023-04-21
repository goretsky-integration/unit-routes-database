from dodo_is_auth.models import SelectRoleFormData, HTML
from dodo_is_auth.parsers import parse_select_role_form


def test_parse_select_role_form():
    html = """
        <form method="post">
            <input type="hidden" name="__RequestVerificationToken" value="token456">
            <select name="role">
                <option value="1">Role 1</option>
                <option value="2">Role 2</option>
            </select>
            <input type="submit" value="Select">
        </form>
    """
    result = parse_select_role_form(HTML(html))

    assert isinstance(result, SelectRoleFormData)
    assert result.request_verification_token == 'token456'
