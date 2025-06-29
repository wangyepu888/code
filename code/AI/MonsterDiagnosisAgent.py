from itertools import combinations

class MonsterDiagnosisAgent:
    def __init__(self):
        self.vitamin_to_index = {}
        for i in range(26):
            self.vitamin_to_index[chr(ord('A') + i)] = i

    def solve(self, diseases, patient):
        effect_map = {'+': 1, '-': -1, '0': 0}
        num_vitamins = 26
        disease_effects = {}

        for disease_name in diseases:
            effects = diseases[disease_name]
            disease_effect = []
            for vitamin in effects:
                idx = self.vitamin_to_index[vitamin]
                while len(disease_effect) <= idx:
                    disease_effect.append(0)
                disease_effect[idx] = effect_map[effects[vitamin]]
            disease_effects[disease_name] = disease_effect

        patient_symptoms = [0] * num_vitamins
        for vitamin in patient:
            idx = self.vitamin_to_index[vitamin]
            patient_symptoms[idx] = effect_map[patient[vitamin]]

        disease_names = list(disease_effects.keys())
        num_diseases = len(disease_names)

        for k in range(1, num_diseases + 1):
            all_combinations = combinations(disease_names, k)
            for combination in all_combinations:
                net_effect = [0] * num_vitamins
                for disease in combination:
                    current_effect = disease_effects[disease]
                    for i in range(len(current_effect)):
                        net_effect[i] += current_effect[i]
                match = True
                for i in range(num_vitamins):
                    if net_effect[i] > 0:
                        if patient_symptoms[i] != 1:
                            match = False
                            break
                    elif net_effect[i] < 0:
                        if patient_symptoms[i] != -1:
                            match = False
                            break
                    else:
                        if patient_symptoms[i] != 0:
                            match = False
                            break
                if match:
                    return list(combination)
        return []
