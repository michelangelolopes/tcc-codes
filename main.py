import math
import random
from optparse import OptionParser

from lib import data_processing
from lib import file_operations

def parse_terminal_options():
    # a função gera padrões de parâmetros a serem analisados e retorna o resultado final

    parser = OptionParser()
    parser.add_option("-d", "--datadir", type="string", dest="datadir", default=".", help="Diretório para salvar dados")
    parser.add_option("-v", "--verbose", action="store_true", dest="verbose", default=False, help="Imprime mensagens para debug")

    return parser.parse_args()

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

def tracking(informed_academic, informed_id, informed_day, room_mapping, academics_mapping, students, professors, classrooms):
    if informed_academic == "P":
        choosed_academic = professors[informed_id]
    elif informed_academic == "A":
        choosed_academic = students[informed_id]

    # assumindo que o acadêmico fez o teste no primeiro dia que sentiu os sintomas da covid e informou que estava contaminado
    # ignorando dias de fim de semana por enquanto
    
    choosed_academic.has_covid = True
    choosed_academic.can_transmit = True
    # choosed_academic.has_symptoms = True
    choosed_academic.infected_days = 0
    choosed_academic.infection_probability = 0

    for student_id in students:
        students[student_id].breathing_rate = 0.5
    for professor_name in professors:
        professors[professor_name].breathing_rate = 0.5

    # quatro dias anteriores a notificação de contaminação, ignorando fim de semana
    days = get_days_to_analyse(informed_day)

    #sábado e domingo
    # for student_id in students:
    #     students[student_id].infection_probability = random.uniform(0, 1)

    # for professor_name in professors:
    #     professors[professor_name].infection_probability = random.uniform(0, 1)
    
    # pessoas que estiveram na mesma sala de alguém infectado
    affected_academics = []

    # segunda a sexta
    for day in days:
        for hour in room_mapping[day]:
            for classroom in room_mapping[day][hour]:
                for component_code, component_class in room_mapping[day][hour][classroom]:
                    # print(academics_mapping[component_code])
                    # print(academics_mapping[component_code][component_class])
                    # input()
                    # print(choosed_academic in academics_mapping[component_code][component_class])
                    if choosed_academic in academics_mapping[component_code][component_class]:
                        print(day, hour, classroom, component_code, component_class)
                        count_people = len(academics_mapping[component_code][component_class])
                        count_infected = 0
                        exhaled_room_volume_per_hour = 0
                        room_volume = classrooms[classroom].volume

                        for academic in academics_mapping[component_code][component_class]:
                            # print(academic)
                            exhaled_room_volume_per_hour += academic.breathing_rate
                            if academic not in affected_academics and academic != choosed_academic:
                                affected_academics.append(academic)
                            if academic.has_covid and academic.can_transmit:
                                count_infected += 1
                        
                        print(count_people, count_infected, exhaled_room_volume_per_hour, room_volume)
                        classroom_contamination_prob = rudnick(count_people, count_infected, exhaled_room_volume_per_hour=exhaled_room_volume_per_hour, room_volume=room_volume)
                        print(classroom_contamination_prob)

                        for academic in academics_mapping[component_code][component_class]:
                            # analisar como "juntar" probabilidades
                            # teste com somatório ficou esquisito
                            if not academic.has_covid:
                                academic.infection_probability = classroom_contamination_prob * (1 + academic.infection_probability)
                                # += classroom_contamination_prob 

    calculate_contamination_associated_values(professors)
    calculate_contamination_associated_values(students)

    # print(affected_academics)
    # print(academics_mapping)

    for student_id in students:
        if students[student_id] in affected_academics:
            if students[student_id].has_covid:
                print(student_id, students[student_id].infection_probability, "foi contaminado")
            else:
                print(student_id, students[student_id].infection_probability, "não foi contaminado")
    
    for professor_name in professors:
        if professors[professor_name] in affected_academics:
            if professors[professor_name].has_covid:
                print(professor_name, professors[professor_name].infection_probability, "foi contaminado")
            else:
                print(professor_name, professors[professor_name].infection_probability, "não foi contaminado")

def calculate_contamination_associated_values(academics):
    for academic_id in academics:
        if academics[academic_id].has_covid:
            if academics[academic_id].infected_days == 14:
                academics[academic_id].has_covid = False
                academics[academic_id].can_transmit = False
                academics[academic_id].has_symptoms = False
                academics[academic_id].infected_days = 0
                academics[academic_id].infection_probability = 0
            else:
                academics[academic_id].infected_days += 1
        else:
            random_probability = random.uniform(0.5, 1)

            if academics[academic_id].infection_probability > random_probability:
                academics[academic_id].has_covid = True
                academics[academic_id].can_transmit = True
                academics[academic_id].has_symptoms = False
                academics[academic_id].infected_days = 0


def main():
    # (opt, args) = parse_terminal_options()

    room_mapping, academics_mapping, students, professors, classrooms = data_processing.get_and_save_data("lib/file.txt")
    informed_academic, informed_id, informed_day = file_operations.load_parameters_from_txt_file("lib/info.txt")
    # informed_academic = input("Digite \"P\" se for Professor ou \"A\" se for Aluno: ")
    # informed_id = input("Digite a sua matrícula (aluno) ou nome completo (professor): ")
    # informed_day = input("Digite a data na qual você descobriu estar com Covid-19: ")

    # print(classrooms)
    
    tracking(informed_academic, informed_id, informed_day, room_mapping, academics_mapping, students, professors, classrooms)

    return

if __name__ == "__main__":
    main()
