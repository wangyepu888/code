from PIL import Image
import numpy as np
import cv2

class Agent:
    def __init__(self):
        pass

    def Solve(self, prob):
        imgs = {k: self.load_img(prob.figures[k].visualFilename) for k in prob.figures}
        feats = {k: self.get_feats(imgs[k]) for k in imgs}
        
        if prob.problemType == '2x2':
            return self.solve_2(feats)
        return -1

    def load_img(self, filename):
        img = Image.open(filename).convert('L')
        return np.array(img)

    def get_feats(self, img):
        _, thresh = cv2.threshold(img, 128, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        features = {
            'num_contours': len(contours)
        }
        return features

    def solve_2(self, feats):
  
        num_A = feats['A']['num_contours']
        num_B = feats['B']['num_contours']
        num_C = feats['C']['num_contours']


        expected_num_D = num_C + (num_C - num_B) 


        closest_match = None
        min_difference = float('inf')
        for option in range(1, 7):
            opt_key = str(option)
            if opt_key in feats:
                difference = abs(feats[opt_key]['num_contours'] - expected_num_D)
                if difference < min_difference:
                    closest_match = option
                    min_difference = difference

        return closest_match


agent = Agent()
