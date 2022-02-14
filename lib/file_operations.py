import os
import pickle

def load_html_file(filepath):
    # a função carrega de um arquivo html o conteúdo dessa página

    file_t = open(filepath, "r")
    page_html = " ".join(file_t.readlines())
    file_t.close()
    return page_html

def load_pickle_file(dfpath):
    # a função carrega o conteúdo de um arquivo pickle para uma variável e retorna essa variável
    
    if os.path.exists(dfpath):
        print("Lendo arquivo pickle.")
        file = open(dfpath, 'rb')
        data = pickle.load(file)
        file.close()
        # print(data)
        return data
    else:
        print("Arquivo não encontrado.")

def save_room_mapping_to_csv_file(room_mapping):
    with open("room_mapping.csv", "w") as file:
        file.write("Dia;Hora;Sala;Disciplina;Turma\n")
        for day in room_mapping:
            for hour in room_mapping[day]:
                for classroom in room_mapping[day][hour]:
                    for component_code, component_class in room_mapping[day][hour][classroom]:
                        file.write("%s;%s;%s;%s;%s\n" % (day, hour, classroom, component_code, component_class))

def save_students_mapping_to_csv_file(students_mapping):
    with open("students_mapping.csv", "w") as file:
        file.write("Disciplina;Turma;Matrícula;Curso\n")
        for component_code in students_mapping:
            for component_class in students_mapping[component_code]:
                for student in students_mapping[component_code][component_class]:
                    file.write("%s;%s;%s;%s\n" % (component_code, component_class, student.id, student.course))

def save_professors_mapping_to_csv_file(professors):
    with open("professors_mapping.csv", "w") as file:
        file.write("Nome do professor;Disciplina;Turma\n")
        for professor in professors:
            for component_code, component_class in professor.subjects:
                file.write("%s;%s;%s\n" % (professor.name, component_code, component_class))

def load_parameters_from_txt_file(filename):
    with open(filename, "r") as file:
        file_content = file.readlines()
        file_content = [string.replace("\n", "") for string in file_content]
    
    return file_content