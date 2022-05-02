import matplotlib.pyplot as plt
import os
import pandas as pd
from matplotlib.ticker import FuncFormatter

import numpy as np

from . import data_processing

def weighted_avg(df, values_column, weights_column):
    # calcula a média ponderada usando duas colunas de um dataframe

    values = df[values_column]
    weights = df[weights_column]
    
    return (values * weights).sum() / weights.sum()

def get_dataframe_dict_to_calculate_average(df, choosed_column):
    # retorna um dicionário de dataframes agrupados pelo tipo de máscara usado

    df_masks = df.groupby(["infector_mask"])
    
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

def get_chart_errors(case_df, legend_title):
    case_df_rows_count = len(case_df.index)

    error = []
    for df_index in case_df:
        error_aux = [case_df[df_index].std()] * case_df_rows_count
        error.append(error_aux)

    return error

def generate_and_save_dataframe_chart_by_case(case_df, plot_kind, label_data, fig_filename, legend_title):
    # gera o plot de um gráfico usando um dataframe como base e salva, logo em seguida esse gráfico em um arquivo

    label_prob = "Probabilidade média de contaminação"
    
    error = get_chart_errors(case_df, legend_title)

    if label_data == "Variantes":
        if plot_kind == 'bar':
            ax = case_df.plot(kind=plot_kind, edgecolor = 'black', rot=0, width=0.9, capsize=3)
            ax.set_xlabel(label_data)
            ax.set_ylabel(label_prob)
            ax.yaxis.set_major_formatter(FuncFormatter(lambda value, _: '{:.1%}'.format(value)))        
    else:
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
    
    ax.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=2, mode="expand", borderaxespad=0., title=legend_title)

    plt.savefig(fig_filename, bbox_inches='tight')
    plt.close()

def save_chart_data_to_csv_file(case_df, case_index, path):
    # salva os dados usados para gerar o gráfico para um caso em um arquivo csv

    csv_filename = path + "case_" + str(case_index) + "." + "csv"
    case_df['Desvio Padrão - Sem máscara'] = case_df["Sem máscara"].std()
    case_df['Desvio Padrão - Máscara cirúrgica'] = case_df["Máscara cirúrgica"].std()
    case_df['Desvio Padrão - Máscara N95'] = case_df["Máscara N95"].std()

    case_df.to_csv(csv_filename, header=False, sep=' ')

def generate_and_save_dataframe_chart(df_dict, df_index, df_ordered_index, path, filetype, plot_kind, label_data):
    # gera e salva os dados usados para gerar um gráfico e o próprio gráfico
    dir_path = path.rsplit("/", 1)[0] + "/"
    if not os.path.exists(dir_path):
        os.makedirs(dir_path, exist_ok=True)

    series_dict = get_dataframe_series_dict_with_calculated_averages(df_dict)

    mask_name = {
        'no_mask': 'Sem máscara',
        'surgery_mask': 'Máscara cirúrgica',
        'n95_mask': 'Máscara N95'
    }

    found_masks = list(df_dict.keys())

    case_df = {}

    for case_index in range(1, 7):
        case_df[case_index] = pd.DataFrame(index=df_index)

        for found_mask in found_masks:
            found_mask_name = mask_name[found_mask]
            case_df[case_index][found_mask_name] = series_dict[case_index][found_mask].values

        if df_ordered_index != []:
            case_df[case_index] = case_df[case_index].loc[df_ordered_index]

    for case_index in range(1, 7):
        fig_filename = path + "case_" + str(case_index) + "." + filetype
        legend_title = "Uso de máscara da pessoa infectada"

        generate_and_save_dataframe_chart_by_case(case_df[case_index], plot_kind, label_data, fig_filename, legend_title)

    all_cases_df = {}

    for case_index in range(1, 7):
        masks_list = [mask_name[found_mask] for found_mask in found_masks]

        mask_df = {}
        for found_mask in found_masks:
            found_mask_name = mask_name[found_mask]
            drop_masks = masks_list.copy()
            drop_masks.remove(found_mask_name)
            mask_df[found_mask] = case_df[case_index].drop(drop_masks, axis=1)
            mask_df[found_mask].rename(columns={found_mask_name:'Caso %d' % case_index}, inplace=True)

            if found_mask not in all_cases_df:
                all_cases_df[found_mask] = pd.DataFrame()
            
            all_cases_df[found_mask] = pd.concat([all_cases_df[found_mask], mask_df[found_mask]], axis=1)

    legend_title = "Casos de ventilação"

    for found_mask in found_masks:
        fig_filename = path + "all_cases-" + found_mask + "." + filetype
        generate_and_save_dataframe_chart_by_case(all_cases_df[found_mask], plot_kind, label_data, fig_filename, legend_title)

def generate_charts_by_day_average(df, choosed_column, path, filetype):
    # gera gráficos considerando a média das probabilidades de contaminação dependendo do dia da semana em que ocorreu a notificação do infectado

    df_dict = get_dataframe_dict_to_calculate_average(df, choosed_column)
    named_days = ["Domingo", "Terça", "Quarta", "Quinta", "Sexta", "Sábado"]
    ordered_named_days = ["Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]

    generate_and_save_dataframe_chart(df_dict, named_days, ordered_named_days, path, filetype, "bar", "Dia da notificação")

def generate_charts_by_professor_student_average(df, choosed_column, path, filetype, professors_ids, students_ids):
    # gera gráficos considerando a média das probabilidades de contaminação dependendo se o infectado é professor ou aluno

    new_df = df.copy().assign(professor_student='')
    new_df.loc[new_df["academic_id"].isin(professors_ids), 'professor_student'] = 'professor'
    new_df.loc[new_df["academic_id"].isin(students_ids), 'professor_student'] = 'student'

    df_dict = get_dataframe_dict_to_calculate_average(new_df, choosed_column)
    df_index = ["Professor", "Estudante"]

    generate_and_save_dataframe_chart(df_dict, df_index, [], path, filetype, "bar", "Acadêmico")

def generate_charts_by_course_average(df, choosed_column, path, filetype, students_by_courses):
    # gera gráficos considerando a média das probabilidades de contaminação dependendo do curso do infectado

    new_df = df.copy().assign(student_course = '')

    for course in students_by_courses:
        new_df.loc[new_df["academic_id"].isin(students_by_courses[course]), choosed_column] = course

    new_df.drop(new_df[new_df[choosed_column] == ''].index, inplace=True)

    df_dict = get_dataframe_dict_to_calculate_average(new_df, choosed_column)

    all_courses = ["Geografia (L)", "Ciências Econômicas (B)", "Letras - Português (L)", "Letras - Espanhol (L)", "Pedagogia (L)", "História (L)", "Matemática (L)", "Administração (B)", "Ciência da Computação (B)", "Direito (B)", "Matemática Aplicada (B)", "Turismo (B)"]
    all_courses.sort() 
    all_courses_reverse = all_courses.copy()
    all_courses_reverse.sort(reverse=True) # na hora de plotar, a ordem fica invertida

    generate_and_save_dataframe_chart(df_dict, all_courses, all_courses_reverse, path, filetype, "barh", "Cursos")
    
def generate_chart_based_on_variants(df, choosed_column, path, filetype):
    df_dict = get_dataframe_dict_to_calculate_average(df, choosed_column)
    variants = ["Delta", "Ômicron"]

    generate_and_save_dataframe_chart(df_dict, variants, [], path, filetype, "bar", "Variantes")

def generate_charts_based_on_statistics(data):
    # gera gráficos com as estatísticas obtidas na simulação

    covid_variants = {}

    parent_path = "./images/"
    filetype = "pdf"
    df = pd.read_csv("results.csv", sep=";")
    df = df.query("variant != 'origin'")

    _, _, academics, professors, students, _, _ = data
    professors_ids, students_ids = get_professors_and_students_list(academics)
    students_by_courses = get_students_by_courses_dict(students_ids, academics, professors, students)

    for susceptible_mask in ["no_mask", "surgery_mask", "n95_mask"]:
        for variant in ["delta", "omicron"]:
            if variant not in covid_variants:
                covid_variants[variant] = {}

            if susceptible_mask not in covid_variants[variant]:
                covid_variants[variant][susceptible_mask] = df.query("variant == '%s' and susceptible_mask == '%s'" % (variant, susceptible_mask))
        
        variants_df = pd.concat([covid_variants["delta"][susceptible_mask], covid_variants["omicron"][susceptible_mask]])
        path_variants = parent_path + "variants/%s-" % susceptible_mask
        generate_chart_based_on_variants(variants_df, "variant", path_variants, filetype)

    for susceptible_mask in ["no_mask", "surgery_mask"]:
        new_df = df.query("variant == 'omicron' and infector_mask != 'n95_mask' and susceptible_mask != 'n95_mask'") # removendo casos que não serão considerados nessas comparações

        new_df = new_df.query("susceptible_mask == '%s'" % susceptible_mask)
        
        path_days = parent_path + "/days/%s-" % susceptible_mask
        path_people = parent_path + "/people/%s-" % susceptible_mask
        path_courses = parent_path + "/courses/%s-" % susceptible_mask

        generate_charts_by_day_average(new_df, "notification_day", path_days, filetype)
        generate_charts_by_professor_student_average(new_df, "professor_student", path_people, filetype, professors_ids, students_ids)
        generate_charts_by_course_average(new_df, "student_course", path_courses, filetype, students_by_courses)
