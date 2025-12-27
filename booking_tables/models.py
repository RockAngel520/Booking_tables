from django.db import models

from users.models import User


class Table(models.Model):
    number = models.PositiveIntegerField(unique=True, verbose_name="Номер столика", help_text="Укажите номер столика")
    max_guests = models.PositiveIntegerField(default=2, verbose_name="Максимальная вместимость столика", help_text=(
        "Укажите максимальную вместимость гостей за столиком"))
    description = models.TextField(verbose_name="Описание", help_text="Введите описание", blank=True, null=True)
    image = models.ImageField(
        upload_to="booking_tables/media",
        blank=True,
        null=True,
        verbose_name="Фото столика",
        help_text="Добавьте фото столика",
    )
    is_publish = models.BooleanField(verbose_name="Доступен к бронированию", default=True)

    class Meta:
        verbose_name = "Столик"
        verbose_name_plural = "Столики"

    def __str__(self):
        return f"Столик №{self.number}"


class Booking(models.Model):
    guest = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="bookings",
        verbose_name="Гость",
        help_text="Выберите гостя",
    )
    number_of_guests = models.PositiveIntegerField(default=1, verbose_name="Количество гостей", help_text=("Укажите "
                                                                                                           "количество гостей"))
    date = models.DateField(verbose_name="Дата посещения", help_text="Укажите дату посещения")
    time = models.TimeField(verbose_name="Время посещения", help_text="Укажите время посещения")
    created_at = models.DateField(auto_now_add=True, verbose_name="Дата создания")
    comment = models.TextField(verbose_name="Комментарий", help_text="Введите комментарии (пожелания)", blank=True,
                               null=True)
    table = models.ForeignKey(
        Table,
        on_delete=models.CASCADE,
        related_name="tables",
        verbose_name="Столик",
        help_text="Выберите столик",
    )

    class Meta:
        verbose_name = "Бронирование"
        verbose_name_plural = "Брони"
        ordering = ["guest", "number_of_guests", "date", "time", "comment", "table"]
        # permissions = [
        #     ('can_unpublish_product', 'Can unpublish product'),
        # ]

    def __str__(self):
        return f"Бронирование номер {self.id} от {self.guest} на {self.date} {self.time}"
