from flask import Blueprint, render_template, request, send_from_directory
from .app_functions import ValuePredictor, pred
import os
from werkzeug.utils import secure_filename

prediction = Blueprint('prediction', __name__)

UPLOAD_FOLDER = 'uploads'
STATIC_FOLDER = 'static'

dir_path = os.path.dirname(os.path.realpath(__file__))

# Diccionarios para las enfermedades y sus mensajes
enfermedades_dict = {
    'liver': 'hígado',
    'kidney': 'riñón',
    'diabete': 'diabetes',
    'stroke': 'derrame cerebral',
    'heart': 'corazón'
}

# Mensajes para cada enfermedad en español
mensajes_dict = {
    'liver': {
        0: "¡No te preocupes! Tu hígado está en buen estado. No hay señales de riesgo en este momento.",
        1: "Lamentablemente, parece que estás en riesgo de contraer una enfermedad hepática. Te recomendamos que sigas de cerca tu salud y consultes a un especialista."
    },
    'kidney': {
        0: "¡Todo está bien! Tus riñones están saludables, no hay señales de riesgo en este momento.",
        1: "Lo siento, parece que estás en riesgo de padecer problemas renales. Es importante que sigas las indicaciones médicas."
    },
    'diabete': {
        0: "Tu nivel de glucosa está bajo control. No hay señales de diabetes en este momento.",
        1: "Lamentablemente, estás en riesgo de desarrollar diabetes. Se recomienda hacerte más estudios para confirmarlo."
    },
    'stroke': {
        0: "¡No hay de qué preocuparse! No presentas síntomas de un derrame cerebral.",
        1: "Lamentablemente, estás en riesgo de sufrir un derrame cerebral. Es muy importante que tomes medidas preventivas y consultes a tu médico."
    },
    'heart': {
        0: "¡Todo está bien! Tu corazón está saludable y no hay signos de problemas.",
        1: "Parece que estás en riesgo de sufrir problemas cardíacos. Consulta a tu médico para una evaluación más detallada."
    }
}

@prediction.route('/predict', methods=["POST", 'GET'])
def predict():

    if request.method == "POST":
        to_predict_list = request.form.to_dict()
        to_predict_list = list(to_predict_list.values())
        to_predict_list = list(map(float, to_predict_list))
        result, page = ValuePredictor(to_predict_list)

        # Usamos el diccionario para obtener los mensajes según la predicción
        enfermedad = enfermedades_dict.get(page, 'enfermedad desconocida')  # En caso de que no se reconozca la página
        mensaje = mensajes_dict.get(page, {}).get(result, 'Mensaje no disponible')  # Mensaje de la enfermedad según el resultado
        
        return render_template("result.html", prediction=result, page=page, enfermedad=enfermedad, mensaje=mensaje)
    
    else:
        return render_template('base.html')

@prediction.route('/upload', methods=['POST','GET'])
def upload_file():
    if request.method == "GET":
        return render_template('pneumonia.html', title='Pneumonia Disease')
    else:
        file = request.files["file"]
        basepath = os.path.dirname(__file__)
        file_path = os.path.join(basepath, 'uploads', secure_filename(file.filename))
        file.save(file_path)
        indices = {0: 'Normal', 1: 'Pneumonia'}
        result = pred(file_path)

        if result > 0.5:
            label = indices[1]
            accuracy = result * 100
        else:
            label = indices[0]
            accuracy = 100 - result
        return render_template('deep_pred.html', image_file_name=file.filename, label=label, accuracy=accuracy)

@prediction.route('/uploads/<filename>')
def send_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)
