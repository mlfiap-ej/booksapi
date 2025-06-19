import sys

parquet_filename = sys.argv[1]
print(parquet_filename)

if not parquet_filename:
    print("informar arquivo")
    sys.exit(1)

###

import pandas as pd
from sqlalchemy import create_engine

pd1 = pd.read_parquet(parquet_filename)
engine = create_engine("sqlite:///{}.db".format(parquet_filename.split(".")[0]))
pd1.to_sql("books", con=engine)
