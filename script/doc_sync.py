import pandas as pd
import numpy as np
import docx
from docxtpl import DocxTemplate
from docxcompose.composer import Composer

from io import BytesIO
from pathlib import Path
import sys
import os

import logging
import re

def add_to_file(mainP, templ,context):
    doc=DocxTemplate(templ)
    doc.render(context)
    
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)

    main=Composer(docx.Document(mainP))
    appended=docx.Document(buffer)
    
    main.append(appended)
    main.save(mainP)

def clean_spaces(string):
    if not isinstance(string,str):
        return string
    string=string.strip()
    string=re.sub(r'\s+',' ',string)
    return string

def color_diff_visible(a, b,logger):
    # Replace the space character with a visible symbol (like '␣' or '·')
    for char in difflib.ndiff(a, b):
        # Determine the character to display
        display_char = '␣' if char[2] == ' ' else char[2]
        
        # Apply color based on the diff status
        if char[0] == '-':
            logger.info(f'\033[91m{display_char}\033[0m', end='')  # Red
        elif char[0] == '+':
            logger.info(f'\033[92m{display_char}\033[0m', end='')  # Green
        else:
            logger.info(display_char, end='')  # No color
    print()  # Newline at the end

def check_file(path,logger):
    clean=np.vectorize(clean_spaces)

    al=pd.read_excel(path / '3318.06' / 'Учет металлов.xlsx', skiprows=3,sheet_name='Алюминий')
    al=al.drop([0])
    al=al.drop(['Прибыло (т.)','Убыло (т.)','Состоит (т.)'],axis=1)
    al=al.set_index('№        документа')
    al=al.dropna(axis=1)

    fe=pd.read_excel(path / '3318.06' / 'Учет металлов.xlsx', skiprows=3,sheet_name='Черный металл (ЧМ)')
    fe=fe.drop([0])
    fe=fe.drop(['Прибыло (т.)','Убыло (т.)','Состоит (т.)'],axis=1)
    fe=fe.set_index('№        документа')
    fe=fe.dropna(axis=1)
    fe=fe.loc[al.index]

    str_col=['Наименование документа','Поставщик','Получатель']

    al[str_col]=clean(al[str_col])
    fe[str_col]=clean(fe[str_col])

    unmatch=(alv==fev)

    fed=fev[~unmatch].dropna(axis=1,thresh=1)
    fed=fed[~unmatch].dropna(axis=0,thresh=1)
    fed=fed.stack()

    ald=alv[~unmatch].dropna(axis=1,thresh=1)
    ald=ald[~unmatch].dropna(axis=0,thresh=1)
    ald=ald.stack()

    res=pd.concat([ald,fed],join='inner',axis=1)
    res.columns=['Железо', "Алюминий"]

    for row in res.index:
        logger.warning(row)
        color_diff_visible(res.loc[row,'Железо'], res.loc[row,'Алюминий'],logger)

def main():
    logging.basicConfig(filename='logs.log', level=logging.INFO,format='%(asctime)s %(levelname)s: %(message)s')
    logger = logging.getLogger(__name__)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    logger.addHandler(console_handler)

    path=Path('/mnt/c/Users/user/Desktop/учет МЕ Армада')
    path_tem=Path('/home/jul/projects/Sync docs/templates')

    if len(sys.argv)>1:
        main=(path / '554.727' / 'накладные' / 'НАКЛАДНАЯ Чистая 2.docx'
               if sys.argv[1]=='2' 
               else path / '3318.06' / 'накладные' / 'НАКЛАДНЫЕ.docx')
        templ=(path_tem / 'sample 2.docx'
               if sys.argv[1]=='2'
               else path_tem / 'sample 1.docx')
        source=(path / '554.727' / 'Учет металлов 2.xlsx'
                if sys.argv[1]=='2'
                else path / '3318.06' / 'Учет металлов.xlsx')
        back=int(sys.argv[2]) if len(sys.argv)==3 else 1
    else:
        main=path / '3318.06' / 'накладные' / 'НАКЛАДНЫЕ.docx'
        templ='../templates/sample 1.docx'
        source=path / '3318.06' / 'Учет металлов.xlsx'
        back=1

    df=pd.read_excel(source, skiprows=3)
    df=df.drop([0])
    df=df.drop(df.columns[9:14],axis=1)

    cars={
        'ООО «Армада» маз г.р.з. у 075кв 138':'Маз № У075КВ 138',
        'ООО «Армада» шангси г.р.з. а 595мт 03':'Шангси № А595МТ 03',
        'ООО «Армада» хино г.р.з. в 559вр 03':'Хино.№ В559ВР 03',
        'ООО «Армада» шахман г.р.з. с 389кн 57':'Шахман № С389КН 57',
        'ООО «Армада» фав г.р.з. е152вк 57':'Фав № Е152ВК 57',
        'ООО «Армада» камаз г.р.з. н 870кт 03':'Камаз № Н870КТ 03',
        'ООО «Армада» ивеко г.р.з. а700на 03':'Ивеко № А700НА 03',
        'ООО «Армада» мицубиси г.р.з. р 888вт 38':'Мицубиси № Р888ВТ 38',
        'ООО «Армада» вольво г.р.з. в 543ев 03':'Вольво № В543ЕВ 03',
        'ООО «Армада» камаз г.р.з. х 633рм 125':'Камаз № Х633РМ 125'
    }

    need=df[df["Дата записи"].isin(df['Дата записи'].unique()[-back:])]

    logger.info('----------------Start----------------')
    for index,row in need.iterrows():
        car=cars[clean_spaces(row['Получатель'])]
        date=row['Дата записи'].strftime('%d.%m.%Y')
        number=row['№        документа']
        logger.info(" ".join([date,number,car]))
        print(date,number,car)

        add_to_file(main,templ,
            {'number':f'{number}',
             'date':f'{date}',
             'car':f'{car}'})
    logger.info('----------------Finish--------------')
if __name__ == "__main__":
    main()

