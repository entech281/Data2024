# abuse a google sheet using a tab as a table
from gspread.utils import ValueRenderOption
from pydantic import BaseModel
import pandas as pd

import gspread


class Table:
    def __init__(self, key_cols: list[str], model_class,records: list[BaseModel]):
        self.key_cols = key_cols
        self.model_class = model_class
        self.records = records

    def select_all(self):
        return self.records

    def select_for_key(self,query_dict):
        results = []
        for r in self.records:
            model_dict = r.model_dump()

            if query_dict.items() <= model_dict.items():
                results.append(r)
        return results

    def update_row(self,to_update: BaseModel):
        #worksheet.update
        #https://github.com/maybelinot/df2gspread
        #https: // pypi.org / project / gspread - dataframe /
        pass

    def __len__(self):
        return len(self.records)

def load_table(worksheet,model_class,key_columns) -> Table:
    data_dict = worksheet.get_all_records(empty2zero=False,default_blank="", value_render_option=ValueRenderOption.unformatted)

    records = []
    print("Data Out=",data_dict)
    for r in data_dict:
        m = model_class(**r)
        records.append(m)
        print(m.model_dump())
    return Table(key_columns,model_class,records)






