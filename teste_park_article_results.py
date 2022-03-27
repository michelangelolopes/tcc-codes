import math

from lib import file_operations


from flask import Flask, request
from flask_cors import CORS, cross_origin
 
app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

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

    return infection_probability
    # print(ventilation_volume, duration_time, "%.2f" % (100 * infection_probability), sep="\t\t")

@app.route('/mult', methods=["POST"])
@cross_origin()
def mult():
    return "funcionou"
    
@app.route('/')
def main():
    default_values = Default(infectors_count=1, quantum_generation_rate=48, breathing_rate=0.3, room_volume=168)
    duration_ventilation_list = file_operations.load_parameters_from_txt_file("park_examples.txt")

    durations = [float(duration) for duration in duration_ventilation_list[6:10]]
    ventilations = [float(duration) for duration in duration_ventilation_list[0:6]]

    infection_prob_by_ventilation_rate = {}
    count = 1

    for duration_time in durations:
        for ventilation_rate in ventilations:
            infection_prob_by_ventilation_rate['case%d' % count] = wells_riley_equation(default_values, duration_time, ventilation_rate)
            count += 1
        
    return infection_prob_by_ventilation_rate

if __name__ == "__main__":
    main()