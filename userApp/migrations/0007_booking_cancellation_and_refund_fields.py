# Generated manually to add cancellation and refund tracking fields to Booking
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("userApp", "0006_review"),
    ]

    operations = [
        migrations.AddField(
            model_name="booking",
            name="cancellation_reason",
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="booking",
            name="cancellation_requested_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="booking",
            name="refund_amount",
            field=models.FloatField(default=0.0),
        ),
        migrations.AddField(
            model_name="booking",
            name="refund_notes",
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="booking",
            name="refund_processed_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
