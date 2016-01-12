from time import time
import psycopg2
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
from gensim.utils import simple_preprocess
import multiprocessing
import re
import argparse


class DocIterator(object):

    def __init__(self, conn):
        self.conn = conn

    def __iter__(self):
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM articles;")
            for index, title, authors, subject, abstract, pubdate, arxid in cur:
                body = title + '. ' + abstract
                words = re.findall(r"[\w']+|[.,!?;]", body)
                tags = [index]
                yield TaggedDocument(words, tags)


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='trains model based on corpus in psql')
    parser.add_argument('dbname', help="Name of postgres database")
    parser.add_argument('model_name', help="Filename to save the model to")
    args = parser.parse_args()

    n_workers = multiprocessing.cpu_count()

    with psycopg2.connect(dbname=args.dbname) as conn:
        doc_iterator = DocIterator(conn)
        model = Doc2Vec(documents=doc_iterator, workers=n_workers)

    t_i = time()
    model.save('models/' + args.model_name)
    print("Time elapsed: %s seconds"%(time() - t_i))
    print("Model can be found at models/%s"%args.model_name)