# Класс HttpResponse из пакета django.http, который позволяет отправить текстовое содержимое.
from django.http import HttpResponse, HttpResponseNotFound

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
#from django.utils.translation import ugettext as _
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponseRedirect

from django.utils.decorators import method_decorator
from django.views.generic import UpdateView
from django.contrib.auth.models import User
from django.urls import reverse_lazy

from django.urls import reverse

from django.contrib.auth import login as auth_login

import time

# Подключение моделей
from .models import Logfile
# Подключение форм
#from .forms import LogfileForm

# Create your views here.
# Групповые ограничения
def group_required(*group_names):
    """Requires user membership in at least one of the groups passed in."""
    def in_groups(u):
        if u.is_authenticated:
            if bool(u.groups.filter(name__in=group_names)) | u.is_superuser:
                return True
        return False
    return user_passes_test(in_groups, login_url='403')

# Стартовая страница 
def index(request):
    try:
        # Стартовые данные
        glob.start_url = "https://zakup.sk.kz/#/ext/participants"
        glob.start_page = 1
        glob.finish_page = 10
        glob.pause_popup = 2
        glob.pause_load_page = 4
        glob.pause_flipping = 1
        glob.pause_flipping_shot = 1
        if request.method == "POST":
            glob.start_url = request.POST.get("start_url")
            glob.start_page = int(request.POST.get("start_page"))
            glob.finish_page = int(request.POST.get("finish_page"))
            glob.pause_popup = float(request.POST.get("pause_popup"))
            glob.pause_load_page = float(request.POST.get("pause_load_page"))
            glob.pause_flipping = float(request.POST.get("pause_flipping"))
            glob.pause_flipping_shot = float(request.POST.get("pause_flipping_shot"))
            glob.data = []   
            run()
        return render(request, "index.html", {"start_url": glob.start_url, "start_page": glob.start_page, "finish_page": glob.finish_page, "pause_popup": glob.pause_popup, 
                                              "pause_load_page": glob.pause_load_page, "pause_flipping": glob.pause_flipping, "pause_flipping_shot": glob.pause_flipping_shot, })
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# Контакты
def contact(request):
    return render(request, "contact.html")

###################################################################################################

# Импорт библиотек
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
# Таймер
from time import sleep        
# Чтобы засечь время выполнения
import time
# Подключаем модуль для работы с датой/веременем
from datetime import datetime, timedelta
# Работа в потоке
import threading
# Вывод в Excel
import xlwt
# Заголовок в Excel
HEADER = ["1", "2", "Наименование", "ИИН/БИН", "Организационно правовая форма", "Юридический адрес", "Руководитель, Должность", "Руководитель, ФИО", "E-mail", "Факс", "Телефон", "Сайт", "URL"]
# Функция отладки
DEBUG = False
# Элемент класса Firefox, Chrome, Edge.
driver = webdriver.Ie()

# Общие "глобальные" переменные (со значениями по умолчанию), здесь не меняются, меняются в set_variables() для консольного или в главной форме для оконного
def glob():
    # start_url основной страницы (не менять!)
    start_url="https://zakup.sk.kz/#/ext/participants"
    # Стартовая страница (не менять!)
    start_page = 1
    # Финишная страница (не менять!)
    finish_page = 100
    # Пауза для загрузки всплывающего окна (не менять!)
    pause_popup = 3
    # Пауза для загрузки страницы (не менять!)
    pause_load_page = 5
    # Пауза для переключения между страницами (не менять!)
    pause_flipping = 1
    pause_flipping_shot = 0.5
    # Список для экспорта в Excel (не менять!)
    data = []      

# Запись в лог-файл
def writing_log(category, message):
    try:        
        # Лог-файл
        somefile = open("log.txt", "a", encoding="utf-8")
        # Сообщение
        message = str(datetime.now().strftime('%d.%m.%Y %H:%M:%S')) + "\t" + category + "\t" + message + "\r"
        try:
            # Запись в файл и вывод на экран
            somefile.write(message)
            print(message)
        except Exception as exception:
            print(exception)
        finally:
            # Закрыть при любом раскладе!
            somefile.close()
    except Exception as exception:
        #print(exception)
        writing_log("Ошибка", "writing_log\t" + str(exception))

# Экспорт данных в Excel
# hdr - Заголовок таблицы, dat данные (список списков), название файла
def export_to_excel(hdr, dat, file_name):
    try:
        writing_log("Информация", "Экспорт в Excel")
        # Убрать начальные и концевые пробеды
        for i in range(0, len(dat)):
            for j in range(0, len(dat[i])):
                dat[i][j] = dat[i][j].strip()
        # Максимальная ширина столбца в Excel
        col_max_width = 65535
        # Стиль заголовка
        style_hdr = xlwt.easyxf('font: name Arial, color-index blue, bold on')
        # Стиль данных
        style_dat = xlwt.easyxf('font: name Arial')
        # Новая книга
        wb = xlwt.Workbook()
        # Новый лист
        ws = wb.add_sheet("List")
        # Заголовок
        for i in range(0, len(hdr)):        
            ws.write(0, i, hdr[i], style_hdr)
        # Данные (смещение на 1 строку из-за заголовка)
        #for row in dat:
        #    for elem in row:
        #        print(elem, end=' ')
        #    print()
        for i in range(0, len(dat)):
            for j in range(0, len(dat[i])):
                #print(dat[i][j])
                # Подбор ширины колонки в зависимости от длины выводимых данных
                cwidth = ws.col(j).width
                if (len(dat[i][j])*367) > cwidth:
                    if len(dat[i][j])*367 > col_max_width :
                        ws.col(j).width = col_max_width
                    else:
                        ws.col(j).width = (len(dat[i][j])*367)
                # Запись ячейки
                ws.write(i+1, j, dat[i][j], style_dat)
        # Сохранить книгу
        wb.save(file_name)
        writing_log("Информация", "См. файл: " + str(file_name))
    except Exception as exception:
        #print(exception)
        writing_log("Ошибка", "export_to_excel\t" + str(exception))

# Получение дополнительной информации по ссылке url
def details(url):
    try:
        # Пустой url не надо
        if (url==''):
            return
        # Пустой url не надо
        if(url[0:39]!="https://zakup.sk.kz/#/ext/participants("):
            return
        # Для контроля
        writing_log("Информация", "Старт парсинга " + str(url))
        # Метод driver.get перенаправляет к странице URL в параметре.
        # WebDriver будет ждать пока страница не загрузится полностью (то есть, событие “onload” игнорируется), 
        # прежде чем передать контроль вашему тесту или скрипту. 
        driver.get(url)
        # Задержка по времени т.к. это всплвающе окно и ему надо отработать
        writing_log("Информация", "Старт паузы для всплывающего окна")
        sleep(glob.pause_popup)
        #writing_log("Информация", "Продолжить после паузы")
        row = []    # Один клиент
        # Поиск информации
        inputs = driver.find_elements(By.TAG_NAME, "input")
        for inp in inputs:
            if inp.get_attribute("type") == "text":
                row.append(inp.get_attribute("value"))
        row.append(url)     # Добавить url для контроля
        writing_log("Данные", str(row))
        # Нажатие кнопки "Закрыть"
        #button_close = driver.find_element(By.XPATH, "/html/body/ngb-modal-window/div/div/jhi-participant-info/form/div[3]/button")
        #button_close = driver.find_element(By.CLASS_NAME, "button button--inverted")
        #writing_log("Информация", "Найдена кнопка \"Закрыть\"")
        button_close = driver.find_element(By.CLASS_NAME, "close")
        writing_log("Информация", "Найдена кнопка \"X\"")
        button_close.click()
        writing_log("Информация", "Нажата кнопка \"X\"")
        # В завершение, окно браузера закрывается. Вы можете также вызывать метод quit вместо close. 
        # Метод quit закроет браузер полностью, в то время как close закроет одну вкладку. 
        #driver.close()
        return row
    except Exception as exception:
        #print(exception)
        row = [] 
        writing_log("Ошибка", "details\t" + str(exception))
        button_close = driver.find_element(By.CLASS_NAME, "button button--inverted")
        writing_log("Информация", "Найдена кнопка \"Закрыть\"")
        button_close.click()
        writing_log("Информация", "Нажата кнопка \"Закрыть\"")

def parsing(url):
    try:
        # Метод driver.get перенаправляет к странице URL в параметре.
        # WebDriver будет ждать пока страница не загрузится полностью (то есть, событие “onload” игнорируется), 
        # прежде чем передать контроль вашему тесту или скрипту. 
        driver.get(url)
        # Задержка по времени для загрузки страницы
        writing_log("Информация", "Старт паузы для загрузки страницы")
        sleep(glob.pause_load_page)
        #writing_log("Информация", "Продолжить после паузы")
        # Поиск ссылок
        links = driver.find_elements(By.TAG_NAME, "a")
        for link in links:
            try:
                glob.data.append(details(link.get_attribute('href')))
                if glob.data[len(glob.data)-1] == None:
                    glob.data.pop(len(glob.data)-1)
                else:
                    if (len(glob.data) > 0):
                        writing_log("Информация", "Создана запись № " + str(len(glob.data)))
                    if (len(glob.data) % 100 == 0):
                        # Вызов: заголовок таблицы, данные, название файла
                        current_date_time = datetime.now().strftime('%Y%m%d%H%M%S')
                        export_to_excel(HEADER, glob.data, "zakup.kz." + str(current_date_time) + ".xls")
                    # Если это отладка достточно будте по три карточки
                    if DEBUG == True:
                        if (len(glob.data) % 3 == 0):
                            break # Счетчик на время тестирования
            except Exception as exception:
                #print(exception)
                writing_log("Ошибка", "parsing for link in links\t" + str(exception))
        # В завершение, окно браузера закрывается. Вы можете также вызывать метод quit вместо close. 
        # Метод quit закроет браузер полностью, в то время как close закроет одну вкладку. 
        #driver.quit()
    except Exception as exception:
        #print(exception)
        writing_log("Ошибка", "parsing\t" + str(exception))

# Запуск процесса
def run():    
    try:
        # Установить переменные (используется в консольном приложении, в оконном получается из формы)
        #set_variables()
        # Время старта
        start = time.time()
        # Записать праметры
        writing_log("Информация", "Старт")
        writing_log("Информация", "URL основной страницы " + str(glob.start_url))
        writing_log("Информация", "Стартовая страница " + str(glob.start_page))
        writing_log("Информация", "Финишная страница " + str(glob.finish_page))
        writing_log("Информация", "Пауза для загрузки страницы " + str(glob.pause_load_page))
        writing_log("Информация", "Пауза для переключения между страницами " + str(glob.pause_flipping))
        writing_log("Информация", "Пауза для переключения между страницами " + str(glob.pause_flipping_shot))
        writing_log("Информация", "Пауза для загрузки всплывающего окна " + str(glob.pause_popup))
        writing_log("Информация", "DEBUG " + str(DEBUG))
        # Метод driver.get перенаправляет к странице URL в параметре.
        # WebDriver будет ждать пока страница не загрузится полностью (то есть, событие “onload” игнорируется), 
        # прежде чем передать контроль вашему тесту или скрипту. 
        driver.get(glob.start_url)
        print(1)
        writing_log("Информация", "Старт паузы для первоначальной загрузки страницы")
        sleep(glob.pause_load_page)
        #writing_log("Информация", "Продолжить после паузы")
        # Нахождение элемента выпадающего списка
        select = Select(driver.find_element(By.XPATH, "/html/body/sk-app/sk-external-template/div/div[2]/div/main/sk-participants/div/div/div[1]/div/div/sk-select/div/div/div/select"))
        #select = Select(driver.find_element(By.XPATH, "//select[@class=\"select ng-pristine ng-valid ng-touched\"]"))
        writing_log("Информация", "Найден select")
        # Выбор опции по индексу (Поставщик)
        select.select_by_index(2)
        writing_log("Информация", "Выбран select")
        # Нажатие кнопки "Найти"
        button = driver.find_element(By.XPATH, "/html/body/sk-app/sk-external-template/div/div[2]/div/main/sk-participants/div/div/div[4]/button[1]")
        #button = driver.find_element(By.XPATH, "//button[text()=\"Найти\"].")
        writing_log("Информация", "Найдена кнопка \"Найти\"")
        button.click()
        writing_log("Информация", "Нажата кнопка \"Найти\"")
        # Смещение стартовой страницы
        sleep(glob.pause_load_page)
        for i in range(glob.start_page - 1): 
            # Нажатие кнопки "Next"
            try:
                #btnNext = driver.find_element(By.XPATH, "/html/body/sk-app/sk-external-template/div/div[2]/div/main/sk-participants/div/div/div[6]/div[2]/ngb-pagination/ul/li[14]/a/span")
                #btnNext = driver.find_element(By.CLASS_NAME, "page-link")
                btnNext = driver.find_element(By.LINK_TEXT, "»")
                btnNext.click()
                writing_log("Информация", "Переход на страницу " + str(i + 1))
                # Задержка по времени для загрузки страницы
                writing_log("Информация", "Старт короткой паузы для переключения между страницами")
                sleep(glob.pause_flipping_shot)        
            except Exception as exception:
                #print(exception)
                writing_log("Ошибка", "main for i in range(glob.start_page - 1)\t" + str(exception))

        # Собственно цикл перебора страниц
        for i in range(glob.finish_page-glob.start_page + 1): 
            # Парсинг страницы
            parsing(glob.start_url) 
            # Нажатие кнопки "Next" для перехода на следующую страницу
            try:
                #btnNext = driver.find_element(By.XPATH, "/html/body/sk-app/sk-external-template/div/div[2]/div/main/sk-participants/div/div/div[6]/div[2]/ngb-pagination/ul/li[14]/a/span")
                #btnNext = driver.find_element(By.CLASS_NAME, "page-link")
                btnNext = driver.find_element(By.LINK_TEXT, "»")
                btnNext.click()
                writing_log("Информация", "Переход на страницу " + str(glob.start_page + (i + 1)))                
            except Exception as exception:
                #print(exception)
                writing_log("Ошибка", "main for i in range(glob.finish_page-glob.start_page)\t" +  str(exception))

        ## Список потоков
        #writing_log("Информация", "Старт потока")
        #threads = []
        #for i in range(glob.finish_page-glob.start_page + 1):
        #    # Создание потока
        #    thread = threading.Thread(target=parsing, args=(glob.start_url,))
        #    # Добавить поток в список
        #    threads.append(thread)
        #    # Запуск потока
        #    thread.start()
        #    # Нажатие кнопки "Next" для перехода на следующую страницу
        #    try:
        #        #btnNext = driver.find_element(By.XPATH, "/html/body/sk-app/sk-external-template/div/div[2]/div/main/sk-participants/div/div/div[6]/div[2]/ngb-pagination/ul/li[14]/a/span")
        #        #btnNext = driver.find_element(By.CLASS_NAME, "page-link")
        #        btnNext = driver.find_element(By.LINK_TEXT, "»")
        #        btnNext.click()
        #        writing_log("Информация", "Переход на страницу " + str(glob.start_page + (i + 1)))                
        #    except Exception as exception:
        #        #print(exception)
        #        writing_log("Ошибка", "main for i in range(glob.finish_page-glob.start_page)\t" +  str(exception))
        #for thread in threads:
        #    # Указать одному потоку дождаться завершения потока
        #    thread.join()     
        #writing_log("Информация", "Финиш потока")

        # Экспорт в Excel
        # Вызов: заголовок таблицы, данные, название файла
        current_date_time = datetime.now().strftime('%Y%m%d%H%M%S')
        export_to_excel(HEADER, glob.data, "zakup.kz.range(" +str(glob.start_page) + "-" + str(glob.finish_page) + ")_" +str(current_date_time) + ".xls")
        # Затраченное время
        writing_log("Информация", "Затраченное время:" + str(time.time() - start) + " секунд")
        # В завершение, окно браузера закрывается. Вы можете также вызывать метод quit вместо close. 
        # Метод quit закроет браузер полностью, в то время как close закроет одну вкладку. 
        #driver.quit()
    except Exception as exception:
        #print(exception)
        writing_log("Ошибка", "main\t" + str(exception))

###################################################################################################

# Список для изменения с кнопками создать, изменить, удалить
@login_required
@group_required("Managers")
def logfile_index(request):
    try:
        logfile = Logfile.objects.all().order_by('-datel')
        return render(request, "logfile/index.html", {"logfile": logfile,})
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# В функции create() получаем данные из запроса типа POST, сохраняем данные с помощью метода save()
# и выполняем переадресацию на корень веб-сайта (то есть на функцию index).
@login_required
@group_required("Managers")
def logfile_create(request):
    try:
        if request.method == "POST":
            logfile = Logfile()
        #    logfile.title = request.POST.get("title")
        #    logfileform = LogfileForm(request.POST)
        #    if logfileform.is_valid():
        #        logfile.save()
        #        return HttpResponseRedirect(reverse('logfile_index'))
        #    else:
        #        return render(request, "logfile/create.html", {"form": logfileform})
        #else:        
        #    logfileform = LogfileForm()
        #    return render(request, "logfile/create.html", {"form": logfileform})
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# Функция edit выполняет редактирование объекта.
@login_required
@group_required("Managers")
def logfile_edit(request, id):
    try:
        logfile = Logfile.objects.get(id=id)
        #if request.method == "POST":
        #    logfile.title = request.POST.get("title")
        #    logfileform = LogfileForm(request.POST)
        #    if logfileform.is_valid():
        #        logfile.save()
        #        return HttpResponseRedirect(reverse('logfile_index'))
        #    else:
        #        return render(request, "logfile/edit.html", {"form": logfileform})
        #else:
        #    # Загрузка начальных данных
        #    logfileform = LogfileForm(initial={'title': logfile.title, })
        #    return render(request, "logfile/edit.html", {"form": logfileform})
    except Logfile.DoesNotExist:
        return HttpResponseNotFound("<h2>Logfile not found</h2>")
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# Удаление данных из бд
# Функция delete аналогичным функции edit образом находит объет и выполняет его удаление.
@login_required
@group_required("Managers")
def logfile_delete(request, id):
    try:
        logfile = Logfile.objects.get(id=id)
        logfile.delete()
        return HttpResponseRedirect(reverse('logfile_index'))
    except Logfile.DoesNotExist:
        return HttpResponseNotFound("<h2>Logfile not found</h2>")
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# Просмотр страницы read.html для просмотра объекта.
@login_required
def logfile_read(request, id):
    try:
        logfile = Logfile.objects.get(id=id) 
        return render(request, "logfile/read.html", {"logfile": logfile})
    except Logfile.DoesNotExist:
        return HttpResponseNotFound("<h2>Logfile not found</h2>")
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

###################################################################################################

# Регистрационная форма 
def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return HttpResponseRedirect(reverse('index'))
            #return render(request, 'registration/register_done.html', {'new_user': user})
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})

# Изменение данных пользователя
@method_decorator(login_required, name='dispatch')
class UserUpdateView(UpdateView):
    model = User
    fields = ('first_name', 'last_name', 'email',)
    template_name = 'registration/my_account.html'
    success_url = reverse_lazy('index')
    #success_url = reverse_lazy('my_account')
    def get_object(self):
        return self.request.user


