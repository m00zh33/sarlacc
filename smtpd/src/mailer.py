import email
import re


class MailHandler:
    def __init__(self, store):
        self.store = store


    async def handle_DATA(self, server, session, envelope):
        subject = ""
        toAddressList = envelope.rcpt_tos
        fromAddress = envelope.mail_from
        body = None
        attachments = []
        filename = None
        dateSent = datetime.now()

        # parse message
        try:
            message = email.message_from_string(envelope.content.decode("utf8", errors="replace"))
            subject = message["subject"]
            if message.is_multipart():
                for part in message.get_payload():
                    if "Content-Disposition" in part and "attachment;" in part["Content-Disposition"]:
                        matches = re.findall(r'filename=".*"', part["Content-Disposition"])
                        if len(matches) > 0:
                            a = matches[0].index('"')
                            b = matches[0].index('"', a + 1)
                            fileName = matches[0][a + 1:b]
                            content = part.get_payload()
                            attachments.append({
                                "content": content,
                                "fileName": fileName})
                    elif "Content-Type" in part and "text/plain" in part["Content-Type"]:
                        body = part.get_payload()
            else:
                # This is gross
                if "Content-Disposition" in message and "attachment;" in message["Content-Disposition"]:
                    matches = re.findall(r'filename=".*"', message["Content-Disposition"])
                    if len(matches) > 0:
                        a = matches[0].index('"')
                        b = matches[0].index('"', a + 1)
                        fileName = matches[0][a + 1:b]
                        content = message.get_payload()
                        attachments.append({
                            "content": content,
                            "fileName": fileName})
                elif "Content-Type" in message and "text/plain" in message["Content-Type"]:
                    body = message.get_payload()

            asyncio.ensure_future(self.store.store_email(
                subject = subject,
                toAddressList = toAddressList,
                fromAddress = fromAddress,
                body = body,
                attachments = attachments,
                dateSent = dateSent))

        except:
            print("crashed when parsing email.. lol")

        return "250 Message accepted for delivery"