import os
import sys
from typing import Dict, List

import pandas as pd

from decimal import Decimal


class CsvAnalysisDataSource:
    def __init__(self, path):
        self.filepath = os.path.join(os.getcwd(), path)
        self.df = pd.read_csv(self.filepath)

    def books_count(self) -> int:
        return self.df.shape[0]

    def prices_average(self) -> Decimal:
        return Decimal(self.df['price'].mean())

    def rating_distribution(self) -> Dict[int, int]:
        return self.df['rating'].value_counts().to_dict()

    def categories_books_count(self) -> Dict[str, int]:
        return self.df.groupby('category')['id'].count().to_dict()

    def categories_prices_data(self) -> Dict[str, Dict[str, float]]:
        dg = self.df.groupby('category')['price'].describe().transpose().to_dict()
        return dg

    def books_best_rated(self, qty: int = 0) -> List[str]:
        dg = self.df[['id', 'title','rating']].sort_values(by='rating', ascending=False)['id']
        if qty > 0:
            dg = dg[:qty]
        return dg.to_list()

    def books_filtered_by_price(self, min: float = 0, max: float = sys.float_info.max, qty: int = 0) -> List[str]:
        data = self.df[(self.df.price > min) & (self.df.price < max)]['id']
        if qty > 0:
            data = data[:qty]
        return data.to_list()