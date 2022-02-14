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

## Dataframe das disciplinas

{"data": 
[[
        0               1
    0   Componente:     Código da disciplina - Nome da disciplina
    1   Turma:          Código da turma
    2   Docente(s):     Nome do professor
    3   Horário:        NaN,     

        Matrícula       Unnamed: 1      Nome        Curso       Situação
    0   Matrícula1      NaN             Aluno1      Curso1      Aprovado ou reprovado
    1   Matrícula2      NaN             Aluno2      Curso2      Aprovado ou reprovado,

        0
    0   Nenhum aluno solicitou matrícula para esta turma
]]}
