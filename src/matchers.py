import pandas as pd
import logging
from abc import ABC, abstractmethod
from typing import Optional

# Setup logger for the matching pipeline
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def clean_issn(issn: any) -> Optional[str]:
    """
    Universal sanitation for ISSNs to guarantee a reliable join key.
    Removes hyphens, spaces, and handles variations of dash characters.
    """
    if pd.isna(issn):
        return None
    issn_str = str(issn).strip().upper()
    if issn_str in ["N/A", "#N/A", ""]:
        return None
    for char in ['-', '–', '—', '−', ' ']:
        issn_str = issn_str.replace(char, '')
    return issn_str


class BaseMatcher(ABC):
    """
    Abstract Base Class (Strategy Pattern) that defines the contract 
    for all publisher data cross-referencing strategies.
    """
    def __init__(self, sucupira_df: pd.DataFrame):
        self.sucupira_df = sucupira_df.copy()
        # Create a standardized matching column in the Sucupira base
        self.sucupira_df['issn_match'] = self.sucupira_df['ISSN'].apply(clean_issn)

    @abstractmethod
    def match(self, publisher_file_path: str) -> pd.DataFrame:
        """Executes the specific cross-referencing logic for a publisher."""
        pass


class ACMMatcher(BaseMatcher):
    def match(self, publisher_file_path: str) -> pd.DataFrame:
        df = pd.read_csv(publisher_file_path)
        df['issn_clean'] = df['ISSN'].apply(clean_issn)
        df['eissn_clean'] = df['eISSN'].apply(clean_issn)
        
        m1 = pd.merge(df, self.sucupira_df, left_on='issn_clean', right_on='issn_match', how='inner')
        m2 = pd.merge(df, self.sucupira_df, left_on='eissn_clean', right_on='issn_match', how='inner')
        
        combined = pd.concat([m1, m2]).drop_duplicates(subset=['Títulos'])
        # FIX: Matches 'Título' and 'Estrato' from your updated Sucupira structure
        return combined[['Título', 'ISSN_x', 'eISSN', 'Estrato']].rename(
            columns={'Título': 'Journal Title', 'ISSN_x': 'ISSN', 'Estrato': 'Qualis'}
        )


class IEEEMatcher(BaseMatcher):
    def match(self, publisher_file_path: str) -> pd.DataFrame:
        df = pd.read_csv(publisher_file_path)
        df['issn_clean'] = df['ISSN'].apply(clean_issn)
        df['eissn_clean'] = df['eISSN'].apply(clean_issn)
        
        m1 = pd.merge(df, self.sucupira_df, left_on='issn_clean', right_on='issn_match', how='inner')
        m2 = pd.merge(df, self.sucupira_df, left_on='eissn_clean', right_on='issn_match', how='inner')
        
        combined = pd.concat([m1, m2]).drop_duplicates(subset=['Publication Title'])
        # FIX: Matches 'Estrato' from your updated Sucupira structure
        return combined[['Publication Title', 'ISSN_x', 'eISSN', 'Estrato', 'Open Access Type']].rename(
            columns={'Publication Title': 'Journal Title', 'ISSN_x': 'ISSN', 'Estrato': 'Qualis', 'Open Access Type': 'Type'}
        )


class ElsevierMatcher(BaseMatcher):
    def match(self, publisher_file_path: str) -> pd.DataFrame:
        df = pd.read_csv(publisher_file_path)
        df['issn_clean'] = df['ISSN'].apply(clean_issn)
        
        matched = pd.merge(df, self.sucupira_df, left_on='issn_clean', right_on='issn_match', how='inner')
        # FIX: Matches 'Estrato' from your updated Sucupira structure
        return matched[['Journal Title', 'ISSN_x', 'Estrato', 'Status']].rename(
            columns={'ISSN_x': 'ISSN', 'Estrato': 'Qualis'}
        )


class SpringerMatcher(BaseMatcher):
    def match(self, publisher_file_path: str) -> pd.DataFrame:
        df = pd.read_csv(publisher_file_path)
        df = df[df['Publish'].str.contains('Publish', na=False, case=False)]
        df['eissn_clean'] = df['eISSN'].apply(clean_issn)
        
        matched = pd.merge(df, self.sucupira_df, left_on='eissn_clean', right_on='issn_match', how='inner')
        # FIX: Matches 'Estrato' from your updated Sucupira structure
        return matched[['Journal Title', 'eISSN', 'Estrato', 'Subject Area', 'Publishing Model']].rename(
            columns={'Estrato': 'Qualis', 'Subject Area': 'Field'}
        )


class WileyMatcher(BaseMatcher):
    def match(self, publisher_file_path: str) -> pd.DataFrame:
        df = pd.read_csv(publisher_file_path)
        df['eissn_clean'] = df['ESSN'].apply(clean_issn)
        
        matched = pd.merge(df, self.sucupira_df, left_on='eissn_clean', right_on='issn_match', how='inner')
        # FIX: Matches 'Estrato' from your updated Sucupira structure
        return matched[['TITULO', 'ESSN', 'Estrato', 'ÁREA PRINCIPAL']].rename(
            columns={'TITULO': 'Journal Title', 'ESSN': 'eISSN', 'Estrato': 'Qualis', 'ÁREA PRINCIPAL': 'Field'}
        )