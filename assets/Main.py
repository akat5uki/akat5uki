import requests
import sys

QOT_CONTENT = r"{{QuoteContent}}"
QOT_AUTHOR = r"{{QuoteContent}}"
EXT_JSON = "json"

class MyExecption(Exception):
    pass

class QuoteAPI:
    def __init__(self, urls):
        self.urls = urls

    def get_quote(self):
        for url in self.urls:
            try:
                response = requests.get(url["URL"], timeout=5)
                response.raise_for_status()
                quote = response.json()
                return quote[url["QOT"]], quote[url["AUT"]]
            except requests.exceptions.RequestException as e:
                continue
            except KeyError as e:
                return None, "Could not retrieve quote. Unexpected JSON format: " + str(e)
            except Exception as e:
                return None, "An unexpected error occurred: " + str(e)
        return None, "Could not retrieve quote. All API servers are down."

class FileHandler:
    def __init__(self, file_name):
        self.file_name = file_name

    def read_file(self):
        try:
            with open(self.file_name, "r") as f:
                return f.read()
        except FileNotFoundError as e:
            return None, "Could not open file: " + str(e)
        except Exception as e:
            return None, "An unexpected error occurred: " + str(e)

    def read_json_file(self):
        try:
            fname, fext = (self.file_name).split(".")
            if fext.lower() != EXT_JSON:
                raise MyExecption()
            with open(self.file_name, "r") as f:
                data = json.load(f)
                return data
        except FileNotFoundError as e:
            return None, "Could not open file: " + str(e)
        except json.JSONDecodeError as e:
            return None, "Could not parse JSON: " + str(e)
        except MyExecption as e:
            return None, "Wrong file type, not JSON"
        except Exception as e:
            return None, "An unexpected error occurred: " + str(e)

    def write_file(self, contents):
        try:
            with open(self.file_name, "w") as f:
                f.write(contents)
                f.close()
            return True, "File written successfully."
        except Exception as e:
            return False, "Could not write to file: " + str(e)

if len(sys.argv) != 4:
    print("Usage: python program.py urls.txt template.txt result.txt")
else:
    urls_file_name, template_file_name, result_file_name = sys.argv[1:]
    urls_file = FileHandler(urls_file_name)
    urls_result = urls_file.read_json_file()
    if isinstance(urls_result, tuple):
        success, message = urls_result
        print(message)
    else:
        urls = urls_result
        quote_api = QuoteAPI(urls)
        quote_result = quote_api.get_quote()
        if isinstance(quote_result, tuple):
            quote, author = quote_result
            if quote and author:
                template_file = FileHandler(template_file_name)
                template_result = template_file.read_file()
                if isinstance(template_result, tuple):
                    success, message = template_result
                    print(message)
                else:
                    contents = template_result
                    contents = contents.replace(QOT_CONTENT, quote)
                    contents = contents.replace(QOT_AUTHOR, author)

                    result_file = FileHandler(result_file_name)
                    file_write_result = result_file.write_file(contents)
                    success, message = file_write_result
                    print(message)
            else:
                print(author)