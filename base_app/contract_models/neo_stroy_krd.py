import datetime

import pandas as pd
from base_app.utils import data_to_dict, save_to_xml

# Константы по филиалу — только чтение, не изменяются во время работы
_CONST_KRD = {'id_sklad': '16718149', 'id_client': '16718173', 'id_postav': '16718148',
               'delivery_type': 2, 'id_inspection': '16720118'}
_CONST_SOCHI = {'id_sklad': '16718318', 'id_client': '16718173', 'id_postav': '16718148',
                'delivery_type': 2, 'id_inspection': '16720118'}
_CONST_RND = {'id_sklad': '17017234', 'id_client': '17017253', 'id_postav': '17017238',
              'delivery_type': 2, 'id_inspection': '17011254'}

# Индексы колонок Excel (0-based) — при изменении структуры Excel обновить здесь
COL_DOC_NUM = 1      # номер документа
COL_ITEM_CODE = 6    # код товара
COL_ITEM_NAME = 5    # наименование товара
COL_ITEM_UNIT = 7    # ед. изм.
COL_COMMENT = 11     # комментарий
COL_QTY_PORDER = 50  # приход
COL_QTY_ORDER = 51   # расход
COL_QTY_ENGINEER = 52  # инженерный доступ


def start(file_name, contract):
    """Обработка Excel-заявки. Возвращает (dic_log, error_flag)."""
    # Выбираем константы филиала — создаём копию, чтобы не менять оригинал
    if contract.name == 'Волга-М_Сочи(Сбер)':
        dic_const = dict(_CONST_SOCHI)
    elif contract.name == 'Нео-Строй(Ростов)':
        dic_const = dict(_CONST_RND)
    else:
        dic_const = dict(_CONST_KRD)

    dic_log = {'Расход': 0, 'Приход': 0, 'Доступы': 0, 'Справочник товаров': 0}

    try:
        _df_order, _df_porder, _df_engineer = __load_parse_file(file_name)

        if len(_df_order) > 0:
            __create_order(_df_order, contract, dic_const, COL_QTY_ORDER, dic_log, engineer=False)

        if len(_df_porder) > 0:
            __create_porder(_df_porder, contract, dic_const, COL_QTY_PORDER, dic_log, engineer=False)
            __create_product(_df_porder, contract, dic_log)

        if len(_df_engineer) > 0:
            # Для инженерного доступа — клиент и поставщик = inspection
            dic_const_eng = dict(dic_const)
            dic_const_eng['id_client'] = dic_const['id_inspection']
            dic_const_eng['id_postav'] = dic_const['id_inspection']
            __create_order(_df_engineer, contract, dic_const_eng, COL_QTY_ENGINEER, dic_log, engineer=True)
            __create_porder(_df_engineer, contract, dic_const_eng, COL_QTY_ENGINEER, dic_log, engineer=True)

        if len(_df_order) == 0 and len(_df_porder) == 0 and len(_df_engineer) == 0:
            return {
                'Ошибка: должно быть заполнено одно из полей — '
                '6.2 Приёмка, 6.3 Отгрузка или 6.4 Перемещение': 1
            }, False

        return dic_log, False

    except Exception as exc:
        return {'error': str(exc)}, True


def __load_parse_file(_wb_file):
    _df = pd.read_excel(_wb_file)
    _df.drop(index=[0], inplace=True)
    _df.dropna(subset=_df.columns[COL_DOC_NUM], inplace=True)
    _df.reset_index(drop=True, inplace=True)
    dt = __create_datetime()
    _df[_df.columns[COL_ITEM_CODE]] = _df[_df.columns[COL_ITEM_CODE]].astype(str).str.replace("'", '')
    _df[_df.columns[COL_ITEM_NAME]] = _df[_df.columns[COL_ITEM_NAME]].astype(str).str.replace("'", '')
    _df[_df.columns[COL_DOC_NUM]] = (
        _df[_df.columns[COL_DOC_NUM]].astype(str)
        .str.replace('б/н', dt)
        .str.replace(r'б\н', dt, regex=False)
    )
    _df = _df.fillna(0)
    _df[_df.columns[COL_QTY_ORDER]] = _df[_df.columns[COL_QTY_ORDER]].astype(int)
    _df[_df.columns[COL_QTY_PORDER]] = _df[_df.columns[COL_QTY_PORDER]].astype(int)
    _df[_df.columns[COL_QTY_ENGINEER]] = _df[_df.columns[COL_QTY_ENGINEER]].astype(int)
    _df_order = _df[_df[_df.columns[COL_QTY_ORDER]] > 0].copy()
    _df_porder = _df[_df[_df.columns[COL_QTY_PORDER]] > 0].copy()
    _df_engineer = _df[_df[_df.columns[COL_QTY_ENGINEER]] > 0].copy()
    return _df_order, _df_porder, _df_engineer


def __create_datetime():
    _dt = datetime.datetime.now() + datetime.timedelta(days=1)
    return _dt.strftime("%Y%m%d-%H%M%S")


def __create_datetime_order():
    _dt = datetime.datetime.now() + datetime.timedelta(days=1)
    return _dt.strftime("%Y-%m-%d")


def __create_order(_df, contract, dic_const, col_qty, dic_log, engineer):
    df_order = pd.DataFrame()
    df_order['SalesId'] = _df[_df.columns[COL_DOC_NUM]]
    df_order['InventLocationId'] = dic_const['id_sklad']
    df_order['ConsigneeAccount'] = dic_const['id_client']
    df_order['DeliveryDate'] = __create_datetime_order()
    df_order['ManDate'] = __create_datetime_order()
    df_order['Itemid'] = _df[_df.columns[COL_ITEM_CODE]]
    df_order['Qty'] = _df[_df.columns[col_qty]]
    df_order['SalesUnit'] = 'шт'
    df_order['Delivery'] = dic_const['delivery_type']
    df_order['Redelivery'] = 1
    df_order['OrderType'] = 1
    df_order['Comment'] = _df[_df.columns[COL_COMMENT]]
    dic_order = data_to_dict(df_order)
    save_to_xml(dic_order, 'CustPicking', contract=contract)
    if engineer:
        dic_log['Доступы'] += len(dic_order)
    else:
        dic_log['Расход'] += len(dic_order)


def __create_porder(_df, contract, dic_const, col_qty, dic_log, engineer):
    df_porder = pd.DataFrame()
    df_porder['Itemid'] = _df[_df.columns[COL_ITEM_CODE]]
    df_porder['Qty'] = _df[_df.columns[col_qty]]
    df_porder['PurchId'] = _df[_df.columns[COL_DOC_NUM]]
    df_porder['VendAccount'] = dic_const['id_postav']
    df_porder['DeliveryDate'] = __create_datetime_order()
    df_porder['InventLocationId'] = dic_const['id_sklad']
    df_porder['ProductionDate'] = '01-01-2023'
    df_porder['PurchUnit'] = 'шт'
    df_porder['PurchTTN'] = 1
    df_porder['Price'] = 1
    dic_porder = data_to_dict(df_porder)
    save_to_xml(dic_porder, 'VendReceipt', contract=contract)
    if engineer:
        dic_log['Доступы'] += len(dic_porder)
    else:
        dic_log['Приход'] += len(dic_porder)


def __create_product(_df, contract, dic_log):
    df_product = pd.DataFrame()
    df_product['ItemId'] = _df[_df.columns[COL_ITEM_CODE]]
    df_product['ItemName'] = (
        _df[_df.columns[COL_ITEM_NAME]].astype(str) + '_' +
        _df[_df.columns[COL_ITEM_UNIT]].astype(str)
    )
    # Габариты и веса — константы по умолчанию; вынести в ContractConfig при необходимости
    for field in ('NetWeight', 'NetWeightBox', 'NetWeightPack',
                  'BruttoWeight', 'BruttoWeightBox', 'BruttoWeightPack'):
        df_product[field] = 500
    df_product['Quantity'] = 1
    df_product['standardShowBoxQuantity'] = 1
    df_product['UnitId'] = 'шт'
    for field in ('Depth', 'BoxDepth', 'BlockDepth'):
        df_product[field] = 1200
    for field in ('Height', 'BoxHeight', 'BlockHeight'):
        df_product[field] = 1800
    for field in ('Width', 'BoxWidth', 'BlockWidth'):
        df_product[field] = 800
    df_product['StandardPalletQuantity'] = 1
    df_product['QtyPerLayer'] = 1
    df_product['Price'] = 1
    df_product['ShelfLife'] = 1095
    barcode_col = _df[_df.columns[COL_ITEM_NAME]]
    for field in ('EanBarcode', 'EanBarcodeBox', 'EanBarcodePack',
                  'Gs1Barcode', 'Gs1BarcodeBox', 'Gs1BarcodePack'):
        df_product[field] = barcode_col
    dic_product = data_to_dict(df_product)
    save_to_xml(dic_product, 'InventTable', contract=contract)
    dic_log['Справочник товаров'] += len(dic_product)

