from optparse import OptionParser

from lib import chart_generating
from lib import contamination_tracking
from lib import data_processing
from lib import file_operations

# from flask import Flask 
# from flask_cors import CORS, cross_origin
 
# app = Flask(__name__)
# cors = CORS(app)
# app.config['CORS_HEADERS'] = 'Content-Type'

# @app.route('/tracking', methods=["POST"])
# @cross_origin()

def parse_terminal_options():
    # a função gera padrões de parâmetros a serem analisados e retorna o resultado final

    parser = OptionParser()
    parser.add_option("-s", "--save-csv", action="store_true", dest="save_csv", default=False, help="Define se os dados brutos tratados serão salvos ou não")
    parser.add_option("-f", "--use-flask", action="store_true", dest="use_flask", default=False, help="Define se o Flask será usado ou não")
    parser.add_option("-l", "--load-option", type="string", dest="load_option", default="csv", help="Padrão: \"csv\". Seleciona a forma como os dados serão obtidos, por csv, dados anonimizados, ou por excel, dados brutos")
    parser.add_option("-t", "--simulate-tracking", action="store_true", dest="simulate_tracking", default=False, help="Define se a simulação será executada ou não")
    parser.add_option("-c", "--generate-charts", action="store_true", dest="generate_charts", default=False, help="Define se os gráficos com os resultados da simulação serão gerados ou não")
    parser.add_option("-e", "--extra-data", action="store_true", dest="extras", default=False, help="Define se informações extras devem ser salvas")

    return parser.parse_args()

def load_data(load_option):
    load_options = {
        "csv": file_operations.load_anonymized_data_from_csv_files,
        "excel": data_processing.get_processed_data
    }

    data = load_options[load_option]()

    return data

def save_processed_data(save_data, data):
    if save_data == True:
        file_operations.save_structures_to_csv_files(data)

def main():
    (opt, _) = parse_terminal_options()

    data = load_data(opt.load_option)
    save_processed_data(opt.save_csv, data)

    if opt.simulate_tracking == True:
        contamination_tracking.simulate_tracking(data)
    
    if opt.generate_charts == True:
        chart_generating.generate_charts_based_on_statistics(data)

    if opt.extras == True:    
        students_by_courses = data_processing.count_students_by_course(data)
        data_processing.get_classes_predominance(data, list(students_by_courses.keys()))
        data_processing.count_classroom_types(data)

if __name__ == "__main__":
    main()
