from tavily import TavilyClient

class DiseaseInformation:
    def __init__(self, api_key):
        """
        Initialize the DiseaseInformation class with a Tavily API key.
        
        Args:
            api_key (str): Tavily API key for authentication
        """
        self.client = TavilyClient(api_key)
    
    def search_disease(self, disease_name):
        """
        Search for comprehensive information about a specific disease.
        
        Args:
            disease_name (str): Name of the disease to search for
            
        Returns:
            dict: The search results from Tavily API
        """
        if not disease_name:
            raise ValueError("Disease name cannot be empty")
        
        query = f"{disease_name} risks symptoms diagnosis treatment prevention prognosis latest research"
        response = self.client.search(query=query)
        return response