import math

from lib import file_operations

class Default:
    def __init__(self, infectors_count, quantum_generation_rate, breathing_rate, room_volume):
        self.infectors_count = infectors_count
        self.quantum_generation_rate = quantum_generation_rate
        self.breathing_rate = breathing_rate
        self.room_volume = room_volume

def wells_riley_equation(default_values, duration_time, ventilation_rate):
    ventilation_volume = default_values.room_volume * ventilation_rate
    
    n = (default_values.infectors_count * default_values.quantum_generation_rate * default_values.breathing_rate * duration_time) / ventilation_volume
    infection_probability = 1 - math.exp(-n)

    print(ventilation_volume, duration_time, "%.2f" % (100 * infection_probability), sep="\t\t")

def main():
    default_values = Default(infectors_count=1, quantum_generation_rate=48, breathing_rate=0.3, room_volume=168)
    duration_ventilation_list = file_operations.load_parameters_from_txt_file("park_examples.txt")

    durations = [float(duration) for duration in duration_ventilation_list[6:10]]
    ventilations = [float(duration) for duration in duration_ventilation_list[0:6]]

    for duration_time in durations:
        for ventilation_rate in ventilations:
            wells_riley_equation(default_values, duration_time, ventilation_rate)
        print()

if __name__ == "__main__":
    main()