import requests
import json
from typing import Dict, List, Optional

class KingCountyVoterAPI:
    def __init__(self, app_token: str):
        """
        Initialize the King County Voter API client
        
        Args:
            app_token (str): Your Socrata API token
        """
        self.base_url = "https://data.kingcounty.gov"
        self.headers = {
            'X-App-Token': app_token,
            'Content-Type': 'application/json'
        }
    
    def get_election_results(self, dataset_id: str, params: Optional[Dict] = None) -> Dict:
        """
        Get election results from a specific dataset
        
        Args:
            dataset_id (str): The Socrata dataset identifier
            params (dict): Query parameters for filtering results
            
        Returns:
            dict: JSON response from the API
        """
        url = f"{self.base_url}/resource/{dataset_id}.json"
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data: {e}")
            return None
    
    def get_voter_info(self, precinct: str) -> Dict:
        """
        Get voter information for a specific precinct
        
        Args:
            precinct (str): Precinct identifier
            
        Returns:
            dict: Voter information for the precinct
        """
        params = {
            '$where': f"precinct='{precinct}'",
            '$limit': 1000
        }
        # Note: You'll need to replace with the correct dataset ID
        return self.get_election_results('dataset-id-here', params)
    
    def get_presidential_results(self, year: int) -> Dict:
        """
        Get presidential election results for a specific year
        
        Args:
            year (int): Election year
            
        Returns:
            dict: Presidential election results
        """
        # Map of known dataset IDs for presidential elections
        dataset_map = {
            2008: 'av7y-ibxs',  # Example ID - replace with actual
            # Add more years as needed
        }
        
        if year not in dataset_map:
            raise ValueError(f"No dataset available for year {year}")
            
        return self.get_election_results(dataset_map[year])

# Example usage
def main():
    # Initialize the API client
    app_token = "YOUR_APP_TOKEN_HERE"
    api = KingCountyVoterAPI(app_token)
    
    # Example: Get 2008 presidential results
    results = api.get_presidential_results(2008)
    
    if results:
        # Process and format the results
        formatted_results = {
            "Election Year": 2008,
            "State": "Washington",
            "County": "King",
            "Democratic Votes": sum(int(r['votes']) for r in results if 'Obama' in r.get('candidate', '')),
            "Republican Votes": sum(int(r['votes']) for r in results if 'McCain' in r.get('candidate', '')),
        }
        print(json.dumps(formatted_results, indent=2))

if __name__ == "__main__":
    main()