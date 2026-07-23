from io import BytesIO

from docxtpl import DocxTemplate
import docx
from docxcompose.composer import Composer

import logging

import pandas as pd

from lib.utils import clean_spaces, diff_visible

logger=logging.getLogger(__name__)
logger.propagate = True
class Metals_table:
    def __init__(self,path,fe_page_name='Черный металл (ЧМ)',skiprows=3,col_numb=9):
        self.drop_columns=['Прибыло (т.)','Убыло (т.)','Состоит (т.)']
        self.path=path
        self.logger=logging.getLogger(__name__)

        self.str_col=['Наименование документа','Поставщик','Получатель']

        self.load_file(path,col_numb=col_numb,skiprows=skiprows)
        for key, page in self.file.items():
            page=page.drop([0])
            page=page.set_index('№        документа')
            self.file[key]=page.dropna(thresh=1)

        self.fe_page=self.file[fe_page_name]   
        self.fe_check= self.fe_page.drop(self.drop_columns,axis=1)   
    def load_file(self,path,skiprows=3,col_numb=9):
        try:
            self.file=pd.read_excel(path,usecols=range(col_numb) ,sheet_name=None,skiprows=skiprows)
            self.logger.debug(f'Loaded {path}')
        except:
            self.logger.error(f'File {path} not found')
            raise FileNotFoundError()

    def check_page(self,page,page_name='Testing'):
        if len(page[page.isna().any(axis=1)])>=1:
            logging.warning(page[page.isna().any(axis=1)])                

        fe_page=self.fe_page
        fe_page=fe_page.loc[page.index]

        page=page.drop(self.drop_columns,axis=1)
        fe_page=fe_page.drop(self.drop_columns,axis=1)

        page[self.str_col]=page[self.str_col].map(clean_spaces)
        fe_page[self.str_col]=fe_page[self.str_col].map(clean_spaces)
        unmatch=(page==fe_page)

        fe_page=fe_page[~unmatch].dropna(axis=1,thresh=1)
        fe_page=fe_page[~unmatch].dropna(axis=0,thresh=1)
        fe_page=fe_page.stack()

        page=page[~unmatch].dropna(axis=1,thresh=1)
        page=page[~unmatch].dropna(axis=0,thresh=1)
        page=page.stack()

        mismatches=pd.concat([page,fe_page],join='inner',axis=1)
        mismatches.columns=['Железо', page_name]

        for row in mismatches.index:
                line=diff_visible(mismatches.loc[row,'Железо'], mismatches.loc[row,page_name])
                self.logger.warning(str(row)+'\n'+line)
        return mismatches
    def check_file(self):
        self.logger.info("_____________________\n"+f'Checking pages:\n{" | ".join(self.file.keys())}'+"\n_____________________")
        for name,page in self.file.items():
            res=self.check_page(page,name)
            line='✅' if len(res)==0 else f'❌ Mismatches: {len(res)}'
            self.logger.info(name.capitalize() + line)
def add_to_file(mainP, templ,context):
    doc=DocxTemplate(templ)
    doc.render(context)
    
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    try:
        main=Composer(docx.Document(mainP))
        logger.debug(f'loaded {mainP}')
    except FileNotFoundError:
        logger.error(f'File not found: {mainP}')
    appended=docx.Document(buffer)
    
    main.append(appended)
    main.save(mainP)
