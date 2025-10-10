import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.worksheet.datavalidation import DataValidation
import pandas as pd


########################
# Excel formatting
########################
def create_excel(df, excel_path):
    main_df = df[df["Zájem"] != "NE"].copy()
    removed_df = df[df["Zájem"] == "NE"].copy()
    with pd.ExcelWriter(excel_path, engine="openpyxl") as writer:
        main_df.to_excel(writer, sheet_name="Hlavní", index=False)
        removed_df.to_excel(writer, sheet_name="Vyřazené", index=False)
    wb = openpyxl.load_workbook(excel_path)
    for sheet_name in ["Hlavní", "Vyřazené"]:
        ws = wb[sheet_name]
        url_col = None
        for idx, cell in enumerate(ws[1], 1):
            if cell.value == "URL":
                url_col = idx
                break
        if url_col:
            col_letter = openpyxl.utils.get_column_letter(url_col)
            for row in range(2, ws.max_row + 1):
                cell = ws[f"{col_letter}{row}"]
                if (
                    cell.value
                    and isinstance(cell.value, str)
                    and cell.value.startswith("http")
                ):
                    cell.hyperlink = cell.value
                    cell.style = "Hyperlink"
        header_font = Font(bold=True, color="FFFFFF")
        header_fill = PatternFill("solid", fgColor="4F81BD")
        odd_fill = PatternFill("solid", fgColor="DCE6F1")
        even_fill = PatternFill("solid", fgColor="FFFFFF")
        for cell in ws[1]:
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = Alignment(
                horizontal="center", vertical="center", wrap_text=True
            )
        for i, row in enumerate(ws.iter_rows(min_row=2, max_row=ws.max_row), start=2):
            fill = odd_fill if i % 2 else even_fill
            for cell in row:
                cell.fill = fill
                cell.alignment = Alignment(wrap_text=True, vertical="top")
            ws.row_dimensions[i].height = 30
        for col in ws.columns:
            max_length = 0
            col_letter = col[0].column_letter
            for cell in col:
                try:
                    cell_length = len(str(cell.value))
                    if cell_length > max_length:
                        max_length = cell_length
                except:
                    pass
            ws.column_dimensions[col_letter].width = max(15, min(max_length + 2, 50))
        interest_col = None
        for idx, cell in enumerate(ws[1], 1):
            if cell.value == "Zájem":
                interest_col = idx
                break
        if interest_col:
            try:
                col_letter = openpyxl.utils.get_column_letter(interest_col)
                dv = DataValidation(type="list", formula1='"ANO,NE"', allow_blank=True)
                ws.add_data_validation(dv)
                dv.add(f"{col_letter}2:{col_letter}{ws.max_row}")
            except Exception as e:
                print(f"Error adding data validation: {e}")
    wb.save(excel_path)
