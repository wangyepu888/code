import cv2
import numpy as np
class Agent:
    def __init__(self):
        pass
    def Solve(self, problem):
        self.problem_type = problem.problemType
        self.figures = problem.figures
        self.images = {}
        self.options = []
        self.load_and_prepare_images()

        if self.problem_type == '2x2':
            return self.solve_2x2()
        elif self.problem_type == '3x3':
            return self.solve_3x3()
        else:
            return -1
    def load_and_prepare_images(self):
        for name, fig in self.figures.items():
            img = cv2.imread(fig.visualFilename, cv2.IMREAD_GRAYSCALE)
            if img is not None:
                img = cv2.resize(img, (100, 100))
                _, img = cv2.threshold(img, 128, 255, cv2.THRESH_BINARY)
                self.images[name] = img
        for i in range(1, 9):
            key = str(i)
            if key in self.images:
                self.options.append(self.images[key])
    def solve_2x2(self):
        A = self.images.get('A')
        B = self.images.get('B')
        C = self.images.get('C')

        if A is None or B is None or C is None:
            return -1

        operations = ['bitwise_and', 'bitwise_or', 'bitwise_xor', 'add', 'subtract']
        best_op = None
        highest_score = -1

        for op in operations:
            result = self.apply_op(A, B, op)
            score = self.similarity(result, C)
            if score > highest_score:
                highest_score = score
                best_op = op

        predicted1 = self.apply_op(C, B, best_op)
        predicted2 = self.apply_op(C, A, best_op)
        predicted_images = [predicted1, predicted2]

        best_match = -1
        max_similarity = -1
        for predicted in predicted_images:
            for idx, option in enumerate(self.options):
                similarity = self.similarity(predicted, option)
                if similarity > max_similarity:
                    max_similarity = similarity
                    best_match = idx + 1

        return best_match

    def solve_3x3(self):
        positions = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
        for pos in positions:
            if pos not in self.images:
                return -1

        op_row1 = self.find_best_op(self.images['A'], self.images['B'], self.images['C'])
        op_row2 = self.find_best_op(self.images['D'], self.images['E'], self.images['F'])

        if op_row1 == op_row2 and op_row1 is not None:
            best_op = op_row1
            predicted_row = self.apply_op(self.images['G'], self.images['H'], best_op)
        else:
            predicted_row = None

        op_col1 = self.find_best_op(self.images['A'], self.images['D'], self.images['G'])
        op_col2 = self.find_best_op(self.images['B'], self.images['E'], self.images['H'])

        if op_col1 == op_col2 and op_col1 is not None:
            best_op = op_col1
            predicted_col = self.apply_op(self.images['C'], self.images['F'], best_op)
        else:
            predicted_col = None

        if predicted_row is not None and predicted_col is not None:
            predicted = self.apply_op(predicted_row, predicted_col, 'bitwise_or')
        elif predicted_row is not None:
            predicted = predicted_row
        elif predicted_col is not None:
            predicted = predicted_col
        else:
            predicted = self.apply_op(self.images['G'], self.images['H'], 'bitwise_xor')

        best_match = -1
        max_similarity = -1
        for idx, option in enumerate(self.options):
            similarity = self.similarity(predicted, option)
            if similarity > max_similarity:
                max_similarity = similarity
                best_match = idx + 1

        return best_match

    def find_best_op(self, img1, img2, target):
        if target is None:
            return None

        operations = ['bitwise_and', 'bitwise_or', 'bitwise_xor', 'add', 'subtract']
        highest_score = -1
        best_op = None

        for op in operations:
            result = self.apply_op(img1, img2, op)
            score = self.similarity(result, target)
            if score > highest_score:
                highest_score = score
                best_op = op

        return best_op

    def apply_op(self, img1, img2, operation):
        if operation == 'bitwise_and':
            return cv2.bitwise_and(img1, img2)
        elif operation == 'bitwise_or':
            return cv2.bitwise_or(img1, img2)
        elif operation == 'bitwise_xor':
            return cv2.bitwise_xor(img1, img2)
        elif operation == 'add':
            return cv2.add(img1, img2)
        elif operation == 'subtract':
            return cv2.absdiff(img1, img2)
        else:
            return img1

    def similarity(self, img1, img2):
        intersection = np.sum(np.logical_and(img1 == 0, img2 == 0))
        union = np.sum(np.logical_or(img1 == 0, img2 == 0))
        if union == 0:
            return 0
        return intersection / union
