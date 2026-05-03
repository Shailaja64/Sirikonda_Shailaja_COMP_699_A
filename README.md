# Barcode Governance & Risk Intelligence System (BGRIS)

## Overview

BGRIS is a Python-based offline system used to process barcode images, check compliance rules, and calculate risk scores. It is designed for warehouse and logistics environments where barcode accuracy is important.

The system allows users to upload images, decode barcodes, handle damaged barcodes, evaluate compliance, and generate reports. All actions are recorded for tracking and transparency.

---

## Features

- Upload single or multiple product images  
- Image preprocessing (rotation, noise removal, contrast adjustment)  
- Barcode decoding  
- Reconstruction of damaged barcodes  
- Compliance rule evaluation  
- Risk score calculation  
- Report generation (JSON / CSV)  
- Audit logging  
- Works completely offline  

---

## Technologies Used

- Python  
- Streamlit  
- OpenCV  
- Pillow  
- Pyzbar  
- Pytesseract  

---

## Installation

Run the following command to install all required libraries:

```

pip install streamlit opencv-python pillow pyzbar pytesseract

```

---

## Project Structure

```

bgris.py        -> Main application file
data/           -> Input and processed images
logs/           -> Audit logs
reports/        -> Generated reports
rules/          -> Compliance rule files

```

---

## How to Run

1. Install Python (3.x recommended)  
2. Install dependencies using the command above  
3. Run the application:

```

streamlit run bgris.py

```

4. Open the browser link shown in terminal  

---

## Example Workflow

1. Upload image or batch  
2. Preprocess image  
3. Decode barcode  
4. Reconstruct if needed  
5. Apply compliance rules  
6. Calculate risk score  
7. View results and export report  

---

## Unit Testing

Basic unit tests are included for:

- Barcode decoding  
- Rule validation  
- Risk calculation  
- Logging  

Run tests using:

```

python bgris.py

```

---

## Key Design Points

- Fully offline system  
- Simple and modular design  
- Easy to extend with new rules  
- Audit tracking for all actions  

---

## Limitations

- Basic barcode reconstruction  
- Limited UI customization  
- No advanced analytics or dashboards  

---

## Future Improvements

- Advanced reconstruction algorithms  
- Better UI design  
- Interactive dashboards  
- Enhanced rule engine  

---

## Conclusion

BGRIS helps in improving barcode accuracy, ensuring compliance, and reducing operational risk. It simplifies barcode processing and supports better decision-making in warehouse environments.
