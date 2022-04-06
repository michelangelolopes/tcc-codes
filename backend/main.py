import datetime
from fileinput import filename
import math
import matplotlib.pyplot as plt
import os
import numpy
import pandas as pd
import seaborn as sns
from itertools import combinations
from matplotlib.ticker import FuncFormatter
from optparse import OptionParser

from lib import classes
from lib import data_processing
from lib import file_operations

from flask import Flask, request
from flask_cors import CORS, cross_origin
 
# app = Flask(__name__)
# cors = CORS(app)
# app.config['CORS_HEADERS'] = 'Content-Type'

def parse_terminal_options():
    # a função gera padrões de parâmetros a serem analisados e retorna o resultado final

    parser = OptionParser()
    parser.add_option("-c", "--save-csv", action="store_true", dest="save_csv", default=False, help="Define se os dados serão salvos ou não")
    parser.add_option("-f", "--use-flask", action="store_true", dest="use_flask", default=False, help="Define se o Flask será usado ou não")
    parser.add_option("-d", "--load-data", type="string", dest="load_data", default="csv", help="Seleciona a forma como os dados serão obtidos, por csv ou por excel")

    return parser.parse_args()

def wells_riley_equation(param):
    # calcula a probabilidade de contaminação por um vírus transmissível pelo ar, dados os parâmetros informados no dict param

    infection_probability = []

    for ventilation_rate in param['ventilation_rates']:
        ventilation_volume = param['room_volume'] * ventilation_rate
        
        n = (param['infectors_count'] * param['quantum_generation_rate'] * param['breathing_rate'] * param['duration_time'])
        n *= (1 - param['infector_mask']) * (1 - param['susceptible_mask'])
        n /= ventilation_volume

        infection_probability.append(1 - math.exp(-n))

    return infection_probability

def get_incubation_days(informed_day, incubation_interval):
    days = [1, 2, 3, 4, 5, 6, 7]
    week_days = [2, 3, 4, 5, 6]

    incubation_days = []

    # intervalos recebem os valores dos índices, o que permite a utilização da funcionalidade de índices negativos do python
    
    count = 0
    while count < incubation_interval:
        index = informed_day - (incubation_interval + count)

        if days[index] in week_days:
            incubation_days.append(days[index])

        count += 1
    
    # dia que os sintomas apareceram --- dias a serem analisados (serão ignorados sábado e domingo) --- 4 dias de incubação
    # 2 --- 5671
    # 3 --- 6712
    # 4 --- 7123
    # 5 --- 1234
    # 6 --- 2345

    return incubation_days

def calculate_contamination_prob_from_one_infector(room_mapping, academics_mapping, classrooms, infected_academic, incubation_days, equation_params):
    # assumindo que o acadêmico fez o teste no primeiro dia que sentiu os sintomas da covid e informou que estava contaminado
    
    # pessoas que estiveram na mesma sala de alguém infectado
    affected_academics = []

    # segunda a sexta
    for day in incubation_days:
        for hour in room_mapping[day]:
            for classroom in room_mapping[day][hour]:
                component_code, component_class = room_mapping[day][hour][classroom]

                if infected_academic in academics_mapping[component_code][component_class]:
                    # print(day, hour, classroom, component_code, component_class)
                    current_classroom = data_processing.find_class_instance_by_id(classroom, classrooms)
                    count_infected = 1

                    for academic in academics_mapping[component_code][component_class]:
                        if academic not in affected_academics and academic != infected_academic:
                            affected_academics.append(academic)
                    
                    equation_params['infectors_count'] = count_infected
                    equation_params['room_volume'] = current_classroom.type.volume
                    classroom_contamination_prob = wells_riley_equation(equation_params)

                    for academic in academics_mapping[component_code][component_class]:
                        if academic != infected_academic:
                            if academic.infection_probability == []:
                                for _ in range(0, 6): # são 6 casos do artigo do park
                                    academic.infection_probability.append([])
                            for case in range(0, 6): 
                                academic.infection_probability[case].append(classroom_contamination_prob[case])

    for affected_academic in affected_academics:
        for case in range(0, 6):
            case_combination_prob = combination_probability(affected_academic.infection_probability[case])
            affected_academic.comb_prob.append(case_combination_prob)
    # print_affected_academics_contamination_prob(affected_academics)
    return affected_academics

def combination_probability(prob_list):
    
    prob_indexes = [index for index in range(0, len(prob_list))]

    comb_prob_all = 0
    for n_comb in range(1, len(prob_list) + 1):
        comb_list = combinations(prob_indexes, n_comb)
        comb_list = list(comb_list)

        for comb in comb_list:
            comb_prob = 1
            comb_prob = math.prod(list(map(lambda index: prob_list[index], comb))) #multiplica todas as probabilidades baseadas em seus índices
            not_comb = [index for index in prob_indexes if index not in comb] #pega os índices dos elementos que não estavam na lista de combinações
            not_comb = list(map(lambda index: prob_list[index], not_comb))
            
            for elem in not_comb:
                comb_prob *= (1 - elem)

            comb_prob_all += comb_prob

    return comb_prob_all

def print_affected_academics_contamination_prob(affected_academics):
    for affected_academic in affected_academics:
        for case in range(0, 6):
            print("%s (%s)\t\tcaso %d\t\t%f" % (affected_academic.academic_id, affected_academic.id, case + 1, affected_academic.comb_prob[case]))
        print("----------------------------------------------------------------------------------------------")

def get_mask_efficiency(mask_type):
    mask_dict = {
        'no_mask': 0,
        'surgery_mask': 0.5,
        'n95_mask': 0.95
    }

    return mask_dict[mask_type]

def get_weekday_by_date(datetime_str):
    date_format = '%Y-%m-%d'
    date_str = datetime_str.split('T')[0] # sobra apenas a data, sem o tempo

    datetime_obj = datetime.datetime.strptime(date_str, date_format)
    
    return datetime_obj.weekday()

def get_ventilation_rates_from_file():
    filename = "ventilation_rates"
    with open(filename, "r") as file:
        ventilation_rates = file.readlines()
    
    ventilation_rates = [float(value.replace("\n", "")) for value in ventilation_rates]

    return ventilation_rates

def load_and_save_data(load_option, save_data):
    load_data_option = {
        "csv": file_operations.load_anonymized_data_from_csv_files,
        "excel": data_processing.get_processed_data
    }

    data = load_data_option[load_option]()

    if save_data == True:
        file_operations.save_structures_to_csv_files(data)

    return data

def get_informed_params(use_flask):
    if use_flask == True:
        post_param = request.get_json()
        informed_id = post_param['id']
        informed_day = get_weekday_by_date(post_param['date'])
        informed_mask = get_mask_efficiency(post_param['mask'])
        params = [informed_id, informed_day, informed_mask]
    else:
        informed_id, informed_day, informed_mask = file_operations.load_parameters_from_txt_file("lib/info.txt")
        params = [informed_id, int(informed_day), float(informed_mask)]

    return params

def set_contaminated_academic(academic):
    academic.has_covid = True
    academic.can_transmit = True
    academic.infected_days = 0

# @app.route('/tracking', methods=["POST"])
# @cross_origin()
def simulate_tracking(data):
    room_mapping, academics_mapping, academics, professors, students, _, classrooms = data

    equation_params = {
        'quantum_generation_rate': 48, # foi o máximo de quanta para a covid 19, segundo o artigo do park (2021)
        'breathing_rate': 0.3, # segundo o artigo de park (2021) é a taxa de respiração de uma pessoa em repouso
        'duration_time': 2, # considerando que as aulas sempre durem 2 horas
        'ventilation_rates': get_ventilation_rates_from_file(),
        'infector_mask': 0,
        'susceptible_mask': 0
    }

    file = open("results.csv", "w")
    file.write("academic_id;notification_day;mask_type;affected_people_count")
    
    for index in range(1, 7):
        file.write(";case_%d" % index)
    
    file.write("\n")

    days = [3, 4, 5, 6, 7, 1]

    for informed_id in academics:
        for informed_day in days:
            for mask_type in ["no_mask", "surgery_mask", "n95_mask"]:
                # print(informed_id, informed_day)
                # informed_id, informed_day, informed_mask = get_informed_params(opt.use_flask)
                infected_academic = data_processing.find_class_instance_by_academic_id(informed_id, academics, professors, students)

                # ignorando dias de fim de semana
                incubation_days = get_incubation_days(informed_day, incubation_interval = 2)

                equation_params["infector_mask"] = get_mask_efficiency(mask_type)
                equation_params["susceptible_mask"] = get_mask_efficiency(mask_type)
                affected_academics = calculate_contamination_prob_from_one_infector(room_mapping, academics_mapping, classrooms, infected_academic, incubation_days, equation_params)

                average = [0] * 6
                count_affected = len(affected_academics)
                
                if count_affected != 0:
                    for affected_academic in affected_academics:
                        for case in range(0, 6):
                            average[case] += affected_academic.comb_prob[case]
                        
                        affected_academic.infection_probability = []
                        affected_academic.comb_prob = []
                    for case in range(0, 6):
                        average[case] /= count_affected

                # print(average)
                file.write("%s;%d;%s;%d" % (informed_id, informed_day, mask_type, count_affected))
                for case in range(0, 6):
                    file.write(";%f" % average[case])
                file.write("\n")
                file.flush()
                os.fsync(file)
    file.close()

def weighted_std(df, values_column, weights_column, average_column):
    """
    Return the weighted average and standard deviation.

    values, weights -- Numpy ndarrays with the same shape.
    """
    values = df[values_column]
    weights = df[weights_column]
    average = df[average_column]
    # average = numpy.average(values, weights=weights)
    # Fast and numerically precise:
    variance = numpy.average((values - average)**2, weights = weights)
    return math.sqrt(variance)

def weighted_avg(df, values_column, weights_column):
    values = df[values_column]
    weights = df[weights_column]
    
    return (values * weights).sum() / weights.sum()

def get_dataframe_dict_to_calculate_average(df, choosed_column):
    df_masks = df.groupby(["mask_type"])
    
    df_dict = {}
    for mask_type, df_mask in df_masks:
        df_dict[mask_type] = df_mask.groupby([choosed_column])

    return df_dict

def get_dataframe_series_dict_with_calculated_averages(df_dict):
    series_dict = {}

    for index in range(1, 7):
        for mask_type in df_dict:
            current_case = "case_%d" % index
            average_case_series = df_dict[mask_type].apply(weighted_avg, current_case, "affected_people_count")
            
            if index not in series_dict:
                series_dict[index] = {}
            
            if mask_type not in series_dict[index]:
                series_dict[index][mask_type] = average_case_series
    
    return series_dict

def generate_dataframe_series_dict_plot(case_df, case_index, filetype, path, choosed_column):
    final_df = case_df.melt(id_vars=[choosed_column])

    plot = sns.barplot(x=choosed_column, y="value", hue='variable', data=final_df)
    plot.set_xlabel("Dia da notificação")
    plot.set_ylabel("Probabilidade média de contaminação no Caso " + str(case_index))
    plot.yaxis.set_major_formatter(FuncFormatter(lambda y, _: '{:.1%}'.format(y))) 
    legend = plt.legend(bbox_to_anchor=(1.02, 0.8), borderaxespad=0, title="Tipo de máscara")

    filename = path + "case_" + str(case_index) + "." + filetype
    figure = plot.get_figure()
    figure.savefig(filename, bbox_extra_artists=(legend,), bbox_inches='tight')
    plt.close()

def generate_graphs_by_day_average(df, filetype):
    choosed_column = "notification_day"
    path = './images/days/'

    df_dict = get_dataframe_dict_to_calculate_average(df, choosed_column)
    series_dict = get_dataframe_series_dict_with_calculated_averages(df_dict)
    
    named_days = ["Domingo", "Terça", "Quarta", "Quinta", "Sexta", "Sábado"]
    reordered_named_days = ["Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]

    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)
        
    for case_index in range(1, 7):
        case_df = pd.DataFrame(index=named_days)
        case_df["Sem máscara"] = series_dict[case_index]["no_mask"].values
        case_df["Máscara Cirúrgica"] = series_dict[case_index]["surgery_mask"].values
        case_df["Máscara N95"] = series_dict[case_index]["n95_mask"].values

        case_df = case_df.loc[reordered_named_days]
        case_df.reset_index(inplace=True)
        case_df.rename(columns={'index': choosed_column}, inplace=True)

        generate_dataframe_series_dict_plot(case_df, case_index, filetype, path, choosed_column)

def generate_graphs_by_professor_student_average(df, filetype, professors_ids, students_ids):
    new_df = df.copy().assign(professor_student='')
    new_df.loc[new_df["academic_id"].isin(professors_ids), 'professor_student'] = 'professor'
    new_df.loc[new_df["academic_id"].isin(students_ids), 'professor_student'] = 'student'

    choosed_column = "professor_student"
    path = './images/people/'

    df_dict = get_dataframe_dict_to_calculate_average(new_df, choosed_column)
    series_dict = get_dataframe_series_dict_with_calculated_averages(df_dict)

    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)
        
    for case_index in range(1, 7):
        case_df = pd.DataFrame()
        case_df[choosed_column] = ["professor", "student"]
        case_df["Sem máscara"] = series_dict[case_index]["no_mask"].values
        case_df["Máscara Cirúrgica"] = series_dict[case_index]["surgery_mask"].values
        case_df["Máscara N95"] = series_dict[case_index]["n95_mask"].values

        generate_dataframe_series_dict_plot(case_df, case_index, filetype, path, choosed_column)

def get_professors_students_academic_id(academics):
    professors_ids = []
    students_ids = []

    for academic_id in academics:
        if academics[academic_id][0] == '':
            students_ids.append(academic_id)

        if academics[academic_id][1] == '':
            professors_ids.append(academic_id)

    return professors_ids, students_ids

def get_students_by_courses_dict(students_ids, academics, professors, students):
    students_by_courses = {}

    for academic_id in students_ids:
        student_instance = data_processing.find_class_instance_by_academic_id(academic_id, academics, professors, students)
        
        student_course = student_instance.course

        if student_course not in students_by_courses:
            students_by_courses[student_course] = []
        
        students_by_courses[student_course].append(academic_id)
    
    return students_by_courses

def generate_graphs_by_course_average(df, data):
    return

def get_statistics(data):
    df = pd.read_csv("results.csv", sep=";")
    
    _, _, academics, professors, students, _, _ = data
    
    professors_ids, students_ids = get_professors_students_academic_id(academics)
    students_by_courses = get_students_by_courses_dict(students_ids, academics, professors, students)

    generate_graphs_by_day_average(df, "png")
    generate_graphs_by_professor_student_average(df, "png", professors_ids, students_ids)


    

def main():
    (opt, _) = parse_terminal_options()

    data = load_and_save_data(opt.load_data, opt.save_csv)

    # simulate_tracking(data)
    get_statistics(data)

if __name__ == "__main__":
    main()
