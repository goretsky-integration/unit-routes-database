from collections.abc import Iterable

from reports.services.gateways.dodo_is_api import StaffMemberBirthday


def clean_staff_member_full_name(name: str) -> str:
    prefixes_to_clean = (
        'СЗ',
        'сз',
        'Сз',
        'сЗ',
        'У',
        'у',
        'К',
        'к',
        'k',
        'K',
    )
    for prefix in prefixes_to_clean:
        name = name.removeprefix(f'{prefix} ').strip()
    return name


def filter_birthdays_by_full_name(
    employee_birthdays: Iterable[StaffMemberBirthday],
) -> list[StaffMemberBirthday]:
    blacklist = ["Аббасов Азиз", "Амбарцумова Виктория", "Быкова Вероника",
                 "Герганова Мария", "Горецкая Антонина", "Горецкая Инна",
                 "Горецкий Владимир", "Горяйнова Светлана",
                 "Зиганшин Александр", "Котиков Александр", "Лавренова Ольга",
                 "Медникова Анастасия", "Савихина Елена", "Тиукова Елизавета",
                 "Тутаева Тамара", "курьер", "кандидат", "стажер",
                 "достависта"]
    employees_blacklist = {name.lower() for name in blacklist}

    result: list[StaffMemberBirthday] = []

    for employee_birthday in employee_birthdays:
        for employee_in_blacklist in employees_blacklist:
            if employee_in_blacklist in employee_birthday.full_name.lower():
                break
        else:
            result.append(employee_birthday)

    return result
