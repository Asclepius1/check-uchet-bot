
import asyncio
import easyocr
import gspread
import dateparser

from dotenv import load_dotenv
import os
load_dotenv()


class GoogleSheetService:
    def __init__(self):
        self.sheet_id = os.getenv("GOOGLE_SHEET_ID")
        self.credentials = os.getenv("SERVICE_ACCOUNT")
        self.gc = gspread.service_account(self.credentials)
        self.sheet = self.gc.open_by_key(self.sheet_id).sheet1
    
    def append_row(self, data: list[str]):
        self.sheet.append_row(data)

gsheet = GoogleSheetService()


def get_date_from_text(text: str) -> int | None:
    # Пытаемся распарсить дату из текста
    parsed = dateparser.parse(text, languages=["ru"])
    if parsed:
        return parsed.date().strftime("%d.%m.%Y")
    return text

reader = None

def get_reader():
    global reader
    if reader is None:
        reader = easyocr.Reader(['ru', 'en'], gpu=False, verbose=False)
    return reader

async def extract_texts_from_photo(path: str) -> dict[str, str]:
    # reader = easyocr.Reader(['en','ru']) # this needs to run only once to load the model into memory
    result: list[str] = reader.readtext(path, detail=0)
    data = {
        'payment_type': 'Неизвестно',
    }
    for i, line in enumerate(result):
        line = line.lower()
        try:
            if 'успешно' in line or 'сумма' in line:
                
                data['sum_'] = result[i+1].lower().replace(' ', '').replace('т', '').replace('₸', '').replace('o', '0').replace('о', '0')
                if data['sum_'][-1] == '7' or not data['sum_'][-1].isdigit():
                    data['sum_'] = data['sum_'][:-1]
            if 'дата' in line or 'счет выставлен' in line:
                if 'г' in result[i+1]:
                    date = result[i+1].split('г')[0].strip()
                    data['date'] = get_date_from_text(date)
                else:
                    data['date'] = result[i+1].replace(',', '.').lstrip().split(' ')[0].strip().replace('o', '0').replace('о', '0')
            if data['payment_type'] == 'Неизвестно':
                if 'kaspi' in line or ('детали оплаты' in line and 'сумма' in result[i+1].lower()):
                    data['payment_type'] = 'Kaspi'
                elif 'halyk' in line:
                    data['payment_type'] = 'Halyk'
        except IndexError:
            continue
    os.remove(path)
    return data

async def upload_to_google_sheet(data: dict[str, str]) -> None:
    result = [
        data.get("fio", "-"),
        data.get("sum_", "-"),
        data.get("date", "-"),
        data.get("payment_type", "-"),
        data.get("user", "-"),
    ]
    
    gsheet.append_row(result)




if __name__ == "__main__":
    # test = asyncio.run(extract_texts_from_photo("checks/photo_2025-10-15_00-58-39.jpg"))
    # print(test)
    print(get_date_from_text('25 сентября 2025'))