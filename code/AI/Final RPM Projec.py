import cv2
import numpy as np
from PIL import Image, ImageOps
from RavensProblem import RavensProblem

class Agent:
    def __init__(self):
        self.images = {}
        self.answers = []

    def Solve(self, problem):
        self.problem = problem
        problem_set = problem.problemSetName
        self.load_images()

        if problem_set in ["Basic Problems B", "Test Problems B", "Challenge Problems B", "Raven's Problems B"]:
            return self.solve_b()
        elif problem_set in ["Basic Problems C", "Test Problems C", "Challenge Problems C", "Raven's Problems C"]:
            return self.solve_c()
        elif problem_set in ["Basic Problems D", "Test Problems D", "Challenge Problems D", "Raven's Problems D"]:
            return self.solve_d()
        elif problem_set in ["Basic Problems E", "Test Problems E", "Challenge Problems E", "Raven's Problems E"]:
            return self.solve_e()
        else:
            return -1

    def load_images(self):
        for name, fig in self.problem.figures.items():
            img = cv2.imread(fig.visualFilename, 0)
            if img is not None:
                _, img = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)
                self.images[name] = img
            else:
                self.images[name] = None

        self.answers = []
        num_options = 6 if self.problem.problemType == "2x2" else 8
        for i in range(1, num_options + 1):
            img = self.images.get(str(i))
            if img is not None:
                self.answers.append(img)
            else:
                img = cv2.imread(self.problem.figures[str(i)].visualFilename, 0)
                if img is not None:
                    _, img = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)
                    self.answers.append(img)
                else:
                    self.answers.append(None)

    def solve_b(self):
        img_a = self.images['A']
        img_b = self.images['B']
        img_c = self.images['C']

        if any(img is None for img in [img_a, img_b, img_c]):
            return -1

        index_row, sim_row = self.compare(img_a, img_b)
        index_col, sim_col = self.compare(img_a, img_c)

        if sim_row > sim_col:
            transformed_img = self.transformation(img_c)[index_row]
        else:
            transformed_img = self.transformation(img_b)[index_col]

        max_similarity = 0
        best_option = -1
        for idx, ans_img in enumerate(self.answers):
            if ans_img is not None:
                similarity = self.tversky(transformed_img, ans_img)
                if similarity > max_similarity:
                    max_similarity = similarity
                    best_option = idx + 1

        return best_option

    def solve_c(self):
        img_g = self.images['G']
        img_h = self.images['H']

        if any(img is None for img in [img_g, img_h]):
            return -1

        diff_gh = self.dpr(img_g, img_h)
        inter_gh = self.ipr(img_g, img_h)

        diffs = []
        inters = []
        for ans_img in self.answers:
            if ans_img is not None:
                diffs.append(self.dpr(img_h, ans_img))
                inters.append(self.ipr(img_h, ans_img))
            else:
                diffs.append(float('inf'))
                inters.append(float('inf'))

        max_thresh = diff_gh + 1.0
        min_thresh = diff_gh - 1.0

        candidates = []
        for idx, diff in enumerate(diffs):
            if min_thresh <= diff <= max_thresh:
                candidates.append((idx, inters[idx]))

        if not candidates:
            index = np.argmin(np.abs(np.array(diffs) - diff_gh))
            return index + 1

        index, _ = min(candidates, key=lambda x: abs(x[1] - inter_gh))
        return index + 1

    def solve_d(self):
        img_a = self.images['A']
        img_b = self.images['B']
        img_c = self.images['C']
        img_e = self.images['E']
        img_f = self.images['F']
        img_g = self.images['G']
        img_h = self.images['H']

        if any(img is None for img in [img_a, img_b, img_c, img_e, img_f, img_g, img_h]):
            return -1

        dpr_gh = self.dpr(img_g, img_h)
        ipr_gh = self.ipr(img_g, img_h)

        dpr_ae = self.dpr(img_a, img_e)
        ipr_ae = self.ipr(img_a, img_e)

        dpr_fa = self.dpr(img_f, img_a)
        ipr_fa = self.ipr(img_f, img_a)

        diffs_h = []
        inters_h = []
        diffs_d = []
        inters_d = []
        diffs_i = []
        inters_i = []

        for ans_img in self.answers:
            if ans_img is not None:
                diffs_h.append(self.dpr(img_h, ans_img))
                inters_h.append(self.ipr(img_h, ans_img))
                diffs_d.append(self.dpr(img_e, ans_img))
                inters_d.append(self.ipr(img_e, ans_img))
                diffs_i.append(self.dpr(img_b, ans_img))
                inters_i.append(self.ipr(img_b, ans_img))
            else:
                diffs_h.append(float('inf'))
                inters_h.append(float('inf'))
                diffs_d.append(float('inf'))
                inters_d.append(float('inf'))
                diffs_i.append(float('inf'))
                inters_i.append(float('inf'))

        thresh_h = (dpr_gh - 1.0, dpr_gh + 1.0)
        thresh_d = (dpr_ae - 1.0, dpr_ae + 1.0)
        thresh_i = (dpr_fa - 1.0, dpr_fa + 1.0)

        best_option = self.evaluate_options(
            diffs_h, inters_h, thresh_h, ipr_gh,
            diffs_d, inters_d, thresh_d, ipr_ae,
            diffs_i, inters_i, thresh_i, ipr_fa
        )

        return best_option

    def evaluate_options(self, diffs_h, inters_h, thresh_h, ipr_h,
                               diffs_d, inters_d, thresh_d, ipr_d,
                               diffs_i, inters_i, thresh_i, ipr_i):
        checks = []
        indices = []

        check_h, idx_h = self.get_best_match(diffs_h, inters_h, thresh_h, ipr_h)
        checks.append(check_h)
        indices.append(idx_h)

        check_d, idx_d = self.get_best_match(diffs_d, inters_d, thresh_d, ipr_d)
        checks.append(check_d)
        indices.append(idx_d)

        check_i, idx_i = self.get_best_match(diffs_i, inters_i, thresh_i, ipr_i)
        checks.append(check_i)
        indices.append(idx_i)

        min_check = min(checks)
        min_idx = checks.index(min_check)
        final_index = indices[min_idx]

        return final_index + 1

    def get_best_match(self, diffs, inters, thresh, ipr):
        min_thresh, max_thresh = thresh
        candidates = []
        for idx, diff in enumerate(diffs):
            if min_thresh <= diff <= max_thresh:
                candidates.append((idx, inters[idx]))

        if not candidates:
            idx = np.argmin(np.abs(np.array(diffs) - ipr))
            check = abs(diffs[idx] - ipr)
        else:
            idx, val = min(candidates, key=lambda x: abs(x[1] - ipr))
            check = abs(val - ipr)
        return check, idx

    def solve_e(self):
        img_a = self.images['A']
        img_b = self.images['B']
        img_c = self.images['C']
        img_g = self.images['G']
        img_h = self.images['H']

        if any(img is None for img in [img_a, img_b, img_c, img_g, img_h]):
            return -1

        best_index = self.bitwise(img_a, img_b, img_c, img_g, img_h, self.answers)
        return best_index

    def bitwise(self, img1, img2, img_c, img_g, img_h, answers):
        operations = {
            'or': cv2.bitwise_or(img1, img2),
            'xor': cv2.bitwise_xor(img1, img2),
            'not_xor': cv2.bitwise_not(cv2.bitwise_xor(img1, img2)),
            'and': cv2.bitwise_and(img1, img2)
        }
        similarities = {key: self.tversky(result, img_c) for key, result in operations.items()}
        max_op = max(similarities, key=similarities.get)
        if max_op == 'or':
            combined_img = cv2.bitwise_or(img_g, img_h)
        elif max_op == 'xor':
            combined_img = cv2.bitwise_xor(img_g, img_h)
        elif max_op == 'not_xor':
            combined_img = cv2.bitwise_not(cv2.bitwise_xor(img_g, img_h))
        else:
            combined_img = cv2.bitwise_and(img_g, img_h)
        sims = [self.tversky(combined_img, ans_img) if ans_img is not None else -1 for ans_img in answers]
        return sims.index(max(sims)) + 1

    def transformation(self, img_cv):
        img = Image.fromarray(img_cv)
        transformations = [img.rotate(angle) for angle in [90, 180, 270]]
        transformations += [ImageOps.flip(img.rotate(angle)) for angle in [90, 180, 270]]
        transformations += [ImageOps.flip(img), img]
        return [np.array(t).astype(np.uint8) for t in transformations]

    def compare(self, img1_cv, img2_cv):
        transformations = self.transformation(img1_cv)
        similarities = [self.tversky(t_img, img2_cv) for t_img in transformations]
        max_similarity = max(similarities)
        best_index = similarities.index(max_similarity)
        return best_index, max_similarity

    def tversky(self, img1, img2):
        set_a, set_b = img1 == 0, img2 == 0
        intersection = np.logical_and(set_a, set_b)
        only_a = np.logical_and(set_a, ~set_b)
        only_b = np.logical_and(~set_a, set_b)
        numerator = np.sum(intersection)
        denominator = numerator + 0.7 * np.sum(only_a) + 0.3 * np.sum(only_b)
        return 0 if denominator == 0 else numerator / denominator

    def dpr(self, img1, img2):
        return (np.sum(img1 == 0) - np.sum(img2 == 0)) / img1.size

    def ipr(self, img1, img2):
        intersection = np.logical_and(img1 == 0, img2 == 0)
        inter_pixels = np.sum(intersection)
        total_pixels_img1 = np.sum(img1 == 0)
        total_pixels_img2 = np.sum(img2 == 0)
        if total_pixels_img1 == 0 or total_pixels_img2 == 0:
            return 0
        return (inter_pixels / total_pixels_img1) - (inter_pixels / total_pixels_img2)
