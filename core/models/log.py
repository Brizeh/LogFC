import json

from requests.models import Response
from typing import Optional, Dict, Any


class Log:
    """
    Représente un fichier log d'une rencontre GW2.
    Stocke les URLs et les données JSON extraites du log.
    """

    def __init__(self, url: str):
        """
        Initialise un objet Log.

        Args:
            url: L'URL du log sur dps.report
        """
        self.url: str = url
        self.jcontent: Optional[Dict[str, Any]] = None
        self.pjcontent: Optional[Dict[str, Any]] = None

    def set_jcontent(self, response: Optional[Response]) -> None:
        """
        Définit le contenu JSON principal du log.
        
        Args:
            response: La réponse HTTP contenant les données JSON
        """
        if response and response.ok:
            # Get the whole content from the response
            content = response.content.decode("utf-8")

            # Extract the JSON from the response
            java_data_text = content.split('var _logData = ')[1].split('var logData = _logData;')[0].rsplit(';', 1)[
                0].strip()

            # Load the JSON
            self.jcontent = json.loads(java_data_text)
        else:
            status = response.status_code if response else "No response"
            print(f"Error during log download: {status}")

    def set_pjcontent(self, response: Optional[Response]) -> None:
        """
        Définit le contenu JSON des métadonnées du log.
        
        Args:
            response: La réponse HTTP contenant les données JSON
        """
        if response and response.ok:
            # Directly load the JSON from the response content
            self.pjcontent = response.json()
        else:
            status = response.status_code if response else "No response"
            print(f"Error during log metadata download: {status}")


    def __repr__(self) -> str:
        """Représentation textuelle de l'objet Log."""
        return f"Log({self.url})"
