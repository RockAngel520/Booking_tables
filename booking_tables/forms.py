import datetime

from django.core.exceptions import ValidationError
from django.forms import (
    BooleanField,
    ChoiceField,
    DateInput,
    HiddenInput,
    ModelChoiceField,
    ModelForm,
    RadioSelect,
    Textarea,
    Widget,
)

from booking_tables.models import Booking, Table


class StyleFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if isinstance(field, BooleanField):
                field.widget.attrs["class"] = "form-check-input"
            else:
                field.widget.attrs["class"] = "form-control"


class TimeButtonWidget(Widget):
    """Виджет для отображения времени в виде плитки"""

    template_name = "widgets/time_button_widget.html"

    def __init__(self, attrs=None, time_choices=None):
        super().__init__(attrs)
        self.time_choices = time_choices or []

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context["widget"]["time_choices"] = self.time_choices
        context["widget"]["value"] = value
        return context


class BookingForm(StyleFormMixin, ModelForm):
    """Форма бронирования столика"""

    # Базовый список всех возможных времен
    ALL_TIME_CHOICES = [
        ("12:00", "12:00"),
        ("13:00", "13:00"),
        ("14:00", "14:00"),
        ("15:00", "15:00"),
        ("16:00", "16:00"),
        ("17:00", "17:00"),
        ("18:00", "18:00"),
        ("19:00", "19:00"),
        ("20:00", "20:00"),
        ("21:00", "21:00"),
        ("22:00", "22:00"),
        ("23:00", "23:00"),
    ]

    time = ChoiceField(choices=ALL_TIME_CHOICES, widget=RadioSelect(), label="Время")

    # Добавляем поле table обратно, но скрываем стандартный виджет
    table = ModelChoiceField(
        queryset=Table.objects.filter(is_publish=True),
        widget=HiddenInput(),  # Скрытое поле для валидации
        required=True,
        label="Столик",
    )

    class Meta:
        model = Booking
        exclude = (
            "guest",
            "created_at",
        )
        widgets = {
            "date": DateInput(
                attrs={
                    "type": "date",
                    "id": "id_date",
                    "class": "form-control",
                }
            ),
            "comment": Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        today = datetime.date.today()
        two_month_later = today + datetime.timedelta(days=60)

        self.fields["date"].widget.attrs.update(
            {
                "min": today.isoformat(),
                "max": two_month_later.isoformat(),
            }
        )

        # Не задаем начальное значение для даты
        if "value" in self.fields["date"].widget.attrs:
            del self.fields["date"].widget.attrs["value"]

    def clean(self):
        """Валидация времени с учетом даты и проверка доступности столика"""

        cleaned_data = super().clean()
        date = cleaned_data.get("date")
        time = cleaned_data.get("time")
        table = cleaned_data.get("table")

        if date and time:

            # Если выбрана сегодняшняя дата
            if date == datetime.date.today():
                current_time = datetime.datetime.now().time()
                time_obj = datetime.datetime.strptime(time, "%H:%M").time()

                # Добавляем дополнительно 10 минут к текущему времени
                buffer_time = (
                    datetime.datetime.now() + datetime.timedelta(minutes=10)
                ).time()

                if time_obj < buffer_time:
                    raise ValidationError(
                        {
                            "time": f'На сегодня нельзя выбрать время раньше {buffer_time.strftime("%H:%M")}.'
                            f'Текущее время: {current_time.strftime("%H:%M")}'
                        }
                    )

        # Проверка доступности столика на выбранное время
        if date and time and table:
            existing_booking = Booking.objects.filter(
                table=table, date=date, time=time
            ).exists()

            if existing_booking:
                raise ValidationError(
                    {"table": "Этот столик уже забронирован на выбранное время"}
                )

        return cleaned_data
