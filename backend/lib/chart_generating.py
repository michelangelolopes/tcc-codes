import matplotlib.pyplot as plt
import os
import pandas as pd
from matplotlib.ticker import FuncFormatter

from . import data_processing

def weighted_avg(df, values_column, weights_column):
    # calcula a média ponderada usando duas colunas de um dataframe

    values = df[values_column]
    weights = df[weights_column]
    
    return (values * weights).sum() / weights.sum()

def get_dataframe_dict_to_calculate_average(df, choosed_column):
    # retorna um dicionário de dataframes agrupados pelo tipo de máscara usado

    df_masks = df.groupby(["mask_type"])
    
    df_dict = {}
    for mask_type, df_mask in df_masks:
        df_dict[mask_type] = df_mask.groupby([choosed_column])

    return df_dict

def get_dataframe_series_dict_with_calculated_averages(df_dict):
    # retorna um dicionário com o valor calculado da média ponderada para cada tipo de máscara usado em cada caso de ventilação do ambiente

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

def get_professors_and_students_list(academics):
    # retorna duas listas: uma com os ids específicos dos professores e outra com os ids específicos dos alunos

    professors_ids = []
    students_ids = []

    for academic_id in academics:
        # academics[academic_id] é uma tupla do tipo (PROFESSOR_ID, STUDENT_ID), sendo que apenas uma das posições é preenchida por vez
        # ou seja, se PROFESSOR_ID == '', então STUDENT_ID != '' e vice-versa

        if academics[academic_id][0] == '':
            students_ids.append(academic_id)
        else:
            professors_ids.append(academic_id)

    return professors_ids, students_ids

def get_students_by_courses_dict(students_ids, academics, professors, students):
    # retorna um dicionário com os cursos como keys e os values sendo listas com os respectivos alunos dos cursos

    students_by_courses = {}

    for academic_id in students_ids:
        student_instance = data_processing.find_class_instance_by_academic_id(academic_id, academics, professors, students)
        
        student_course = student_instance.course

        if student_course not in students_by_courses:
            students_by_courses[student_course] = []
        
        students_by_courses[student_course].append(academic_id)
    
    return students_by_courses

def generate_and_save_dataframe_chart_by_case(case_df, case_index, path, filetype, plot_kind, label_data):
    # gera o plot de um gráfico usando um dataframe como base e salva, logo em seguida esse gráfico em um arquivo

    case_df_rows_count = len(case_df.index)

    error = [
        [case_df["Sem máscara"].std()] * case_df_rows_count, 
        [case_df["Máscara cirúrgica"].std()] * case_df_rows_count, 
        [case_df["Máscara N95"].std()] * case_df_rows_count
    ]

    label_prob = "Probabilidade média de contaminação no Caso " + str(case_index)

    if plot_kind == 'bar':
        ax = case_df.plot(kind=plot_kind, yerr=error, edgecolor = 'black', rot=0, width=0.9, capsize=3)
        ax.set_xlabel(label_data)
        ax.set_ylabel(label_prob)
        ax.yaxis.set_major_formatter(FuncFormatter(lambda value, _: '{:.1%}'.format(value)))
    elif plot_kind == 'barh':
        ax = case_df.plot(kind=plot_kind, xerr=error, edgecolor = 'black', rot=0, width=0.9, capsize=2)
        ax.set_ylabel(label_data)
        ax.set_xlabel(label_prob)
        ax.xaxis.set_major_formatter(FuncFormatter(lambda value, _: '{:.1%}'.format(value)))
    
    ax.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=2, mode="expand", borderaxespad=0., title="Uso de máscara")
    
    fig_filename = path + "case_" + str(case_index) + "." + filetype
    plt.savefig(fig_filename, bbox_inches='tight')
    plt.close()

def save_chart_data_to_csv_file(case_df, case_index, path):
    # salva os dados usados para gerar o gráfico para um caso em um arquivo csv

    csv_filename = path + "case_" + str(case_index) + "." + "csv"
    case_df['Desvio Padrão - Sem máscara'] = case_df["Sem máscara"].std()
    case_df['Desvio Padrão - Máscara cirúrgica'] = case_df["Máscara cirúrgica"].std()
    case_df['Desvio Padrão - Máscara N95'] = case_df["Máscara N95"].std()

    case_df.to_csv(csv_filename, header=False, sep=' ')

def generate_and_save_dataframe_chart(df_dict, df_index, path, filetype, plot_kind, label_data):
    # gera e salva os dados usados para gerar um gráfico e o próprio gráfico

    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)

    series_dict = get_dataframe_series_dict_with_calculated_averages(df_dict)

    for case_index in range(1, 7):
        case_df = pd.DataFrame(index=df_index)
        case_df["Sem máscara"] = series_dict[case_index]["no_mask"].values
        case_df["Máscara cirúrgica"] = series_dict[case_index]["surgery_mask"].values
        case_df["Máscara N95"] = series_dict[case_index]["n95_mask"].values

        if label_data == "Dia da notificação":
            reordered_named_days = list(case_df.index)
            reordered_named_days.append(reordered_named_days.pop(0))
            case_df = case_df.loc[reordered_named_days]

        generate_and_save_dataframe_chart_by_case(case_df, case_index, path, filetype, plot_kind, label_data)
        save_chart_data_to_csv_file(case_df, case_index, path)

def generate_charts_by_day_average(df, choosed_column, path, filetype):
    # gera gráficos considerando a média das probabilidades de contaminação dependendo do dia da semana em que ocorreu a notificação do infectado

    df_dict = get_dataframe_dict_to_calculate_average(df, choosed_column)
    named_days = ["Domingo", "Terça", "Quarta", "Quinta", "Sexta", "Sábado"]

    generate_and_save_dataframe_chart(df_dict, named_days, path, filetype, "bar", "Dia da notificação")

def generate_charts_by_professor_student_average(df, choosed_column, path, filetype, professors_ids, students_ids):
    # gera gráficos considerando a média das probabilidades de contaminação dependendo se o infectado é professor ou aluno

    new_df = df.copy().assign(professor_student='')
    new_df.loc[new_df["academic_id"].isin(professors_ids), 'professor_student'] = 'professor'
    new_df.loc[new_df["academic_id"].isin(students_ids), 'professor_student'] = 'student'

    df_dict = get_dataframe_dict_to_calculate_average(new_df, choosed_column)

    generate_and_save_dataframe_chart(df_dict, ["Professor", "Estudante"], path, filetype, "bar", "Acadêmico")

def generate_charts_by_course_average(df, choosed_column, path, filetype, students_by_courses):
    # gera gráficos considerando a média das probabilidades de contaminação dependendo do curso do infectado

    new_df = df.copy().assign(student_course = '')

    for course in students_by_courses:
        new_df.loc[new_df["academic_id"].isin(students_by_courses[course]), choosed_column] = course

    new_df.drop(new_df[new_df[choosed_column] == ''].index, inplace=True)

    all_courses = list(students_by_courses.keys())
    all_courses = [course.replace("- LICENCIATURA", "(L)").replace("- BACHARELADO", "(B)") for course in all_courses]

    df_dict = get_dataframe_dict_to_calculate_average(new_df, choosed_column)

    generate_and_save_dataframe_chart(df_dict, all_courses, path, filetype, "barh", "Cursos")

def generate_charts_based_on_statistics(data):
    # gera gráficos com as estatísticas obtidas na simulação

    df = pd.read_csv("results.csv", sep=";")
    
    _, _, academics, professors, students, _, _ = data
    
    professors_ids, students_ids = get_professors_and_students_list(academics)
    students_by_courses = get_students_by_courses_dict(students_ids, academics, professors, students)

    parent_path = "./images/"
    filetype = "pdf"

    generate_charts_by_day_average(df, "notification_day", parent_path + "days/", filetype)
    generate_charts_by_professor_student_average(df, "professor_student", parent_path + "people/", filetype, professors_ids, students_ids)
    generate_charts_by_course_average(df, "student_course", parent_path + "courses/", filetype, students_by_courses)
