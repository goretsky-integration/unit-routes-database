import json

import pika
from django.core.management import BaseCommand
from django.db.models import QuerySet

from reports.models.report_routes import ReportRoute
from write_offs.models import IngredientWriteOff
from write_offs.services import (
    get_upcoming_write_offs, get_write_off_status,
)


class Command(BaseCommand):

    def handle(self, *args, **options):
        connection = pika.BlockingConnection(
            pika.ConnectionParameters('localhost')
            )
        channel = connection.channel()
        channel.queue_declare('specific-units-event')
        write_offs = get_upcoming_write_offs()
        for write_off in write_offs:
            status = get_write_off_status(write_off)
            if status is None:
                continue
            channel.basic_publish(
                exchange='',
                routing_key='specific-units-event',
                body=json.dumps({
                    'type': 'WRITE_OFFS',
                    'unit_ids': [write_off.unit_id],
                        'payload': {
                        'type': status,
                            'unit_name': write_off.unit.name,
                        'ingredient_name': write_off.ingredient.name,
                        'write_off_id': str(write_off.id),
                        'write_off_time_a1_coordinates': 'A1',
                            'checkbox_a1_coordinates': 'A1',
                    }
                }).encode('utf-8'),
            )
            write_off.is_notification_sent = True
            write_off.save(update_fields=['is_notification_sent'])
