import os
import logging
import pandas as pd
from typing import Optional

# Setup basic logging configuration for monitoring the data pipeline
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class QualisIngestor:
    """
    Responsible for handling and converting raw data exported from the CAPES/Sucupira platform.
    It standardizes the government's Excel (.xlsx) format into a clean, optimized internal CSV.
    """
    
    def __init__(self, output_dir: str = "data/processed"):
        self.output_dir = output_dir
        # Ensure the destination directory exists safely
        os.makedirs(self.output_dir, exist_ok=True)

    def convert_xlsx_to_csv(self, xlsx_path: str, target_filename: str = "sucupira_base.csv") -> Optional[str]:
        """
        Reads the raw Sucupira Excel file, cleans missing structural blocks, 
        and exports a structured CSV file using robust encoding.
        """
        if not os.path.exists(xlsx_path):
            logging.error(f"Input file not found at: {xlsx_path}")
            raise FileNotFoundError(f"The file {xlsx_path} does not exist.")

        try:
            logging.info(f"Starting to read Excel file: {xlsx_path}")
            
            # Engineering Note: Force ISSN as string to prevent Excel from dropping leading zeros.
            # We explicitly use the 'openpyxl' engine to read modern .xlsx formats.
            df = pd.read_excel(xlsx_path, dtype={'ISSN': str}, engine='openpyxl')
            
            # Data Sanitation: Drop rows that are completely empty (common in CAPES exports)
            df = df.dropna(how='all')
            
            # Define the absolute output path for the processed CSV
            csv_output_path = os.path.join(self.output_dir, target_filename)
            
            # Export to CSV using standard comma separator.
            # 'utf-8-sig' handles Brazilian special characters natively (like accents in Portuguese)
            df.to_csv(csv_output_path, index=False, encoding='utf-8-sig', sep=',')
            
            logging.info(f"Successfully converted and saved at: {csv_output_path}")
            return csv_output_path

        except Exception as e:
            logging.error(f"Critical failure during xlsx conversion for {xlsx_path}: {str(e)}")
            raise e