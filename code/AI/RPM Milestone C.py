from PIL import Image
import numpy as np
import cv2

class Agent:
    def __init__(self):
        pass

    def Solve(self, prob):
        imgs = {k: self.load_img(prob.figures[k].visualFilename) for k in prob.figures}
        feats = {k: self.get_feats(imgs[k]) for k in imgs}
        
        if prob.problemType == '3x3':
            return self.solve_3(feats)
        elif prob.problemType == '2x2':
            return self.solve_2(feats)
        return -1

    def load_img(self, filename):
        img = Image.open(filename).convert('L')
        return np.array(img)

    def get_feats(self, img):
        _, thresh = cv2.threshold(img, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
        cnts, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        feat = {'num_shapes': 0, 'shapes': [], 'edges': cv2.Canny(thresh, 100, 200)}
        for c in cnts:
            area = cv2.contourArea(c)
            if area > 50:
                x, y, w, h = cv2.boundingRect(c)
                ar = float(w) / h
                peri = cv2.arcLength(c, True)
                approx = cv2.approxPolyDP(c, 0.04 * peri, True)
                shape = self.classify(approx)
                feat['shapes'].append({'area': area, 'ar': ar, 'peri': peri, 'shape': shape})
        feat['num_shapes'] = len(feat['shapes'])
        return feat

    def classify(self, approx):
        v = len(approx)
        if v == 3: return 'tri'
        elif v == 4: return 'quad'
        elif v == 5: return 'penta'
        elif v > 5: return 'circ'
        return 'unknown'

    def solve_3(self, feats):
        mtx = [['A', 'B', 'C'], ['D', 'E', 'F'], ['G', 'H', '']]
        trans = self.get_trans_3(feats, mtx)
        pred_feats = self.predict_3(feats, trans)
        return self.match_ans(feats, pred_feats, range(1, 9))

    def get_trans_3(self, feats, mtx):
        trans = {'rows': [], 'cols': []}
        for row in mtx:
            if '' not in row:
                t = self.get_diff(feats[row[0]], feats[row[1]], feats[row[2]])
                trans['rows'].append(t)
        for col in zip(*mtx):
            if '' not in col:
                t = self.get_diff(feats[col[0]], feats[col[1]], feats[col[2]])
                trans['cols'].append(t)
        return trans

    def get_diff(self, f1, f2, f3=None):
        diff = {'num_shapes_diff_1': f2['num_shapes'] - f1['num_shapes']}
        if f3:
            diff['num_shapes_diff_2'] = f3['num_shapes'] - f2['num_shapes']
        return diff

    def predict_3(self, feats, trans):
        last_row_trans = trans['rows'][1]
        pred_feats = {'num_shapes': feats['H']['num_shapes'] + last_row_trans['num_shapes_diff_2']}
        return pred_feats

    def match_ans(self, feats, pred_feats, opts):
        scores = {}
        for o in opts:
            o = str(o)
            sc = 0
            cand = feats[o]
            sc += abs(pred_feats['num_shapes'] - cand['num_shapes']) * 2
            pred_shapes = {shp['shape'] for shp in pred_feats.get('shapes', [])}
            cand_shapes = {shp['shape'] for shp in cand.get('shapes', [])}
            sc += len(pred_shapes.symmetric_difference(cand_shapes)) * 3
            scores[o] = sc
        return int(min(scores, key=scores.get))

    def solve_2(self, feats):
        trans = self.get_trans_2(feats)
        pred_feats = self.predict_2(feats, trans)
        return self.match_ans(feats, pred_feats, range(1, 7))

    def get_trans_2(self, feats):
        t1 = self.get_diff(feats['A'], feats['B'])
        t2 = self.get_diff(feats['A'], feats['C'])
        return {'A_B': t1, 'A_C': t2}

    def predict_2(self, feats, trans):
        avg_shapes_diff = (trans['A_B']['num_shapes_diff_1'] + trans['A_C']['num_shapes_diff_1']) // 2
        return {'num_shapes': feats['C']['num_shapes'] + avg_shapes_diff}
