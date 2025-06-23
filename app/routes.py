import os
from flask import render_template, request, redirect, url_for, jsonify, flash, send_file, make_response
from . import db
from .models import User, Patient, Event
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import requests


def init_routes(app):
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    @app.route('/')
    def index():
        return render_template('index.html', current="index")
    
    @app.route('/users')
    @login_required
    def users():
        users = User.query.all()
        return render_template('users.html', current="users", users=users)

    @app.route('/user/add', methods=["GET", "POST"])
    @login_required
    def user_add():
        if request.method == "GET":
            return render_template('user/add.html', current="users")
        if request.method == "POST":
            user = User()
            user.username = request.form["username"]
            user.password = request.form["password"]
            user.name = request.form["name"]
            user.sur_name = request.form["sur-name"]
            user.position = request.form["position"]
            user.telegram_id = request.form["telegram_id"]
            db.session.add(user)
            db.session.commit()
            return redirect("/users")

    @app.route('/user/edit/<id>', methods=["GET", "POST"])
    @login_required
    def user_edit(id):
        if request.method == "GET":
            user = db.get_or_404(User, id)
            return render_template('user/edit.html', current="users", user=user)
        if request.method == "POST":
            user = db.get_or_404(User, request.form["id"])
            user.username = request.form["username"]
            user.password = request.form["password"]
            user.name = request.form["name"]
            user.sur_name = request.form["sur-name"]
            user.position = request.form["position"]
            user.telegram_id = request.form["telegram_id"]
            db.session.commit()
            return redirect("/users")

    @app.route('/user/del/<id>', methods=["GET", "POST"])
    @login_required
    def user_del(id):
        if request.method == "GET":
            user = db.get_or_404(User, id)
            return render_template('user/del.html', current="users", user=user)
        if request.method == "POST":
            user = db.get_or_404(User, request.form["id"])
            db.session.delete(user)
            db.session.commit()
            return redirect("/users")

    @app.route('/patients')
    @login_required
    def patients():
        patients = Patient.query.all()
        return render_template('patients.html', current="patients", patients=patients)

    @app.route('/patient/add', methods=["GET", "POST"])
    @login_required
    def patient_add():
        if request.method == "GET":
            return render_template('patient/add.html', current="patients")
        if request.method == "POST":
            patient = Patient()
            patient.name = request.form["name"]
            patient.sur_name = request.form["sur-name"]
            patient.data_of_birth = request.form["data-of-birth"]
            db.session.add(patient)
            db.session.commit()
            return redirect("/patients")

    @app.route('/patient/edit/<id>', methods=["GET", "POST"])
    @login_required
    def patient_edit(id):
        if request.method == "GET":
            patient = db.get_or_404(Patient, id)
            return render_template('patient/edit.html', current="patients", patient=patient)
        if request.method == "POST":
            patient = db.get_or_404(Patient, request.form["id"])
            patient.name = request.form["name"]
            patient.sur_name = request.form["sur-name"]
            patient.data_of_birth = request.form["data-of-birth"]
            db.session.commit()
            return redirect("/patients")

    @app.route('/patient/del/<id>', methods=["GET", "POST"])
    @login_required
    def patient_del(id):
        if request.method == "GET":
            patient = db.get_or_404(Patient, id)
            return render_template('patient/del.html', current="patients", patient=patient)
        if request.method == "POST":
            patient = db.get_or_404(Patient, request.form["id"])
            db.session.delete(patient)
            db.session.commit()
            return redirect("/patients")
    
    @app.route('/patient/photo-edit/<id>', methods=["GET", "POST"])
    def patient_photo_edit(id):
        if request.method == "GET":
            patient = db.get_or_404(Patient, id)
            return render_template('patient/add_photo.html', current="patients", patient=patient)
        if request.method == "POST":
            print("Hi")
            # Проверяем, есть ли файл в запросе
            if 'photo' not in request.files:
                flash('No file part')
                return redirect("/patients")
        
            file = request.files['photo']
            print(file)
        
            # Если пользователь не выбрал файл
            if file.filename == '':
                flash('No selected file')
                return redirect("/patients")
            
            def allowed_file(filename):
                return '.' in filename and filename.rsplit('.', 1)[1].lower() in {"jpg"}
            
            # Если файл разрешен и корректен
            if file and allowed_file(file.filename):
                if not os.path.exists(app.config['IMGS']):
                    os.makedirs(app.config['IMGS'])
                file.save(os.path.abspath(os.path.join(app.config['IMGS'], f"{id}.jpg")))
                return redirect("/patients")
    
        return redirect("/patients")

    @app.route('/patient/photo/<id>', methods=["GET", "POST"])
    def patient_photo(id):
        if request.method == "GET":
            patient = db.get_or_404(Patient, id)
            if os.path.isfile(os.path.join(app.config['IMGS'], f"{id}.jpg")):
                return send_file(os.path.abspath(os.path.join(app.config['IMGS'], f"{id}.jpg")), as_attachment=True)
            else:
                return make_response(f"File '{id}' not found.", 404)

    # @app.route('/patients/json')
    # def patients_all():
    #     patients = Patient.query.all()
    #     result = []
    #     for patient in patients:
    #         patients_dict = patient.__dict__
    #         patients_dict.pop('_sa_instance_state', None)  # Удаляем служебное поле SQLAlchemy
    #         result.append(patients_dict)
    #     return jsonify(result)

    @app.route('/events')
    @login_required
    def events():
        events = Event.query.all()
        
        return render_template('events.html', current="events", events=events)

    # @app.route('/event/add', methods=["GET", "POST"])
    # def event_add():
    #     if request.method == "POST":
    #         event = Event()
    #         event.name = request.json["name"]
    #         event.description = request.json["description"]
    #         db.session.add(event)
    #         db.session.commit()
    #         send_event_telegram(event)
    #         return make_response("", 200)
        
    @app.route('/event/add', methods=["GET", "POST"])
    @login_required
    def event_add():
        if request.method == "GET":
            return render_template('event/add.html', current="events")
        if request.method == "POST":
            event = Event()
            event.name = request.form["name"]
            event.description = request.form["description"]
            db.session.add(event)
            db.session.commit()
            return redirect("/events")
        
    @app.route('/event/edit/<id>', methods=["GET", "POST"])
    @login_required
    def event_edit(id):
        if request.method == "GET":
            event = db.get_or_404(Event, id)
            return render_template('event/edit.html', current="events", event=event)
        if request.method == "POST":
            event = db.get_or_404(Event, request.form["id"])
            event.name = request.form["name"]
            event.description = request.form["description"]
            db.session.commit()
            return redirect("/events")

    @app.route('/event/del/<id>', methods=["GET", "POST"])
    @login_required
    def event_del(id):
        if request.method == "GET":
            event = db.get_or_404(Event, id)
            return render_template('event/del.html', current="events", event=event)
        if request.method == "POST":
            event = db.get_or_404(Event, request.form["id"])
            db.session.delete(event)
            db.session.commit()
            return redirect("/events")
    

    def send_event_telegram(event):
        users = User.query.all()
        msg = f"{event.name}\n{event.description}"
        url = f"http://{app.config['TELEGRAM_URL']}/send_notification"
        headers = {"X-API-KEY": app.config['TELEGRAM_API_KEY']}
        for user in users:
            if user.telegram_id == None : continue
            data = {
                "user_id": user.telegram_id,  # ID пользователя из Telegram
                "message": msg
            }
            try:
                response = requests.post(url, json=data, headers=headers)
                if response.status_code != 200:
                    print(f"Ошибка отправки сообщения {data}")
            except requests.exceptions.ConnectionError as e:
                print(f"Ошибка подключения к Telegram Bot")
    
    @app.route('/events/json')
    def events_all():
    # Получаем все события из базы данных
        events = Event.query.all()
    
    # Преобразуем в список словарей
        result = []
        for event in events:
            event_dict = {
                'id': event.id,
                'name': event.name,
                'description': event.description
            }
        result.append(event_dict)
    
        return jsonify(result)

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for('home'))
    
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
        
            user = User.query.filter_by(username=username, password=password).first()
            
            if user:
                login_user(user, remember=True)
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect("/")
            else:
                password_error = Event.query.filter_by(name="Пользователь не найден").first()
            
            # Если событие найдено - берем описание, иначе текст по умолчанию
                error_message = password_error.name if password_error else 'Неверное имя пользователя или пароль'
                flash(error_message, 'danger')
        return render_template('login.html')
    
    
    

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        return redirect("/")