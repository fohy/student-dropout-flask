from flask import Flask, render_template, request, send_file
import pandas as pd
import requests
import os
import logging
from io import StringIO


logger = logging.getLogger(__name__)

app = Flask(__name__)


MODEL_SERVER_URL = 'https://student-dropout-fastapi.onrender.com'


FEATURE_COLUMNS = [
    'Приоритет', 'Cумма баллов испытаний', 'БВИ', 'Балл за инд. достижения',
    'Категория конкурса БВИ', 'Контракт', 'Нуждается в общежитии',
    'Иностранный абитуриент (МОН)', 'Пол', 'Прошло лет с окончания уч. заведения',
    'FromEkaterinburg', 'Human Development Index', 'Полных лет на момент поступления',
    'Особая квота', 'Отдельная квота', 'Целевая квота',
    'всероссийская олимпиада школьников (ВОШ)',
    'олимпиада из перечня, утвержденного МОН РФ (ОШ)', 'Заочная', 'Очно-заочная',
    'Военное уч. заведение', 'Высшее', 'Профильная Школа', 'СПО', 'Боевые действия',
    'Инвалиды', 'Квота для иностранных граждан', 'Сироты', 'PostSoviet', 'others',
    'Код направления 1: 10', 'Код направления 1: 11', 'Код направления 1: 27',
    'Код направления 1: 29', 'Код направления 3: 2', 'Код направления 3: 3',
    'Код направления 3: 4'
]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/team')
def team():
    return render_template('team.html')

@app.route('/predict', methods=['GET', 'POST'])
def predict():
    logger.debug(f"Получен запрос: {request.method} /predict")
    if request.method == 'POST':
        try:
            if 'file' not in request.files:
                return render_template('prediction.html', 
                                    error="Файл не загружен",
                                    show_results=False,
                                    feature_columns=FEATURE_COLUMNS)
            
            file = request.files['file']
            if file.filename == '':
                return render_template('prediction.html', 
                                    error="Файл не выбран",
                                    show_results=False,
                                    feature_columns=FEATURE_COLUMNS)

            data = pd.read_csv(file, sep=';')
            
            missing_cols = [col for col in FEATURE_COLUMNS if col not in data.columns]
            if missing_cols:
                return render_template('prediction.html',
                                    error=f"Отсутствуют колонки: {missing_cols}",
                                    show_results=False,
                                    feature_columns=FEATURE_COLUMNS)

            request_data = {
                "education_level": request.form.get('education_level', 'bak_spec'),
                "data": data[FEATURE_COLUMNS].to_dict(orient='records')
            }

            response = requests.post(
                f"{MODEL_SERVER_URL}/predict",
                json=request_data,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )

            response.raise_for_status() 
            result = response.json()
            
            data['prediction'] = result['predictions']
            result_csv = data.to_csv(index=False, sep=';')
            
            with open('results.csv', 'w', encoding='utf-8') as f:
                f.write(result_csv)
                
            return render_template('prediction.html',
                                result_html=data.to_html(classes='table table-striped', index=False),
                                show_results=True,
                                error=None,
                                feature_columns=FEATURE_COLUMNS)

        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка запроса к FastAPI: {str(e)}")
            return render_template('prediction.html',
                                error=f"Ошибка соединения с сервером модели: {str(e)}",
                                show_results=False,
                                feature_columns=FEATURE_COLUMNS)
            
        except Exception as e:
            logger.error(f"Ошибка обработки: {str(e)}", exc_info=True)
            return render_template('prediction.html',
                                error=f"Ошибка обработки: {str(e)}",
                                show_results=False,
                                feature_columns=FEATURE_COLUMNS)

    return render_template('prediction.html', 
                         show_results=False, 
                         error=None, 
                         feature_columns=FEATURE_COLUMNS)

@app.route('/download_results')
def download_results():
    try:
        return send_file('results.csv',
                         mimetype='text/csv',
                         as_attachment=True,
                         download_name='predictions.csv')
    except Exception as e:
        logger.error(f"Ошибка скачивания файла: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
