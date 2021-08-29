from flask import Flask, render_template, request, redirect, url_for, flash, abort, session, jsonify #Blueprint
# 1) render_template - для генерации и вывода шаблонов хтмл
# 2) request - (request.form[имя поля в html-документе])
# ....
# 7) session - для сохранения параметров(типа куки, т.е. сессии пользователя)
# 8) jsonify - отличный инструмент фласка, принимает строки и преобразует их в json

import json
# импортируем библитеку ос.пат для проверки существует файл или нет
import os.path
from werkzeug.utils import secure_filename

# bp = Blueprint("urlshort", __name__) - не встала в этом приложении даже на Убунту

app = Flask(__name__)
app.secret_key = b"h1h2h2jdowoefhjdkf"

# app.register_blueprint(urlshort.bp)
app.url_map.strict_slashes = False

# добавляем strict_slashes в False, чтобы localhost:500/about и localhost:500/about/ отдавало 1 страницу
# bp.url_map.strict_slashes = False


@app.route('/')
def home():
    return render_template("home.html", codes=session.keys())


# methods=['POST', 'GET'] - задаем явно 2 метода обработки для фласка, пост и гет
@app.route('/your-url', methods=['POST', 'GET'])
def your_url():
    if request.method == 'POST':
        urls = {}
        if os.path.exists("../url.json"):
            with open('../url.json') as url_file:
                urls = json.load(url_file)

        if request.form['code'] in urls.keys():
            flash("That short name has already been taken. Please select another name")
            return redirect(url_for('home'))

        if 'url' in request.form.keys():
            urls[request.form['code']] = {'url': request.form['url']}
        else:
            f = request.files['file']
            full_name = request.form['code'] + "_" + secure_filename(f.filename)
            f.save("/static/user_files/" + full_name)
            urls[request.form['code']] = {'file': full_name}

        with open('../url.json', 'w') as url_file:
            json.dump(urls, url_file)  # urls - то что сохраняем, url_file - то куда сохраняем
            session[request.form['code']] = True

        return render_template("your_url.html", code=request.form['code'])
    else:
        return redirect(url_for('home'))


# request.args['code'] содержит в себе словарь с нашими названиями полей с формы, которые мы отправили на сервер
# при методе post, уже нужно использовать request.form['code'] с данными из нашей формы

# объявляем шаблон, роут зависит от того что ввел пользователь <тип строка：переменная>
@app.route('/<string:code>')
def redirect_to_url(code):
    if os.path.exists('../url.json'):
        with open('../url.json', 'r') as urls_file:
            urls = json.load(urls_file)
            if code in urls.keys():
                if 'url' in urls[code].keys():
                    return redirect(urls[code]['url'])
                else:
                    return redirect(url_for('static', filename="user_files/" + urls[code]['file']))
    return abort(404)


# теперь мы можем опрделить route для ошибок(ошибка в скобках), как наш роут, и задать ему кастом

@app.errorhandler(404)
def page_not_found(error):
    return render_template('page_not_found.html'), 404

# api - встроенный роут и метод фласк, на его основе можно создать API сервис с продвинутым функционалом
@app.route('/api')
def session_api():
    return jsonify(list(session.keys())) # оборачиваем в ф-ю jsonify c 1м аргументом -ключи, и на выходе получаем JSON


if __name__ == '__main__':
    app.run()

