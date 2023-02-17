import pytest

import models
from services.report_routes import group_report_routes_by_report_type_and_chat_id


@pytest.mark.parametrize(
    'report_routes, expected',
    [
        (
                (
                        models.ReportRoute(
                            report_type_name='STATISTICS',
                            unit_id=389,
                            chat_id=123456,
                        ),
                        models.ReportRoute(
                            report_type_name='STATISTICS',
                            unit_id=400,
                            chat_id=123456,
                        )
                ),
                [
                    models.GroupedByReportTypeAndChatIDReportRoute(
                        report_type='STATISTICS',
                        chat_id=123456,
                        unit_ids=[389, 400],
                    ),
                ]
        ),
        (
                (
                        models.ReportRoute(
                            report_type_name='STATISTICS',
                            unit_id=389,
                            chat_id=234567,
                        ),
                        models.ReportRoute(
                            report_type_name='STATISTICS',
                            unit_id=389,
                            chat_id=12345,
                        ),
                ),
                [
                    models.GroupedByReportTypeAndChatIDReportRoute(
                        report_type='STATISTICS',
                        chat_id=234567,
                        unit_ids=[389],
                    ),
                    models.GroupedByReportTypeAndChatIDReportRoute(
                        report_type='STATISTICS',
                        chat_id=12345,
                        unit_ids=[389],
                    )
                ],
        ),
        (
                (
                        models.ReportRoute(
                            report_type_name='STATISTICS',
                            unit_id=389,
                            chat_id=12345,
                        ),
                        models.ReportRoute(
                            report_type_name='STATISTICS',
                            unit_id=400,
                            chat_id=12345,
                        ),
                        models.ReportRoute(
                            report_type_name='STATISTICS',
                            unit_id=401,
                            chat_id=12345,
                        ),
                        models.ReportRoute(
                            report_type_name='STOP_SALES',
                            unit_id=389,
                            chat_id=12345,
                        ),
                        models.ReportRoute(
                            report_type_name='STOP_SALES',
                            unit_id=401,
                            chat_id=12345,
                        ),
                        models.ReportRoute(
                            report_type_name='STOP_SALES',
                            unit_id=389,
                            chat_id=4246234,
                        ),
                ),
                [
                    models.GroupedByReportTypeAndChatIDReportRoute(
                        report_type='STATISTICS',
                        unit_ids=[389, 400, 401],
                        chat_id=12345,
                    ),
                    models.GroupedByReportTypeAndChatIDReportRoute(
                        report_type='STOP_SALES',
                        unit_ids=[389, 401],
                        chat_id=12345,
                    ),
                    models.GroupedByReportTypeAndChatIDReportRoute(
                        report_type='STOP_SALES',
                        unit_ids=[389],
                        chat_id=4246234,
                    )
                ],
        ),
        (
                [], [],
        )
    ]
)
def test_group_report_routes_by_report_type_and_chat_id(report_routes, expected):
    assert group_report_routes_by_report_type_and_chat_id(report_routes) == expected
