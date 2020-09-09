import random
import copy
import logging


def create_group_matrix():
    # find if starting from index 0 or 1 gives less average differences between pairs
    def pairing_algorithm(scores_all):
        pair_combinations = []
        for index in range(0, len(scores_all), 2):
            try:
                pair_combinations.append([scores_all[index], scores_all[index + 1]])
            except IndexError:
                # except is point pairing if uneven players, adding second highest score to be paired with 3rd and 1 st
                pair_combinations.append([scores_all[index], scores_all[index - 1]])

        return pair_combinations

    # add ids to point matrix
    def create_point_ids(points_all):
        return dict(enumerate(points_all, start=1))

    # points_ids --> dict of id:points, point_matrix --> list of list of points (same as group_matrix)
    def convert_points_to_ids(points_ids, point_matrix):
        for group_index in range(len(point_matrix)):
            for point_index in range(len(point_matrix[group_index])):
                value = point_matrix[group_index][point_index]
                try:
                    key = (list(points_ids.keys())[list(points_ids.values()).index(value)])
                    point_matrix[group_index][point_index] = key
                    points_ids.pop(key, -999)
                except ValueError:
                    # if uneven players, point matrix has one more element than ids, uses last
                    point_matrix[group_index][point_index] = point_matrix[group_index-1][point_index]
        return point_matrix



    """def reverse_keys_values(dictionary):
        return dict((v, k) for k, v in dictionary.items())"""

   # points_all = random.sample(range(1, 50), 5)
    points_all = [7,5,5,7,3]
    #print(f"points_all: {points_all}")
    point_matrix = pairing_algorithm(sorted(points_all))
    print(f"pair_combinations: {point_matrix}")
    points_ids = create_point_ids(points_all)
    """    reverse_points_ids = create_point_ids(points_all)
    print(f"pont ids: {reverse_points_ids}")
    points_ids = reverse_keys_values(reverse_points_ids) # FIXME it  removes duplicates"""

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


#  TODO: dont fuck with dic, use list, index == id, pop remove em