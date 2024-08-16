def verify(self, agent_name: str, address:str) -> str:
    """
    Verify connection with an agent and return the response value.

    :param agent_name: The name of the agent
    :type agent_name: str
    :param address: The address hostname:port to be sent to the API.
    :type address: str
    :return: The response from the API as a string.
    :rtype: str
    :raises requests.HTTPError: If the request to the API returns a status code indicating an error.
    :raises requests.RequestException: If there is an error making the request.

    Example usage:
    verify("isp_hr_expert", "localhost:8898")
    """
    import requests

    api_url = f'http://{address}/api/v1/verify'

    response = requests.get(api_url)
    return response.text