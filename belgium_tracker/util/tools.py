# coding: utf-8


def month_fr_to_numbers(mois):
    MOIS = {'janvier': '01',
            'février': '02',
            'mars': '03',
            'avril': '04',
            'mai': '05',
            'juin': '06',
            'juillet': '07',
            'août': '08',
            'septembre': '09',
            'octobre': '10',
            'novembre': '11',
            'décembre': '12'}
    return MOIS.get(mois, 'NOT FOUND')
