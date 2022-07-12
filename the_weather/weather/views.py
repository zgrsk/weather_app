import requests
from django.shortcuts import render, redirect
from .models import City
from .forms import CityForm


def index(request):
    url = 'https://api.openweathermap.org/data/2.5/weather?q={}&appid=fd232b0fbbb583827e8763f0213076e2&units=metric&lang=ru'

    err_msg = ''
    message = ''
    message_class = ''

    # Если данный запрос типа POST, тогда
    if request.method == 'POST':
        # Создаём экземпляр формы и заполняем данными из запроса
        form = CityForm(request.POST)

        # Проверка валидности данных формы
        if form.is_valid():
            # Обработка данных из form.cleaned_data
            # (здесь мы просто присваиваем их new_city)
            new_city = form.cleaned_data['name']
            existing_city_count = City.objects.filter(name=new_city).count()

            # Проверяем есть ли введенный город в списке
            if existing_city_count == 0:
                r = requests.get(url.format(new_city)).json()
                if r['cod'] == 200:
                    form.save()
                else:
                    err_msg = 'Такого города не существует!' # Ошибка для города, которого не существует вообще
            else:
                err_msg = 'Город уже добавлен в список!'

        if err_msg:
            message = err_msg
            message_class = 'is-danger'
        else:
            message = 'Город успешно добавлен!'
            message_class = 'is-success'

    print(err_msg)

    # Выборка данных погоды, которая будет отображена на странице
    form = CityForm()
    cities = City.objects.all()
    weather_data = []
    for city in cities:
        r = requests.get(url.format(city)).json()
        city_weather = {
            'city': city.name,
            'temperature': r['main']['temp'],
            'description': r['weather'][0]['description'],
            'icon': r['weather'][0]['icon'],
        }

        weather_data.append(city_weather)

    context = {
        'weather_data': weather_data,
        'form': form,
        'message': message,
        'message_class': message_class,
    }
    return render(request, 'weather/weather.html', context)

# Создание функции удаления города
def delete_city(request, city_name):
    City.objects.get(name=city_name).delete()
    return redirect('home')
