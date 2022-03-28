import datetime
import math
import random
from itertools import combinations
from optparse import OptionParser

from lib import data_processing
from lib import file_operations

def parse_terminal_options():
    # a função gera padrões de parâmetros a serem analisados e retorna o resultado final

    parser = OptionParser()
    parser.add_option("-d", "--datadir", type="string", dest="datadir", default=".", help="Diretório para salvar dados")
    parser.add_option("-v", "--verbose", action="store_true", dest="verbose", default=False, help="Imprime mensagens para debug")

    return parser.parse_args()

def wells_riley_equation(param):
    # calcula a probabilidade de contaminação por um vírus transmissível pelo ar, dados os parâmetros informados no dict param

    infection_probability = []

    for ventilation_rate in param['ventilation_rates']:
        ventilation_volume = param['room_volume'] * ventilation_rate
        
        n = (param['infectors_count'] * param['quantum_generation_rate'] * param['breathing_rate'] * param['duration_time'])
        n /= ventilation_volume

        infection_probability.append(1 - math.exp(-n))

    return infection_probability

def get_days_to_analyse(informed_day):
    informed_day = int(informed_day)

    days = list(range(1, 8)) #exclusivo

    week_days = []

    for day_index in range(informed_day - 5, informed_day - 1):
        if days[day_index] in [2, 3, 4, 5, 6]:
            week_days.append(days[day_index])
    
    # dia que os sintomas apareceram --- dias a serem analisados (serão ignorados sábado e domingo)
    # 2 --- 5671
    # 3 --- 6712
    # 4 --- 7123
    # 5 --- 1234
    # 6 --- 2345

    return week_days

def tracking(informed_id, informed_day, room_mapping, academics_mapping, academics, professors, students, classrooms):
    choosed_academic = data_processing.find_class_instance_by_academic_id(academics, professors, students, informed_id)

    print(choosed_academic.academic_id)
    # assumindo que o acadêmico fez o teste no primeiro dia que sentiu os sintomas da covid e informou que estava contaminado
    
    choosed_academic.has_covid = True
    choosed_academic.can_transmit = True
    choosed_academic.infected_days = 0

    # quatro dias anteriores a notificação de contaminação, ignorando dias de fim de semana
    days = get_days_to_analyse(informed_day)
    
    # pessoas que estiveram na mesma sala de alguém infectado
    affected_academics = []

    with open("ventilation_rates", "r") as file:
        ventilation_rates = file.readlines()
    
    ventilation_rates = [float(value.replace("\n", "")) for value in ventilation_rates]

    equation_param = {
        'quantum_generation_rate': 48, # foi o máximo de quanta para a covid 19, segundo o artigo do park (2021)
        'breathing_rate': 0.3, # segundo o artigo de park (2021) é a taxa de respiração de uma pessoa em repouso
        'duration_time': 2, # considerando que as aulas sempre durem 2 horas
        'ventilation_rates': ventilation_rates
    }

    # segunda a sexta
    for day in days:
        for hour in room_mapping[day]:
            for classroom in room_mapping[day][hour]:
                component_code, component_class = room_mapping[day][hour][classroom]

                if choosed_academic in academics_mapping[component_code][component_class]:
                    print(day, hour, classroom, component_code, component_class)
                    current_classroom = data_processing.find_class_instance_by_id(classrooms, classroom)
                    count_infected = 0

                    for academic in academics_mapping[component_code][component_class]:
                        if academic not in affected_academics and academic != choosed_academic:
                            affected_academics.append(academic)
                        if academic.has_covid and academic.can_transmit:
                            count_infected += 1
                    
                    equation_param['infectors_count'] = count_infected
                    equation_param['room_volume'] = current_classroom.volume
                    classroom_contamination_prob = wells_riley_equation(equation_param)

                    for academic in academics_mapping[component_code][component_class]:
                        if not academic.has_covid:
                            if academic.infection_probability == []:
                                for _ in range(0, 6): # são 5 casos do artigo do park
                                    academic.infection_probability.append([])
                            
                            for case in range(0, 6): 
                                academic.infection_probability[case].append(classroom_contamination_prob[case])

    calculate_contamination_associated_values(professors)
    calculate_contamination_associated_values(students)

    verify_affected(affected_academics)

def combination_probability(prob_list):
    
    prob_indexes = [index for index in range(0, len(prob_list))]

    comb_prob_all = 0
    for n_comb in range(1, len(prob_list)):
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

def calculate_contamination_associated_values(academics_instances):
    for academic_instance in academics_instances:
        if academic_instance.has_covid:
            if academic_instance.infected_days == 14:
                academic_instance.has_covid = False
                academic_instance.can_transmit = False
                academic_instance.infected_days = 0
                academic_instance.infection_probability = 0
            else:
                academic_instance.infected_days += 1

def verify_affected(affected_academics):
    for affected_academic in affected_academics:
        random_probability = random.uniform(0.7, 1)
        
        for case in range(0, 6):
            case_combination_prob = combination_probability(affected_academic.infection_probability[case])
            
            if case_combination_prob > random_probability:
                print(affected_academic.academic_id, affected_academic.id, case_combination_prob, "foi contaminado no caso %d" % (case + 1))
            else:
                print(affected_academic.academic_id, affected_academic.id, case_combination_prob, "não foi contaminado no caso %d" % (case + 1))

        affected_academic.set_empty_infection_probability()

def main():
    # (opt, args) = parse_terminal_options()

    room_mapping, academics_mapping, academics, professors, students, classrooms = file_operations.load_anonymized_data_from_csv_files()
    
    # room_mapping, academics_mapping, academics, professors, students, classrooms = data_processing.get_processed_data("lib/file.txt")
    # file_operations.save_structures_to_csv_files(room_mapping, academics_mapping, academics, professors, students, classrooms)

    informed_id, informed_day = file_operations.load_parameters_from_txt_file("lib/info.txt")
    # informed_academic = input("Digite \"P\" se for Professor ou \"A\" se for Aluno: ")
    # informed_id = input("Digite a sua matrícula (aluno) ou nome completo (professor): ")
    # informed_day = input("Digite a data na qual você descobriu estar com Covid-19: ")
    # print(classrooms)
    # print(room_mapping)
    # input()
    # print(academics_mapping)
    # input()
    # print(academics)
    # input()
    # print(professors)
    # input()
    # print(students)
    # input()
    # print(classrooms)
    # input()
    # for professor_name in professors:
    #     print(professors[professor_name].name)
    tracking(informed_id, informed_day, room_mapping, academics_mapping, academics, professors, students, classrooms)

    return

if __name__ == "__main__":
    main()
