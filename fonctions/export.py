from io import BytesIO
import pandas as pd


def export_workbook(sheets):
    """Readable, filterable Excel sheets without a technical DataFrame index."""
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter',
                        engine_kwargs={'options': {'strings_to_formulas': False, 'strings_to_urls': False}}) as writer:
        for name, data in sheets.items():
            data.to_excel(writer, sheet_name=name, index=False)
            sheet = writer.sheets[name]
            sheet.freeze_panes(1, 0)
            sheet.hide_gridlines(2)
            if not data.empty:
                sheet.add_table(0, 0, len(data), len(data.columns)-1,
                                {'columns': [{'header': str(c)} for c in data.columns], 'style': 'Table Style Medium 2'})
            for index, column in enumerate(data.columns):
                values = data[column]
                width = min(48, max(14, len(str(column))+2, max((len(str(v)) for v in values), default=0)+2))
                fmt = {'valign': 'top', 'text_wrap': True}
                if pd.api.types.is_numeric_dtype(values):
                    fmt['num_format'] = '0' if pd.api.types.is_integer_dtype(values) else '0.00'
                sheet.set_column(index, index, width, writer.book.add_format(fmt))
    return output.getvalue()

def export_excel(data, name_index, sheet_name):

    output = BytesIO()
    # https://xlsxwriter.readthedocs.io/working_with_pandas.html

    # Pour travailler avec xlswriter et pendas et faire des tableaux, il faut reset l'index
    data = data.reset_index()
    data.rename(columns={'index': name_index}, inplace=True)

    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    data.to_excel(
        writer, startrow=1, sheet_name=sheet_name, index=False, header=False)

    workbook = writer.book
    worksheet1 = writer.sheets[sheet_name]

    # Gestion de la taille des colonnes

    cell_format = workbook.add_format({'valign': 'vcenter', 'align': 'center'})
    cell_format.set_text_wrap()
    for i, col in enumerate(data.columns):
        # colonne, colonne, len_colonne, format colonne
        worksheet1.set_column(i, i+1, 20, cell_format)

    # Tableau

    def tableau(data, worksheet):
        column_settings = [{'header': column} for column in data.columns]
        (max_row, max_col) = data.shape

        worksheet.add_table(0, 0, max_row, max_col-1,
                            {'columns': column_settings})

    if not data.empty:
        tableau(data, worksheet1)
    else:
        worksheet1.write_row(0, 0, [str(c) for c in data.columns])

    writer.close()

    processed_data = output.getvalue()

    return processed_data
