import json

import pika
from django.core.management import BaseCommand
from django.db.models import QuerySet

from reports.models.report_routes import ReportRoute
from write_offs.models import IngredientWriteOff
from write_offs.services import (
    get_expired_repeating_write_offs,
    get_upcoming_write_offs,
)


class Command(BaseCommand):

    def handle(self, *args, **options):
        connection = pika.BlockingConnection(
            pika.ConnectionParameters('localhost')
            )
        channel = connection.channel()
        channel.queue_declare('specific-units-event')
        minutes = [15, 10, 5]
        for minute in minutes:
            write_offs = get_upcoming_write_offs(minute)
            for write_off in write_offs:
                channel.basic_publish(
                    exchange='',
                    routing_key='specific-units-event',
                    body=json.dumps({
                        'type': 'WRITE_OFFS',
                        'unit_ids': [write_off.unit_id],
                        'payload': {
                            'type': f'EXPIRE_AT_{minute}_MINUTES',
                            'unit_name': write_off.unit.name,
                            'ingredient_name': write_off.ingredient.name,
                            'write_off_time_a1_coordinates': 'A1',
                            'checkbox_a1_coordinates': 'A1',
                        }
                    }).encode('utf-8'),
                )
                write_off.is_notification_sent = True
                write_off.save(update_fields=['is_notification_sent'])

        for write_off in get_expired_repeating_write_offs():
            channel.basic_publish(
                exchange='',
                routing_key='specific-units-event',
                body=json.dumps({
                    'type': 'WRITE_OFFS',
                    'unit_ids': [write_off.unit_id],
                    'payload': {
                        'type': 'ALREADY_EXPIRED',
                        'unit_name': write_off.unit.name,
                        'ingredient_name': write_off.ingredient.name,
                        'write_off_time_a1_coordinates': 'A1',
                        'checkbox_a1_coordinates': 'A1',
                    }
                }).encode('utf-8'),
            )
            write_off.is_notification_sent = True
            write_off.save(update_fields=['is_notification_sent'])



