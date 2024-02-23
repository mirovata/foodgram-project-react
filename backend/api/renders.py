import io
from collections import defaultdict

from rest_framework import renderers


class ShoppingCartDataRenderer(renderers.BaseRenderer):

    media_type = 'text/plain'
    format = 'txt'

    def render(self, data, accepted_media_type=None, renderer_context=None):
        text_buffer = io.StringIO()
        unique_data = defaultdict(int)

        for sd in data:
            key = (sd['name'], sd['measurement_unit'])
            unique_data[key] += sd['amount']

        for (name, measurement_unit), amount in unique_data.items():
            text_buffer.write(
                '• {name} ({measurement_unit}) - {amount}\n'.
                format(
                    name=name,
                    measurement_unit=measurement_unit,
                    amount=amount
                ))

        return text_buffer.getvalue()
