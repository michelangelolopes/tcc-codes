generate_gnu_plot_file() {
    path=$1
    case_index=$2
    label_data=$3

    echo """
        set terminal pdf enhanced
        set encoding utf8

        set output \"$path/case_$case_index-gnu.pdf\"

        set key bottom right

        set xlabel \"$label_data\"
        set ylabel \"Probabilidade média de contaminação no Caso $case_index\"

        set key top left
        set style data histogram
        set style histogram cluster gap 1 errorbars
        set style fill solid border rgb \"black\"
        set auto x
        plot \
        \"$path/case_$case_index.csv\" u 2:5:xtic(1) t \"Sem máscara\", \
        \"$path/case_$case_index.csv\" u 3:6:xtic(1) t \"Máscara cirúrgica\", \
        \"$path/case_$case_index.csv\" u 4:7:xtic(1) t \"Máscara N95\", \
    """ > plot.gnu
}

parent_path="./images/"
options="days people courses"

read -a options_array <<< $options

for option in "${options_array[@]}"; do
    for case_index in $(seq 1 6); do
        path=$parent_path$option
        
        case $option in
            "days")
            label_data="Dia da notificação"
            ;;
            "people")
            label_data="Acadêmico"
            ;;
            "courses")
            label_data="Cursos"
            ;;
            *)
        esac

        generate_gnu_plot_file $path $case_index $label_data

        gnuplot plot.gnu
    done
done
