from django.db import models
#from django.utils.translation import ugettext as _
from django.utils.translation import gettext_lazy as _

#from PIL import Image
#from PIL import ImageFile
#ImageFile.LOAD_TRUNCATED_IMAGES = True

from django.contrib.auth.models import User

# Create your models here.

# ћодели отображают информацию о данных, с которыми вы работаете.
# ќни содержат пол¤ и поведение ваших данных.
# ќбычно одна модель представл¤ет одну таблицу в базе данных.
#  ажда¤ модель это класс унаследованный от django.db.models.Model.
# јтрибут модели представл¤ет поле в базе данных.
# Django предоставл¤ет автоматически созданное API дл¤ доступа к данным

# choices (список выбора). »тератор (например, список или кортеж) 2-х элементных кортежей,
# определ¤ющих варианты значений дл¤ пол¤.
# ѕри определении, виджет формы использует select вместо стандартного текстового пол¤
# и ограничит значение пол¤ указанными значени¤ми.

#  атегори¤ тестового задани¤
class Logfile(models.Model):
    # „итабельное им¤ пол¤ (метка, label).  аждое поле, кроме ForeignKey, ManyToManyField и OneToOneField,
    # первым аргументом принимает необ¤зательное читабельное название.
    # ≈сли оно не указано, Django самосто¤тельно создаст его, использу¤ название пол¤, замен¤¤ подчеркивание на пробел.
    # null - ≈сли True, Django сохранит пустое значение как NULL в базе данных. ѕо умолчанию - False.
    # blank - ≈сли True, поле не об¤зательно и может быть пустым. ѕо умолчанию - False.
    # Ёто не то же что и null. null относитс¤ к базе данных, blank - к проверке данных.
    # ≈сли поле содержит blank=True, форма позволит передать пустое значение.
    # ѕри blank=False - поле об¤зательно.
    datel = models.DateTimeField(_('datel'), auto_now_add=True)
    category = models.CharField(_('category'), max_length=128)
    details = models.TextField(_('logfile_details'), blank=True, null=True)
    class Meta:
        # ѕараметры модели
        # ѕереопределение имени таблицы
        db_table = 'logfile'
        # indexes - список индексов, которые необходимо определить в модели
        indexes = [
            models.Index(fields=['datel', 'category']),
        ]
        # —ортировка по умолчанию
        ordering = ['datel']
    def __str__(self):
        # ¬ывод названи¤в тег SELECT 
        return "{}\t{}".format(self.datel, self.category)
