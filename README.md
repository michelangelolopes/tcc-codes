# Estratégia de modelagem de dados

1) receber dados de distribuição de salas para as turmas das disciplinas em um período letivo, em pdf
2) tratar os dados do pdf de forma a habilitar o seu uso, gerando um arquivo xlsx ou csv
3) ler os dados do novo arquivo e utilizá-los para extrair do sistema as informações detalhadas de cada turma
4) tratar os dados das turmas, para obter informações de alunos e professores
4) gerar "bancos de dados" para: alunos, professores, disciplinas, mapeamento de salas

# Estruturas de dados

room_mapping {
    day {
        hour {
            classroom {
                [component_code, component_class]
                ...
                ...
                ...
                [component_code, component_class]
            }
        }
    }
}

students_mapping {
    component_code {
        component_class {
            [student_1, ... student_n]
        }
    }
}

sheet_mapping {
    component_code = [component_class_1, ..., component_class_n]
    ...
    ...
}
