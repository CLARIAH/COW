import sys
import os
import datetime
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFileDialog, QRadioButton, QTextEdit
try:
    # git install
    from converter.csvw import CSVWConverter, build_schema, extensions
except ImportError:
    # pip install
    from cow_csvw.converter.csvw import CSVWConverter, build_schema, extensions

from rdflib import ConjunctiveGraph

class COWGUI(QMainWindow):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.setWindowTitle('CSV on the Web Converter GUI')
        self.setGeometry(100, 100, 400, 300)  # Adjusted for additional button

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        layout = QVBoxLayout()

        self.mode_label = QLabel('Select Mode:')
        layout.addWidget(self.mode_label)

        self.mode_radio_layout = QHBoxLayout()
        self.mode_radio_build = QRadioButton('Build')
        self.mode_radio_convert = QRadioButton('Convert')
        self.mode_radio_build.setChecked(True)
        self.mode_radio_layout.addWidget(self.mode_radio_build)
        self.mode_radio_layout.addWidget(self.mode_radio_convert)
        layout.addLayout(self.mode_radio_layout)

        self.file_label = QLabel('Select File:')
        layout.addWidget(self.file_label)

        self.file_button = QPushButton('Browse Files')
        self.file_button.clicked.connect(self.browse_files)
        layout.addWidget(self.file_button)

        self.process_button = QPushButton('Build/Convert')
        self.process_button.clicked.connect(self.process_files)
        layout.addWidget(self.process_button)

        # Button for editing the JSON file
        self.edit_button = QPushButton('Edit JSON')
        self.edit_button.clicked.connect(self.edit_json)
        layout.addWidget(self.edit_button)

        self.output_text_edit = QTextEdit()
        layout.addWidget(self.output_text_edit)

        self.central_widget.setLayout(layout)

        self.files = []
        self.mode = 'build'  # Default mode

    def browse_files(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        options |= QFileDialog.ExistingFiles
        file_dialog = QFileDialog()
        file_dialog.setNameFilter('CSV Files (*.csv)')
        selected_files, _ = file_dialog.getOpenFileNames(self, 'Select CSV File(s)', '', 'CSV Files (*.csv);;All Files (*)', options=options)
        if selected_files:
            self.files = selected_files
            self.output_text_edit.append(f"Added the files {', '.join(self.files)}")

    def process_files(self):
        if not self.files:
            self.output_text_edit.append("No files selected.")
            return

        # Determine the mode based on the selected radio button
        self.mode = 'convert' if self.mode_radio_convert.isChecked() else 'build'

        # Execute the appropriate method based on the mode
        if self.mode == 'build':
            self.build_schemas()
        elif self.mode == 'convert':
            self.convert_files()

    def build_schemas(self):
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
