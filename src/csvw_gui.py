import sys
import os
import datetime
import webbrowser
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QGridLayout, QHBoxLayout, QLabel, QPushButton, QFileDialog, QRadioButton, QTextEdit
try:
    # git install
    from converter.csvw import CSVWConverter, build_schema, extensions
except ImportError:
    # pip install
    from cow_csvw.converter.csvw import CSVWConverter, build_schema, extensions

from rdflib import ConjunctiveGraph

COW_WIKI = "https://github.com/CLARIAH/COW/wiki"

class COWGUI(QMainWindow):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.setWindowTitle('CSV on the Web Converter')
        self.setGeometry(100, 100, 400, 300)  # Adjusted for additional button

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        layout = QGridLayout()

        self.file_button = QPushButton('Select CSV File(s)')
        self.file_button.clicked.connect(self.browse_files)
        layout.addWidget(self.file_button, 1, 0, 1, 2)

        self.process_button = QPushButton('Build Metadata File')
        self.process_button.clicked.connect(self.build_schemas)
        layout.addWidget(self.process_button, 2, 0)

        # Button for editing the JSON file
        self.edit_button = QPushButton('Customize Metadata File')
        self.edit_button.clicked.connect(self.edit_json)
        layout.addWidget(self.edit_button, 2, 1)

        self.process_button = QPushButton('Convert CSV File(s)')
        self.process_button.clicked.connect(self.convert_files)
        layout.addWidget(self.process_button, 3, 0, 1, 2)


        self.output_text_edit = QTextEdit()
        layout.addWidget(self.output_text_edit, 4, 0, 1, 2)

        self.process_button = QPushButton('Help')
        self.process_button.clicked.connect(self.wiki)
        layout.addWidget(self.process_button, 5, 0)

        self.process_button = QPushButton('Exit')
        self.process_button.clicked.connect(self.quit)
        layout.addWidget(self.process_button, 5, 1)

        self.output_text_edit.append("Welcome to COW!\n\nStart by selecting one or"
                                     " more CSV files. Next, click 'build' to"
                                     " generate a metadata file with"
                                     " mappings, and finally click 'convert' to"
                                     " translate your data to RDF.\n")

        self.central_widget.setLayout(layout)

        self.files = []

    def wiki(self):
        webbrowser.open(COW_WIKI)

    def quit(self):
        sys.exit(0)

    def browse_files(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly

        file_dialog = QFileDialog()
        file_dialog.setNameFilter('CSV Files (*.csv)')
        selected_files, _ = file_dialog.getOpenFileNames(self, caption='Select CSV File(s)',
                                                         filter='CSV Files (*.csv);;All Files (*)',
                                                         options=options)
        if selected_files:
            self.files = selected_files
            self.output_text_edit.append(f"Added the files {', '.join(self.files)}")

    def build_schemas(self):
        if not self.files:
            self.output_text_edit.append("No files selected.")
            return

        for file in self.files:
            self.output_text_edit.append(f"Building schema for {file}")
            target_file = f"{file}-metadata.json"

            if os.path.exists(target_file):
                new_filename = f"{os.path.splitext(target_file)[0]}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.json"
                os.rename(target_file, new_filename)
                self.output_text_edit.append(f"Backed up prior version of schema to {new_filename}")

            build_schema(file, target_file, dataset_name=None, delimiter=None, encoding=None, quotechar='\"', base="https://example.com/id/")
            self.output_text_edit.append(f"Schema built and saved as {target_file}")

    def convert_files(self):
        if not self.files:
            self.output_text_edit.append("No files selected.")
            return

        for file in self.files:
            self.output_text_edit.append(f"Converting {file} to RDF")
            try:
                c = CSVWConverter(file, delimiter= None , quotechar='\"', encoding= None , processes=4, chunksize=5000, output_format='nquads', base="https://example.com/id/")
                c.convert()

                quads_filename = f"{file}.nq"
                new_filename = f"{os.path.splitext(file)[0]}.rdf"

                with open(quads_filename, 'rb') as nquads_file:
                    g = ConjunctiveGraph()
                    g.parse(nquads_file, format='nquads')

                with open(new_filename, 'wb') as output_file:
                    g.serialize(destination=output_file, format='xml')

                self.output_text_edit.append(f"Conversion completed and saved as {new_filename}")

            except Exception as e:
                self.output_text_edit.append(f"Something went wrong while processing {file}: {str(e)}")

    def edit_json(self):
        if not self.files:
            self.output_text_edit.append("No CSV files selected to search for JSON metadata files.")
            return

        for file_path in self.files:
            base_name = os.path.basename(file_path) 
            json_file_name = f"{base_name}-metadata.json"  
            print(json_file_name)
            json_file_path = os.path.join(os.path.dirname(file_path), json_file_name)
            print(json_file_path)
            if os.path.isfile(json_file_path): 
                # Open the JSON file in the default editor for the OS
                if sys.platform.startswith('darwin'):
                    os.system(f'open -e "{json_file_path}"')
                elif os.name == 'nt':  # For Windows
                    os.startfile(json_file_path)
                elif os.name == 'posix':  # For Linux, Unix, etc.
                    os.system(f'xdg-open "{json_file_path}"')
                self.output_text_edit.append(f"Opened {json_file_path} for editing")
                return  
            
        # If the loop completes without opening a JSON file, then no JSON file was found
        self.output_text_edit.append("No corresponding JSON metadata file found for the selected CSV files.")

def main():
    app = QApplication(sys.argv)
    gui = COWGUI()
    gui.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
