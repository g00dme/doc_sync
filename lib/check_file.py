import logging
from unittest import skip

from lib.utils import clean_spaces, color_diff_visible

import numpy as np
import pandas as pd

class Metals_table:
    def __init__(self,path,fe_page_name=['Черный металл (ЧМ)'],skiprows=3):
        self.drop_columns=['Прибыло (т.)','Убыло (т.)','Состоит (т.)']
        self.path=path
        self.logger=logging.getLogger(__name__)
        self.clean=np.vectorize(clean_spaces)

        self.str_col=['Наименование документа','Поставщик','Получатель']

        self.load_file(path,skiprows=skiprows)
        for key, page in self.file.items():
            page=page.drop([0])
            page=page.set_index('№        документа')
            page=page.dropna(axis=1)
            print(key)
            self.file[key][self.str_col]=self.clean(self.file[key][self.str_col])

        self.fe_page=self.file[fe_page_name]   
        self.fe_check= self.fe_page.drop(self.drop_columns,axis=1)   
    def load_file(self,path,skiprows=3):
        self.file=pd.read_excel(path,sheet_name=None,skiprows=skiprows)
    def check_page(self,page,page_name='Testing'):
        page=page.drop(self.drop_columns,axis=1)

        fe_page=self.fe_page
        fe_page=fe_page.loc[page.index]

        page[self.str_col]=self.clean(page[self.str_col])
        fe_page[self.str_col]=self.clean(fe_page[self.str_col])

        unmatch=(page==fe_page)

        fe_page=fe_page[~unmatch].dropna(axis=1,thresh=1)
        fe_page=fe_page[~unmatch].dropna(axis=0,thresh=1)
        fe_page=fe_page.stack()

        page=page[~unmatch].dropna(axis=1,thresh=1)
        page=page[~unmatch].dropna(axis=0,thresh=1)
        page=page.stack()

        mismatches=pd.concat([page,fe_page],join='inner',axis=1)
        mismatches.columns=['Железо', page_name]

        return mismatches
    def check_file(self):
        for name,page in self.file.items():
            mismatches=self.check_page(page,name)
            for row in mismatches.index:
                self.logger.warning(row)
                color_diff_visible(res.loc[row,'Железо'], res.loc[row,name],self.logger)
