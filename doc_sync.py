from lib.utils import *
from lib.excel_word import *

from pathlib import Path
import sys
        
def main():
    logger=configure_logger()
    logger.info('----------------Start----------------')

    config=load_config('config.json')
    defaults=config['defaults']

    args=sys.argv[1:]
    if len(args)>=1:
        defaults[:len(args)]=args
    back=defaults[0]
    table_path=defaults[1]
    naclad_path=defaults[2]

    path_tem = Path(__file__).resolve().parent / 'templates' / 'cont 1 af.docx'
    
    metal=Metals_table(table_path,config['Fe_name'],config['sciprows'],config['col_numb'])
    metal.check_file()

    fe_page=metal.fe_page
    fe_page=fe_page[fe_page["Дата записи"].isin(fe_page['Дата записи'].unique()[-back:])]
    if len(fe_page)>0:
        logger.info(f'Writing {len(fe_page)} накладных')
    for index,row in fe_page.iterrows():
        car=config['cars'][clean_spaces(row['Получатель'])]
        date=row['Дата записи'].strftime('%d.%m.%Y')
        number=str(index)     
        logger.info(" ".join([date,number,car]))

        add_to_file(naclad_path,path_tem,
            {'number':f'{number}',
             'date':f'{date}',
             'car':f'{car}'})
    logger.info('----------------Finish--------------')
if __name__ == "__main__":
    main()

