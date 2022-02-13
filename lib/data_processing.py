import os
from openpyxl import load_workbook

import classes
import file_operations

def get_room_mapping_from_excel_file(filepath, worksheet_name):
    # a função carrega dados de uma planilha; após isso, cria e retorna um dicionário da forma {day: {hour: [room, component_code, component_class] ...} ...}

    excel_workbook = load_workbook(filepath)
    worksheet = excel_workbook[worksheet_name]
    room_mapping = {}

    for i in range(2, worksheet.max_row + 1):
        day = worksheet.cell(row = i, column = 1).value
        hour = worksheet.cell(row = i, column = 2).value
        classroom = worksheet.cell(row = i, column = 3).value
        component_code = worksheet.cell(row = i, column = 4).value
        component_class = worksheet.cell(row = i, column = 5).value

        if day not in room_mapping:
            room_mapping[day] = {}
            room_mapping[day][hour] = {}
        elif hour not in room_mapping[day]:
            room_mapping[day][hour] = {}
        
        if classroom not in room_mapping[day][hour]:
            room_mapping[day][hour][classroom] = []
        
        component_list = [component_code, component_class]
        room_mapping[day][hour][classroom].append(component_list)

    return room_mapping

def get_students_mapping_from_pickle_file(datadir):
    dfpath = os.path.join(os.getcwd(), datadir, "dataframes.pickle")
    data = file_operations.load_pickle_file(dfpath)

    print(data)
    input()

    students_mapping = {}
    students = {}

    for subject in data['data']:
        # print(subject)
        # input()
        component_code = subject[0][1][0].split('-')[0].strip() #0 - elemento dentro da lista, 1 - coluna com as informações, 0 - informações da disciplina, código é a primeira string antes do hífen
        component_class = subject[0][1][1].strip()  #0 - elemento dentro da lista, 1 - coluna com as informações, 0 - informações da turma
        students_ids = subject[1]['Matrícula'].tolist()
        students_courses = subject[1]['Curso'].tolist()

        if component_code not in students_mapping: #adiciona o código da disciplina apenas quando aparece pela primeira vez
            students_mapping[component_code] = {}
        
        if component_class not in students_mapping[component_code]: #os estudantes em uma turma de um determinado código de disciplina são os mesmos, então só adicionamos na primeira vez que aparecem
            students_mapping[component_code][component_class] = []

            for i in range(0, len(students_ids)):
                student_id = students_ids[i]
                student_course = students_courses[i]
                new_student = classes.Student(student_id, student_course)

                if student_id not in students:
                    students[student_id] = new_student
                    students_mapping[component_code][component_class].append(new_student)
                else:
                    students_mapping[component_code][component_class].append(students[student_id])
    
    return students_mapping, students
