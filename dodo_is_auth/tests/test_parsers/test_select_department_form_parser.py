from dodo_is_auth.models import SelectDepartmentFormData, HTML
from dodo_is_auth.parsers import parse_select_department_form


def test_parse_select_department_form():
    html = """
        <form method="post">
            <input type="hidden" name="__RequestVerificationToken" value="token123">
            <select name="department">
                <option value="1">Department 1</option>
                <option value="2">Department 2</option>
            </select>
            <input type="submit" value="Select">
        </form>
    """
    result = parse_select_department_form(HTML(html))

    assert isinstance(result, SelectDepartmentFormData)
    assert result.request_verification_token == 'token123'
