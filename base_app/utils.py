import xml.etree.ElementTree as ET
from xml.dom import minidom

prefix_type_order = {1: 'CustPicking', 0: 'VendReceipt'}


def data_to_dict(df):
    dic_order = {}
    name_col = 'SalesId'
    if 'SalesId' in df.columns:
        name_col = 'SalesId'
    elif 'PurchId' in df.columns:
        name_col = 'PurchId'
    elif 'Quantity' in df.columns:
        name_col = 'ItemId'
    elif 'CustVendID' in df.columns:
        name_col = 'CustVendID'
    for i in df[name_col]:
        dic_order[i] = None
    for key in dic_order.keys():
        _df = df[df[name_col] == key].copy()
        dic_order[key] = _df.to_dict('index')
    return dic_order


# def start_client(data: dict, key_contract):
#     key_contract = __update_name_contract(key_contract)
#     global contract
#     contract = contracts[str(key_contract)]
#     type_order = 'CustVendTable'
#     const_name = f'{str(type_order)}ExportDC'
#     _dt = __create_datetime()
#     new = ET.Element('AxaptaXMLExport')
#     x = str("urn:www.navision.com/Formats/Table")
#     y = str("1.0")
#     new.attrib = {'xmlns:Table': x, 'version': y}
#     title = ET.SubElement(new, 'transaction')
#     title.attrib = {'version': y}
#     for key, value in data.items():
#         title1 = ET.SubElement(title, 'Table:Record')
#         title1.attrib = {'name': const_name, 'row': str(key + 1)}
#         for k, v in value.items():
#             row = ET.SubElement(title1, 'Table:Field')
#             row.attrib = {'name': k}
#             row.text = str(v)
#     save_file_name = __create_name_file_save(str(_dt), str(type_order))
#     __save_xml(save_file_name, new)


def save_to_xml(data: dict, type_order, contract):
    for k1, v1 in data.items():
        const_name = f'{str(type_order)}ExportDC'
        new = ET.Element('AxaptaXMLExport')
        x = str("urn:www.navision.com/Formats/Table")
        y = str("1.0")
        new.attrib = {'xmlns:Table': x, 'version': y}
        title = ET.SubElement(new, 'transaction')
        title.attrib = {'version': y}
        for key, value in data[k1].items():
            title1 = ET.SubElement(title, 'Table:Record')
            title1.attrib = {'name': const_name, 'row': str(key + 1)}
            for k, v in value.items():
                row = ET.SubElement(title1, 'Table:Field')
                row.attrib = {'name': k}
                row.text = str(v)
        save_file_name = __create_name_file_save(str(k1), str(type_order), contract)
        __save_xml(save_file_name, new)


def __update_name_contract(__str_contract):
    __contract = __str_contract.split('.')[1]
    return __contract


def __create_date():
    import datetime
    _dt = datetime.datetime.now().date() + datetime.timedelta(days=1)
    _dt = str(_dt)
    return _dt


def __create_datetime():
    import datetime
    _dt = datetime.datetime.now()
    _dt = _dt.strftime("%Y%m%d-%H%M%S")
    _dt = str(_dt)
    return _dt


def __create_name_file_save(filename, const_name, contract):
    import os
    dt = __create_date()
    wb_path = contract.path_saved_order
    # os.path.join — кроссплатформенный путь (работает на Windows и Linux)
    _path = os.path.join(wb_path, f'{const_name}_{filename}_{dt}.xml')
    return _path


def __save_xml(filename, xml_code):
    xml_string = ET.tostring(xml_code).decode()
    xml_prettyxml = minidom.parseString(xml_string).toprettyxml()
    with open(filename, 'w', encoding='utf-8') as xml_file:
        xml_file.write(xml_prettyxml)
