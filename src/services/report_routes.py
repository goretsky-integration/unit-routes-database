import collections
from typing import Iterable

import models

__all__ = ('group_report_routes_by_report_type_and_chat_id',)


def group_report_routes_by_report_type_and_chat_id(
        report_routes: Iterable[models.ReportRoute]
) -> list[models.GroupedByReportTypeAndChatIDReportRoute]:
    chat_id_and_report_type_to_unit_ids: dict[str, list[int]] = collections.defaultdict(list)
    for report_route in report_routes:
        key = f'{report_route.chat_id}@{report_route.report_type_name}'
        chat_id_and_report_type_to_unit_ids[key].append(report_route.unit_id)
    grouped_report_routes: list[models.GroupedByReportTypeAndChatIDReportRoute] = []
    for chat_id_and_report_type, unit_ids in chat_id_and_report_type_to_unit_ids.items():
        chat_id, *report_type = chat_id_and_report_type.split('@')
        report_type = '@'.join(report_type)
        chat_id = int(chat_id)
        grouped_report_routes.append(models.GroupedByReportTypeAndChatIDReportRoute(
            chat_id=chat_id,
            report_type=report_type,
            unit_ids=unit_ids,
        ))
    return grouped_report_routes
