from io import BytesIO
import pandas as pd

def export_excel(data, name_index, sheet_name):

    output = BytesIO()
    # https://xlsxwriter.readthedocs.io/working_with_pandas.html

    # Pour travailler avec xlswriter et pendas et faire des tableaux, il faut reset l'index
    data.reset_index(inplace=True)
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

    tableau(data, worksheet1)

    writer.save()

    processed_data = output.getvalue()

    return processed_data