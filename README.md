# 📊 Qualtrics Survey Reports Automated Pipeline

This project automates the creation of visual reports from survey data collected using Qualtrics. The pipeline connects to the Qualtrics server, processes raw data, handles transformation logic, and generates PDF reports categorized by response type (complete, student-only, or supervisor-only).

---

## 🚀 Features

- Connects to Qualtrics API to fetch survey data
- Cleans and transforms raw survey responses
- Maintains traceable data folders for raw, intermediate, and processed results
- Categorizes data based on respondent availability
- Generates PDF reports per case type with visual summaries

---

## 🛠 Tech Stack

- Python 3.x
- Pandas
- Matplotlib
- FPDF
- Python-dotenv (for environment configuration)

---

## 📂 Project Structure

```
Qualtrics_Survey_Reports_Automated_Pipeline/
├── .env                     # Environment configuration for API keys
├── data_extraction.py       # Logic for fetching and saving raw data
├── report_generation.py     # Logic for generating reports
├── raw_data/                # Downloaded raw data files
├── intermediate_data/       # Intermediate transformation files for traceability
├── processed_data/          # Final cleaned & separated datasets
├── outputs/                 # Generated PDF reports
├── main.py                  # Pipeline controller script
├── requirements.txt         # Python package dependencies
└── README.md                # Project documentation
```

---

## ⚙️ Installation & Setup

1. **Clone the Repository**
```bash
git clone https://github.com/pzinzuvadia/Qualtrics_Survey_Reports_Automated_Pipeline.git
cd Qualtrics_Survey_Reports_Automated_Pipeline
```

2. **Create and Configure `.env` File**
Create a `.env` file in the root directory:
```env
QUALTRICS_API_TOKEN=your_token_here
QUALTRICS_DATA_CENTER_ID=your_data_center
```

3. **Create Virtual Environment (Optional)**
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

4. **Install Dependencies**
```bash
pip install -r requirements.txt
```

---

## ▶️ How to Use

1. Place your Qualtrics API credentials in the `.env` file.
2. Run the script:
```bash
python main.py
```
3. Raw data will be saved in `raw_data/`.
4. Cleaned and transformed data will be separated into:
   - `processed_data/complete_records/`
   - `processed_data/only_students/`
   - `processed_data/only_supervisors/`
5. PDF reports will be generated in the `outputs/` directory based on data type.

---

## 🔁 Workflow and Code Breakdown

### **main.py**
- Controls the entire pipeline flow.
- Loads environment variables.
- Imports and runs functions from `data_extraction.py` and `report_generation.py`.
- Coordinates raw data extraction, transformation, and reporting.

### **data_extraction.py**

#### `extract_data_from_qualtrics()`
- Connects to the Qualtrics API.
- Downloads and saves raw survey data to `raw_data/`.

#### `clean_and_transform_data()`
- Performs data cleaning and structuring.
- Saves intermediate states to `intermediate_data/` for debugging or audit.
- Outputs cleaned files to `processed_data/` based on data completeness:
  - **complete_records**: Both student and supervisor responses present
  - **only_students**: Only student responses available
  - **only_supervisors**: Only supervisor responses available

### **report_generation.py**

#### `generate_pdf_report(file_path, respondent_type)`
- Reads cleaned data
- Generates bar charts for responses using matplotlib
- Creates a multi-page PDF using FPDF
- Stores output in the `outputs/` directory

---

## 📝 Input/Output Summary

### Input:
- Survey data fetched from Qualtrics (CSV format)
- `.env` file for secure API key access

### Output:
- PDF reports per case type: complete, only students, only supervisors

---

## 🔧 Future Enhancements

- [ ] Add support for different chart types
- [ ] Allow custom report templates or branding
- [ ] Export reports to other formats (HTML, Excel)

---

## 👤 Author

**Priyansh Zinzuvadia**  
[LinkedIn](https://www.linkedin.com/in/pszinzuvadia) • [GitHub](https://github.com/pzinzuvadia)

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

