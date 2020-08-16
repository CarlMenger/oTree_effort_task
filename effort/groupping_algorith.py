import random
import copy
import logging


def create_group_matrix():
    # find if starting from index 0 or 1 gives less average differences between pairs
    def pairing_algorithm(scores_all):
        mean_differences = [-1, -1]
        pair_combinations = [[], []]
        for shift in range(2):
            difference = 0
            for index in range(0, len(scores_all) - shift - 1, 2):
                difference += abs(scores_all[index + shift] - scores_all[index + shift + 1])
                pair_combinations[shift].append([scores_all[index + shift], scores_all[index + shift + 1]])
            mean_differences[shift] = difference / (len(scores_all))
        print(mean_differences)
        print(pair_combinations[0])
        print(pair_combinations[1])
        return pair_combinations[mean_differences.index(min(mean_differences))]

    # FIXME: pair the leftover subjects if even num_subjects
    # points_ids --> dict of id:points, point_matrix --> list of list of points (same as group_matrix)
    def convert_points_to_ids(points_ids, point_matrix):
        #id_matrix = copy.deepcopy(point_matrix)
        for group_index in range(len(point_matrix)):
            for point_index in range(len(point_matrix[group_index])):
                point_matrix[group_index][point_index] = points_ids.pop(point_matrix[group_index][point_index], -1)
        return point_matrix

    def create_point_ids(points_all):
        return dict(list(enumerate(points_all, start=1)))

    def reverse_keys_values(dictionary):
        return dict((v, k) for k, v in dictionary.items())

    points_all = random.sample(range(1, 50), 21)
    point_matrix = pairing_algorithm(sorted(points_all))
    reverse_points_ids = create_point_ids(points_all)
    points_ids = reverse_keys_values(reverse_points_ids)

    print(f"Point ids: {points_ids}")
    # FIXME: return this to original state
    output = convert_points_to_ids(points_ids, point_matrix)
    logging.info(f"group_matrix is : {output}")
    print(f"This is group matrix/output is: {output}")
    return output
    # return convert_points_to_ids(points_ids, point_matrix)


def group_based_on_score(self):
    output = self.create_group_matrix()
    self.set_group_matrix(output)


create_group_matrix()