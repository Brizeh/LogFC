import json

from requests.models import Response
from typing import Optional, Dict, Any


class Log:
    """
    Represents a log file of a GW2 encounter.
    Stores URLs and JSON data extracted from the log.
    """

    def __init__(self, url: str):
        """
        Initializes a Log object.

        Args:
            url: The URL of the log on dps.report
        """
        self.url: str = url
        self.jcontent: Optional[Dict[str, Any]] = None
        self.pjcontent: Optional[Dict[str, Any]] = None

    def set_jcontent(self, response: Optional[Response]) -> None:
        """
        Sets the main JSON content of the log.

        Args:
            response: The HTTP response containing the JSON data
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
        Sets the JSON content of the log metadata.

        Args:
            response: The HTTP response containing the JSON data
        """
        if response and response.ok:
            # Directly load the JSON from the response content
            self.pjcontent = response.json()
        else:
            status = response.status_code if response else "No response"
            print(f"Error during log metadata download: {status}")

    def __repr__(self) -> str:
        """Text representation of the Log object."""
        return f"Log({self.url})"
