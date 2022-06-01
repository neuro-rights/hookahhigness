import ipfshttpclient
import json
from typing import Type, Union, Dict, Any, List
import requests
import os
from pathlib import Path


class IPFSUtils:
    """

    Attributes
    ----------

    Methods
    -------
    """

    def __init__(self):
        """Class init"""
        self._client = ipfshttpclient.connect(session=True)

    def upload_directory_to_ipfs(self, art_directory_path):
        # Share TCP connections using a context manager
        self._client.add(art_directory_path, recursive=True)
        print(self._client.stat(hash))
        return hash

    def upload_files_in_directory_to_ipfs(self, art_directory, file_pattern):
        self._client.add(art_directory, pattern=file_pattern)
        return hash

    # Call this when your done
    def close_ipfs(self):
        self._client.close()

    def infura_ipfs_upload(self, file_to_upload):
        # upload to ipfs or whatever
        files = {"file": file_to_upload}
        #
        response = requests.post(
            "https://ipfs.infura.io:5001/api/v0/add",
            files=files,
            auth=(os.environ["INFURA_IPFS_PROJECT_ID"], os.environ["INFURA_IPFS_SECRET_KEY"]),
        )
        #
        res = json.loads(response.text)
        url = "https://ipfs.infura.io/ipfs/" + res["Hash"]
        print("url: " + url)
        return url

    def pinata_ipfs_upload(self, file_to_upload):
        """ """
        # Connect to the IPFS cloud service
        pinata_api_key = str(os.environ.get("PinataAPIKey"))
        pinata_secret_api_key = str(os.environ.get("PinataAPISecret"))
        pinata = PinataPy(pinata_api_key, pinata_secret_api_key)
        # Upload the file
        result = pinata.pin_file_to_ipfs("markdown.md")
        # Should return the CID (unique identifier) of the file
        print(result)
        # Anything waiting to be done?
        print(pinata.pin_jobs())
        # List of items we have pinned so far
        print(pinata.pin_list())
        # Total data in use
        print(pinata.user_pinned_data_total())
        # Get our pinned item
        # gateway="https://gateway.pinata.cloud/ipfs/"
        gateway = "https://ipfs.io/ipfs/"
        print(requests.get(url=gateway + result["IpfsHash"]).text)
        print(gateway + result["IpfsHash"])

    def pinJSONToIPFS(self, json_obj: Dict[str, Any], pinata_api_key: str, pinata_secret: str) -> Dict[str, Any]:
        """
        Purpose:
            PIN a json obj to IPFS
        Args:
            json_obj - The json obj
            pinata_api_key - pinata api key
            pinata_secret - pinata secret key
        Returns:
            ipfs json - data from pin
        """
        HEADERS = {
            "pinata_api_key": pinata_api_key,
            "pinata_secret_api_key": pinata_secret,
        }

        ipfs_json = {
            "pinataMetadata": {
                "name": json_obj["name"],
            },
            "pinataContent": json_obj,
        }

        endpoint_uri = "https://api.pinata.cloud/pinning/pinJSONToIPFS"
        response = requests.post(endpoint_uri, headers=HEADERS, json=ipfs_json)
        return response.json()

    def pinContentToIPFS(self, filepath: str, pinata_api_key: str, pinata_secret: str) -> Dict[str, Any]:
        """
        Purpose:
            PIN a file obj to IPFS
        Args:
            filepath - file path
            pinata_api_key - pinata api key
            pinata_secret - pinata secret key
        Returns:
            ipfs json - data from pin
        """

        HEADERS = {
            "pinata_api_key": pinata_api_key,
            "pinata_secret_api_key": pinata_secret,
        }

        endpoint_uri = "https://api.pinata.cloud/pinning/pinFileToIPFS"

        filename = filepath.split("/")[-1:][0]

        with Path(filepath).open("rb") as fp:
            image_binary = fp.read()
            response = requests.post(endpoint_uri, files={"file": (filename, image_binary)}, headers=HEADERS)
            print(response.json())

            # response = requests.post(endpoint_uri, data=multipart_form_data, headers=HEADERS)
            # print(response.text)
            # print(response.headers)
            return response.json()

    def pinSearch(self, query: str, pinata_api_key: str, pinata_secret: str) -> List[Dict[str, Any]]:
        """
        Purpose:
            Query pins for data
        Args:
            query - the query str
            pinata_api_key - pinata api key
            pinata_secret - pinata secret key
        Returns:
            data - array of pined objects
        """

        endpoint_uri = f"https://api.pinata.cloud/data/pinList?{query}"
        HEADERS = {
            "pinata_api_key": pinata_api_key,
            "pinata_secret_api_key": pinata_secret,
        }
        response = requests.get(endpoint_uri, headers=HEADERS).json()

        # now get the actual data from this
        data = []
        if "rows" in response:

            for item in response["rows"]:
                ipfs_pin_hash = item["ipfs_pin_hash"]
                hash_data = requests.get(f"https://gateway.pinata.cloud/ipfs/{ipfs_pin_hash}").json()
                data.append(hash_data)

        # print(response.json())
        return data
