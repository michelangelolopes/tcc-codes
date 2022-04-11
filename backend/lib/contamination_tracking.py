import datetime
import math
import os
from flask import request
from itertools import combinations

from . import data_processing
from . import file_operations

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

def get_weekday_by_date(datetime_str):
    date_format = '%Y-%m-%d'
    date_str = datetime_str.split('T')[0] # sobra apenas a data, sem o tempo

    datetime_obj = datetime.datetime.strptime(date_str, date_format)
    
    return datetime_obj.weekday()

def set_contaminated_academic(academic):
    academic.has_covid = True
    academic.can_transmit = True
    academic.infected_days = 0

########################################

def get_ventilation_rates_from_file():
    filename = "./data/ventilation_rates.txt"
    with open(filename, "r") as file:
        ventilation_rates = file.readlines()
    
    ventilation_rates = [float(value.replace("\n", "")) for value in ventilation_rates]

    return ventilation_rates

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

def get_mask_efficiency(mask_type):
    mask_dict = {
        'no_mask': 0,
        'surgery_mask': 0.5,
        'n95_mask': 0.95
    }

    return mask_dict[mask_type]

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

                file.write("%s;%d;%s;%d" % (informed_id, informed_day, mask_type, count_affected))
                for case in range(0, 6):
                    file.write(";%f" % average[case])
                file.write("\n")
                file.flush()
                os.fsync(file)
    file.close()
