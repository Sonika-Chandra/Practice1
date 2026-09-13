def list_message_ids(service, max_results=20, query="assignment OR homework OR due"):
    results = service.users().messages().list(
        userId='me',
        maxResults=max_results,
        q=query
    ).execute()
    
    messages = results.get('messages', [])
    return messages
def fetch_full_messages(service, message_ids):
    full_messages = []
    for msg_id_dict in message_ids:
        msg_id = msg_id_dict['id']
        full_msg = service.users().messages().get(userId='me', id=msg_id).execute()
        parsed = parse_message(full_msg)
        full_messages.append(parsed)
    return full_messages