def ask_to(self, session_id: str, question: str, address:str) -> str:
    """
    Ask a question to an agent and return the response value.

    :param session_id: The current session in your memory: the session_id value
    :type session_id: str
    :param question: The question to be sent to the API.
    :type question: str
    :param address: The address hostname:port to be sent to the API.
    :type address: str
    :return: The response from the API as a string.
    :rtype: str
    :raises requests.HTTPError: If the request to the API returns a status code indicating an error.
    :raises requests.RequestException: If there is an error making the request.

    Example usage:
    ask_to("e36c57e6-2251-438e-8aa5-bf8b11b14e06", "isp_hr_expert", "What is the vacation policy?", "localhost:8898")
    """
    import requests
    #TODO install agentbuddy in memgpt image
    # from agentbuddy.agent.client import AgentClient

    # client = AgentClient(base_url=address)
    # return client.ask(question=question,session_id=session_id)

    api_url = f'http://{address}/api/v1/ask'
    params = {'session_id': session_id, 'question': question}

    response = requests.get(api_url, params=params)
    return response.text