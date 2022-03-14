# Estratégia de modelagem de dados

1) receber dados de distribuição de salas para as turmas das disciplinas em um período letivo, em pdf
2) tratar os dados do pdf de forma a habilitar o seu uso, gerando um arquivo resultante em xlsx (ou csv)
3) ler os dados do novo arquivo e utilizá-los para extrair do sistema as informações detalhadas de cada turma
4) tratar os dados das turmas, para obter informações de alunos e professores
5) remover disciplinas e turmas que não foram importadas, para evitar erros futuros
6) gerar "bancos de dados" para: 
* mapeamento_salas(dia, hora, código_sala, id_disciplina)
* disciplinas(id_disciplina, código_turma, id_acadêmico) 
* acadêmicos(id_acadêmico, id_estudante, id_professor)
* alunos(id_aluno, curso)
* professores(id_professor)
* classrooms(código_sala, altura, largura, profundidade)

# Estruturas de dados

room_mapping {
    day {
        hour {
            classroom {
                [component_code, component_class]
            }
        }
    }
}

academics_mapping {
    component_code {
        component_class {
                [academic_1, academic_2, ... academic_n]
        }
    }
}

academics {
    academic_id [
        (professor_id, student_id), sendo um deles igual a string vazia sempre
    ]
}

professors [
    professor_instance_1, professor_instance_2, ..., professor_instance_n
]

students [
    student_instance_1, student_instance_2, ..., student_instance_n
]

classrooms [
    classroom_instance_1, classroom_instance_2, ..., classroom_instance_n
]

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
