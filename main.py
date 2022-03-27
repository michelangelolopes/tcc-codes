import math
import random
from optparse import OptionParser

from lib import data_processing
from lib import file_operations

# class param:
#     def __init__(self, quantum_generation_rate=48, breathing_rate=0.3, duration_time=2):
#         self.quantum_generation_rate = quantum_generation_rate
#         self.breathing_rate = breathing_rate
#         self.duration_time = duration_time

#     def set_new_param(self, infectors_count, room_volume):
#         self.infectors_count = infectors_count
#         self.room_volume = room_volume

def parse_terminal_options():
    # a função gera padrões de parâmetros a serem analisados e retorna o resultado final

    parser = OptionParser()
    parser.add_option("-d", "--datadir", type="string", dest="datadir", default=".", help="Diretório para salvar dados")
    parser.add_option("-v", "--verbose", action="store_true", dest="verbose", default=False, help="Imprime mensagens para debug")

    return parser.parse_args()

def wells_riley_equation(param):
    infection_probability = []

    for ventilation_rate in param['ventilation_rates']:
        ventilation_volume = param['room_volume'] * ventilation_rate
        
        n = (param['infectors_count'] * param['quantum_generation_rate'] * param['breathing_rate'] * param['duration_time'])
        n /= ventilation_volume

        infection_probability.append(1 - math.exp(-n))

    # print(ventilation_volume, duration_time, "%.2f" % (100 * infection_probability), sep="\t\t")

    return infection_probability

def rudnick(count_people, count_infected, quanta_generated_per_hour = 48, exhaled_room_volume_per_hour = 1, room_volume = 10, time_exposure = 2):
    # quanta_generated_per_hour = 48, foi o máximo de quanta para a covid 19, segundo o artigo do park (2021)
    # print(count_people, count_infected, quanta_generated_per_hour, exhaled_breath_fraction, time_exposure)
    exhaled_room_volume = exhaled_room_volume_per_hour * time_exposure
    exhaled_breath_fraction = exhaled_room_volume / room_volume

    quanta_generated = quanta_generated_per_hour * time_exposure

    total_quanta = (count_infected * quanta_generated * exhaled_breath_fraction) / count_people

    probability = 1 - math.exp(-total_quanta)

    return probability

def get_days_to_analyse(informed_day):
    informed_day = int(informed_day)

    days = list(range(1, 8)) #exclusivo

    week_days = []

    for day_index in range(informed_day - 5, informed_day - 1):
        if days[day_index] in [2, 3, 4, 5, 6]:
            week_days.append(days[day_index])
    
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
    # ignorando dias de fim de semana por enquanto
    
    choosed_academic.has_covid = True
    choosed_academic.can_transmit = True
    # choosed_academic.has_symptoms = True
    choosed_academic.infected_days = 0
    choosed_academic.infection_probability = 0

    for student in students:
        student.breathing_rate = random.uniform(0.25, 0.75)
    for professor in professors:
        professor.breathing_rate = random.uniform(0.75, 1)

    # quatro dias anteriores a notificação de contaminação, ignorando fim de semana
    days = get_days_to_analyse(informed_day)
    
    #sábado e domingo
    # for student_id in students:
    #     students[student_id].infection_probability = random.uniform(0, 1)

    # for professor_name in professors:
    #     professors[professor_name].infection_probability = random.uniform(0, 1)
    
    # pessoas que estiveram na mesma sala de alguém infectado
    affected_academics = []

    with open("ventilation_rates", "r") as file:
        ventilation_rates = file.readlines()
    
    ventilation_rates = [float(value.replace("\n", "")) for value in ventilation_rates]

    equation_param = {
        'quantum_generation_rate': 48,
        'breathing_rate': 0.3,
        'duration_time': 2,
        'ventilation_rates': ventilation_rates
    }

    # segunda a sexta
    for day in days:
        for hour in room_mapping[day]:
            for classroom in room_mapping[day][hour]:
                # print(day, hour, classroom)
                component_code, component_class = room_mapping[day][hour][classroom]
                # print(academics_mapping[component_code])
                # print(academics_mapping[component_code][component_class])
                # input()
                # print(choosed_academic in academics_mapping[component_code][component_class])
                if choosed_academic in academics_mapping[component_code][component_class]:
                    print(day, hour, classroom, component_code, component_class)
                    current_classroom = data_processing.find_class_instance_by_id(classrooms, classroom)
                    # count_people = len(academics_mapping[component_code][component_class])
                    count_infected = 0
                    # exhaled_room_volume_per_hour = 0
                    # room_volume = current_classroom.volume


                    for academic in academics_mapping[component_code][component_class]:
                        # print(academic)
                        # exhaled_room_volume_per_hour += academic.breathing_rate
                        if academic not in affected_academics and academic != choosed_academic:
                            affected_academics.append(academic)
                        if academic.has_covid and academic.can_transmit:
                            count_infected += 1
                    
                    equation_param['infectors_count'] = count_infected
                    equation_param['room_volume'] = current_classroom.volume
                    # print(count_people, count_infected)
                    # classroom_contamination_prob = rudnick(count_people, count_infected, exhaled_room_volume_per_hour=exhaled_room_volume_per_hour, room_volume=room_volume)
                    classroom_contamination_prob = wells_riley_equation(equation_param)
                    print(classroom_contamination_prob)
                    # input()

                    for academic in academics_mapping[component_code][component_class]:
                        # analisar como "juntar" probabilidades
                        # teste com somatório ficou esquisito
                        if not academic.has_covid:
                            if academic.infection_probability == []:
                                for _ in range(0, 6): # são 5 casos do artigo do park
                                    academic.infection_probability.append([])
                            
                            for case in range(0, 6): 
                                academic.infection_probability[case].append(classroom_contamination_prob[case])
                            print(academic.infection_probability)
                                #  * (1 + academic.infection_probability)
                            # += classroom_contamination_prob 
                    # input()
    calculate_contamination_associated_values(professors)
    calculate_contamination_associated_values(students)

    verify_affected(affected_academics)

    # print(affected_academics)
    # print(academics_mapping)

from itertools import combinations
import math

def combination_probability(prob_list):
    # prob_list = [0.3, 0.2]
    
    # prob_indexes = [index + 1 for index in range(0, len(prob_list))]

    comb_prob_all = 0
    for count_comb in range(len(prob_list), 0, -1):
        # print(count_comb)
        comb_list = combinations(prob_list, count_comb)
        comb_list = list(comb_list)

        for comb in comb_list:
            comb_prob = math.prod(comb)
            # print(comb)
            not_comb = [elem for elem in prob_list if elem not in comb]
            
            for elem in not_comb:
                comb_prob *= (1 - elem)

            comb_prob_all += comb_prob
        # print(comb_prob_all)
        # input()
    return comb_prob_all

    # print(comb, math.prod(comb[0]))
    # for prob_index in range(0, len(probability_list)):
    #     prob_combination = probability_list[prob_index]

    #     other_probs = probability_list.copy()
    #     other_probs.remove(prob_index)

    #     other_probs_combinations = []

    #     for other_prob_index_1 in range(0, len(other_probs)):
    #         for other_prob_index_2 in range(0, len(other_probs)):
    #             if other_prob_index_1 != other_prob_index_2:
    #                 # Get all combinations of [1, 2, 3]
    #                 # and length 2
    #                 comb = combinations([1, 2, 3], 2)



    #     prob_combination * = (1 - )

def calculate_contamination_associated_values(academics_instances):
    for academic_instance in academics_instances:
        if academic_instance.has_covid:
            if academic_instance.infected_days == 14:
                academic_instance.has_covid = False
                academic_instance.can_transmit = False
                # academic_instance.has_symptoms = False
                academic_instance.infected_days = 0
                academic_instance.infection_probability = 0
            else:
                academic_instance.infected_days += 1

def verify_affected(affected_academics):

    # print([i.id for i in affected_academics])
    # input()
    for affected_academic in affected_academics:
        random_probability = random.uniform(0.7, 1)
        
        # if affected_academic.infection_probability == []:
        #     print("ERRO", affected_academic.id)
        # else:
        for case in range(0, 6):
            case_combination_prob = combination_probability(affected_academic.infection_probability[case])
            # input()
            if case_combination_prob > random_probability:
                print(affected_academic.academic_id, affected_academic.id, case_combination_prob, "foi contaminado no caso %d" % (case + 1))
                # affected_academic.has_covid = True
                # academic_instance.can_transmit = True
                # academic_instance.has_symptoms = False
                # academic_instance.infected_days = 0
        affected_academic.set_empty_infection_probability()
            # print("CERT", affected_academic.id)

def main():
    # (opt, args) = parse_terminal_options()

    # room_mapping, academics_mapping, academics, professors, students, classrooms = file_operations.load_anonymized_data_from_csv_files()
    room_mapping, academics_mapping, academics, professors, students, classrooms = data_processing.get_processed_data("lib/file.txt")
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
