class MonsterClassificationAgent:
    def __init__(self):
        pass

    def solve(self, samples, new_monster):
        pos_counts = {}
        neg_counts = {}
        total_pos = 0
        total_neg = 0

        for monster, label in samples:
            if label:
                total_pos +=1
                for feature, value in monster.items():
                    if feature not in pos_counts:
                        pos_counts[feature] = {}
                    if value not in pos_counts[feature]:
                        pos_counts[feature][value] = 0
                    pos_counts[feature][value] += 1
            else:
                total_neg +=1
                for feature, value in monster.items():
                    if feature not in neg_counts:
                        neg_counts[feature] = {}
                    if value not in neg_counts[feature]:
                        neg_counts[feature][value] = 0
                    neg_counts[feature][value] +=1

        pos_prob = total_pos / (total_pos + total_neg)
        neg_prob = total_neg / (total_pos + total_neg)
        from math import log
        pos_log_prob = log(pos_prob)
        neg_log_prob = log(neg_prob)

        for feature, value in new_monster.items():
     
            if feature in pos_counts and value in pos_counts[feature]:
                count = pos_counts[feature][value]
                feature_total = sum(pos_counts[feature].values())
                pos_log_prob += log((count + 1) / (feature_total + len(pos_counts[feature])))
            else:
                feature_total = sum(pos_counts.get(feature, {}).values())
                pos_log_prob += log(1 / (feature_total + len(pos_counts.get(feature, {})) + 1))
            # Calculate negative likelihood
            if feature in neg_counts and value in neg_counts[feature]:
                count = neg_counts[feature][value]
                feature_total = sum(neg_counts[feature].values())
                neg_log_prob += log((count + 1) / (feature_total + len(neg_counts[feature])))
            else:
                feature_total = sum(neg_counts.get(feature, {}).values())
                neg_log_prob += log(1 / (feature_total + len(neg_counts.get(feature, {})) + 1))

        return pos_log_prob > neg_log_prob
