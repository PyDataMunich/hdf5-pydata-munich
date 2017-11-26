import time
import os
import tables as tb
from hurry.filesize import size


def main():
    here = os.path.abspath(os.path.dirname(__file__))
    data_dir = os.path.abspath(os.path.join(here, '..', 'data'))
    file_path = os.path.join(data_dir, 'big_file.h5')

    with tb.open_file(file_path, 'r') as hdf:
        table = hdf.root.Day_001.control
        print(table)
        print('Table size in memory: {}'.format(size(table.size_in_memory)))
        print('Table size on disk: {}'.format(size(table.size_on_disk)))
        print('Row size: {}'.format(size(table.rowsize)))

        # querying with numpy is possible only it the table fits in memory
        # t0 = time.time()
        # results = [x['heart_rate'] for x in table.read()
        #            if 60 < x['heart_rate'] < 70 and 40 < x['hematocrit'] < 60]
        # t1 = time.time()
        # print('Querying with numpy took {:.2f}ms'.format((t1 - t0) * 1000))

        # table.iterrows() returns an iterator that iterates over all rows.
        # This allow us to avoid loading the entire table in memory.
        t0 = time.time()
        results = [x['heart_rate'] for x in table.iterrows()
                   if 60 < x['heart_rate'] < 70 and 40 < x['hematocrit'] < 60]
        t1 = time.time()
        print('Querying with table.iterrows took {:.2f}ms'
              .format((t1 - t0) * 1000))

        t0 = time.time()
        results = [x['heart_rate'] for x in table.where(
            """((60 < heart_rate) & (heart_rate < 70)) & ((40 < hematocrit) & (hematocrit < 60))""")]
        t1 = time.time()
        print('Querying with table.where took {:.2f}ms'
              .format((t1 - t0) * 1000))

        t0 = time.time()
        results = [x['heart_rate'] for x in table.read_where(
            """((60 < heart_rate) & (heart_rate < 70)) & ((40 < hematocrit) & (hematocrit < 60))""")]
        t1 = time.time()
        print('Querying with table.read_where took {:.2f}ms'
              .format((t1 - t0) * 1000))

        # this won't work: you can't use Python's standard boolean operators in
        # NumExpr expressions
        condition = """(60 < heart_rate < 70) & (40 < hematocrit < 60)"""

        # this one works
        condition = """((60 < heart_rate) & (heart_rate < 70)) & ((40 < hematocrit) & (hematocrit < 60))"""
        # we can make it more readable
        cond0 = '((60 < heart_rate) & (heart_rate < 70))'
        cond1 = '((40 < hematocrit) & (hematocrit < 60))'
        condition = '{} & {}'.format(cond0, cond1)
        results = [x['heart_rate'] for x in table.read_where(condition)]
        print(len(results))

if __name__ == '__main__':
    main()