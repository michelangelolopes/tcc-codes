import os
import pickle

from . import classes
from . import data_processing

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

def load_parameters_from_txt_file(filename):
    with open(filename, "r") as file:
        file_content = file.readlines()
        file_content = [string.replace("\n", "") for string in file_content]
    
    return file_content

def save_professors_to_csv_file(professors):
    if not os.path.exists("./data/"):
        os.makedirs("./data/")
    with open("./data/professors.csv", "w") as file:
        file.write("ID do Professor\n")
        for professor in professors:
            file.write("%s\n" % (professor.id))

def load_professors_from_csv_file():
    with open("./data/professors.csv", "r") as file:
        rows = file.readlines()
    
    rows.pop(0)
    rows = [row.replace("\n", "") for row in rows]
    professors = []

    for id in rows:
        professor = classes.Professor()
        professor.id = id
        professors.append(professor)

    return professors

def save_students_to_csv_file(students):
    if not os.path.exists("./data/"):
        os.makedirs("./data/")
    with open("./data/students.csv", "w") as file:
        file.write("ID do Aluno;Curso\n")
        for student in students:
            file.write("%s;%s\n" % (student.id, student.course))

def load_students_from_csv_file():
    with open("./data/students.csv", "r") as file:
        rows = file.readlines()
    
    rows.pop(0)
    rows = [row.replace("\n", "").split(";") for row in rows]
    students = []

    for id, course in rows:
        student = classes.Student(course = course)
        student.id = id
        students.append(student)

    return students

def save_academics_to_csv_file(academics):
    if not os.path.exists("./data/"):
        os.makedirs("./data/")
    with open("./data/academics.csv", "w") as file:
        file.write("ID do Acadêmico;ID do Professor;ID do Aluno\n")
        for academic_id in academics:
            professor_id, student_id = academics[academic_id]
            file.write("%s;%s;%s\n" % (academic_id, professor_id, student_id))

def load_academics_from_csv_file(professors, students):
    with open("./data/academics.csv", "r") as file:
        rows = file.readlines()
    
    rows.pop(0)
    rows = [row.replace("\n", "").split(";") for row in rows]
    academics = {}

    for academic_id, professor_id, student_id in rows:
        academics[academic_id] = (professor_id, student_id)

        academic = data_processing.find_class_instance_by_academic_id(academic_id, academics, professors, students)

        academic.academic_id = academic_id

    return academics

def save_academics_mapping_to_csv_file(academics_mapping):
    if not os.path.exists("./data/"):
        os.makedirs("./data/")
    with open("./data/academics_mapping.csv", "w") as file:
        file.write("Disciplina;Turma;ID do Acadêmico\n")
        for component_code in academics_mapping:
            for component_class in academics_mapping[component_code]:
                for academic in academics_mapping[component_code][component_class]:
                    file.write("%s;%s;%s\n" % (component_code, component_class, academic.academic_id))

def load_academics_mapping_from_csv_file(academics, professors, students):
    with open("./data/academics_mapping.csv", "r") as file:
        rows = file.readlines()
    
    rows.pop(0)
    rows = [row.replace("\n", "").split(";") for row in rows]

    academics_mapping = {}

    for component_code, component_class, academic_id in rows:
        if component_code not in academics_mapping:
            academics_mapping[component_code] = {}
        
        if component_class not in academics_mapping[component_code]:
            academics_mapping[component_code][component_class] = []

        academic = data_processing.find_class_instance_by_academic_id(academic_id, academics, professors, students)
        
        academics_mapping[component_code][component_class].append(academic)

    return academics_mapping

def save_room_mapping_to_csv_file(room_mapping):
    if not os.path.exists("./data/"):
        os.makedirs("./data/")
    with open("./data/room_mapping.csv", "w") as file:
        file.write("Dia;Hora;Sala;Disciplina;Turma\n")
        for day in room_mapping:
            for hour in room_mapping[day]:
                for classroom in room_mapping[day][hour]:
                    component_code, component_class = room_mapping[day][hour][classroom]
                    file.write("%s;%s;%s;%s;%s\n" % (day, hour, classroom, component_code, component_class))

def load_room_mapping_from_csv_file():
    with open("./data/room_mapping.csv", "r") as file:
        rows = file.readlines()
    
    rows.pop(0)
    rows = [row.replace("\n", "").split(";") for row in rows]

    room_mapping = {}

    for day, hour, classroom, component_code, component_class in rows:
        day = int(day)
        hour = int(hour)

        if day not in room_mapping:
            room_mapping[day] = {}

        if hour not in room_mapping[day]:
            room_mapping[day][hour] = {}

        if classroom not in room_mapping[day][hour]:
            room_mapping[day][hour][classroom] = [component_code, component_class]

    return room_mapping

def save_classroom_types_to_csv_file(classroom_types):
    if not os.path.exists("./data/"):
        os.makedirs("./data/")
    with open("./data/classroom_types.csv", "w") as file:
        file.write("Tipo da sala;Altura;Largura;Profundidade\n")
        for classroom_type in classroom_types:
            file.write("%s;%s;%s;%s\n" % (classroom_type.type, classroom_type.height, classroom_type.width, classroom_type.length))

def load_classroom_types_from_csv_file():
    with open("./data/classroom_types.csv", "r") as file:
        rows = file.readlines()
    
    rows.pop(0)
    rows = [row.replace("\n", "").split(";") for row in rows]

    classroom_types = []

    for type, height, width, length in rows:
        classroom_types.append(classes.Classroom_Type(type, float(height), float(width), float(length)))

    return classroom_types

def save_classrooms_to_csv_file(classrooms):
    if not os.path.exists("./data/"):
        os.makedirs("./data/")
    with open("./data/classrooms.csv", "w") as file:
        file.write("Sala;Tipo de sala\n")
        for classroom in classrooms:
            file.write("%s;%s\n" % (classroom.id, classroom.type.type))

def load_classrooms_from_csv_file(classroom_types):
    with open("./data/classrooms.csv", "r") as file:
        rows = file.readlines()
    
    rows.pop(0)
    rows = [row.replace("\n", "").split(";") for row in rows]

    classrooms = []

    for id, type in rows:
        for classroom_type in classroom_types:
            if classroom_type.type == type:
                break

        classroom = classes.Classroom(id, classroom_type)
        classrooms.append(classroom)

    return classrooms

def save_structures_to_csv_files(room_mapping, academics_mapping, academics, professors, students, classroom_types, classrooms):
    save_room_mapping_to_csv_file(room_mapping)
    save_academics_mapping_to_csv_file(academics_mapping)
    save_academics_to_csv_file(academics)
    save_professors_to_csv_file(professors)
    save_students_to_csv_file(students)
    save_classroom_types_to_csv_file(classroom_types)
    save_classrooms_to_csv_file(classrooms)

def load_anonymized_data_from_csv_files():
    if not os.path.exists("./data/"):
        print("Impossível carregar dados! A pasta \"data\" não existe.")
        exit()

    professors = load_professors_from_csv_file()
    students = load_students_from_csv_file()
    academics = load_academics_from_csv_file(professors, students)
    academics_mapping = load_academics_mapping_from_csv_file(academics, professors, students)
    room_mapping = load_room_mapping_from_csv_file()
    classroom_types = load_classroom_types_from_csv_file()
    classrooms = load_classrooms_from_csv_file(classroom_types)

    return room_mapping, academics_mapping, academics, professors, students, classroom_types, classrooms
    