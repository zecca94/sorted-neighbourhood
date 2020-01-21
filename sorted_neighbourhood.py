#!/usr/bin/env python3

from operator import itemgetter
import py_stringmatching as sm
import py_entitymatching as em
import pandas as pd


def sorting_key_constructor(table_name, input_table):
    table = list()
    for i in range(0, len(input_table)):
        table.append([table_name, input_table[i][0], input_table[i][1]])
    return table


def matching(a, b, similarity_function):
    tokenizer = sm.QgramTokenizer(qval=2)
    if similarity_function == 'dice':
        dice = sm.Dice()
        if dice.get_sim_score(tokenizer.tokenize(a), tokenizer.tokenize(b)) >= 0.75:
            return True
        else:
            return False
    if similarity_function == 'hamming':
        hd = sm.HammingDistance()
        if hd.get_sim_score(a, b) >= 0.75:
            return True
        else:
            return False
    if similarity_function == 'jaccard':
        jaccard = sm.Jaccard()
        if jaccard.get_sim_score(tokenizer.tokenize(a), tokenizer.tokenize(b)) >= 0.75:
            return True
        else:
            return False
    if similarity_function == 'jaro winkler':
        jw = sm.JaroWinkler()
        if jw.get_sim_score(a, b) >= 0.75:
            return True
        else:
            return False
    if similarity_function == 'levenshtein':
        lev = sm.Levenshtein()
        if lev.get_sim_score(a, b) >= 0.75:
            return True
        else:
            return False


def sorted_neighbourhood(table, sorting_order, window_size, similarity_measure):
    # table should have the format [['table', 'id', 'key'], [...], ...] (omit control)
    # check validity of sorting_order parameter value
    if sorting_order not in ['asc', 'desc']:
        print("Sorting order value must be 'asc' or 'desc'")
        return []
    # check validity of window_size parameter value
    try:
        int(window_size)
    except ValueError:
        print("Window size value must be an integer number")
        return []
    if window_size % 2 == 0:
        print("Window size must be an odd number")
        return []
    if window_size > len(table):
        print("Window size greater that the table size")
        return []
    # check validity of similarity_measure parameter value
    if similarity_measure not in ['dice', 'hamming', 'jaccard', 'jaro winkler', 'levenshtein']:
        print("Similarity measure value must be one among the following: ['dice', 'hamming', 'jaccard', 'jaro winkler', 'levenshtein']")
        return []

    # sort the table elements according to the sorting key
    if sorting_order == 'asc':
        try:
            sorted_table = sorted(table, key=itemgetter(2))
        except Exception as e:
            print("Table must have the format [['table', 'id', 'key'], [...], ...]")
            return []
    else:
        try:
            sorted_table = sorted(table, key=itemgetter(2), reverse=True)
        except Exception as e:
            print("Table must have the format [['table', 'id', 'key'], [...], ...]")
            return []

    # do the comparison of each element in its window
    offset = window_size // 2
    clusters = list()
    for i in range(0, len(sorted_table)):
        cluster = set()
        cluster.add((sorted_table[i][0], sorted_table[i][1]))
        for j in range(i - offset, i + offset + 1):
            if (j >= 0) and (j < len(sorted_table)) and (i != j) and (sorted_table[i][0] != sorted_table[j][0]):
                match = matching(sorted_table[i][2], sorted_table[j][2], similarity_measure)
                if match is True:
                    cluster.add((sorted_table[j][0], sorted_table[j][1]))
        clusters.append(cluster)

    return clusters


def main():
    # starting from the original table, i should call a function to obtain the reduced one in the right format
    # for the moment, i directly create an example of reduced table to test the function
    table = list()
    table.append(['a', 1, "MSKAD98"])
    table.append(['a', 2, "MSKAD98"])
    table.append(['a', 3, "MSKAD97"])
    table.append(['a', 4, "MSCSC97"])
    table.append(['a', 5, "DDMCO91"])
    table.append(['a', 6, "DDMCO98"])
    table.append(['a', 7, "DRMCO97"])
    table.append(['a', 8, "RSHCO98"])
    table.append(['a', 9, "MTRSC99"])
    table.append(['a', 10, "MRRAD00"])
    table.append(['a', 11, "RTRCH94"])
    table.append(['a', 12, "RTRCH96"])
    table.append(['a', 13, "ATRAD94"])
    table.append(['a', 14, "DMSCO91"])
    table.append(['a', 15, "DMSCO91"])
    table.append(['a', 16, "DMSCO93"])
    table.append(['a', 17, "DMSCG94"])
    table.append(['a', 18, "RTRCH95"])
    table.append(['a', 19, "RTRCH99"])
    table.append(['a', 20, "RTRCH00"])

    # application on the case Abt-Buy
    path_a = 'datasets/Abt.csv'
    path_b = 'datasets/Buy.csv'
    a = pd.read_csv(path_a, encoding='latin-1')
    first_table = sorting_key_constructor('a', a.values.tolist())
    b = pd.read_csv(path_b, encoding='latin-1')
    second_table = sorting_key_constructor('b', b.values.tolist())
    complete_table = first_table + second_table
    print('Number of entities in the original combined datasets: ' + str(len(complete_table)))

    clusters = sorted_neighbourhood(complete_table, 'asc', 9, 'levenshtein')

    # further step: give a sense to clusters (delete repetitions and subsets, a cluster for each entity)
    # possible improvement: merge clusters with elements in common
    i = 0
    while i < len(clusters):
        j = i + 1
        while (j < len(clusters)):
            # if the clusters have some elements in common, merge them into the first one
            if len(clusters[i].intersection(clusters[j])) > 0:
                clusters[i].update(clusters[j])
                clusters.pop(j)
            else:
                j = j + 1
        i = i + 1
    print('Number of entities after duplicate detection: ' + str(len(clusters)))
    print(clusters)


if __name__ == "__main__":
    main()
