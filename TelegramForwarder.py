import time
import asyncio
import os
from telethon.sync import TelegramClient
from telethon import errors

class TelegramForwarder:
    def __init__(self):
        # Get credentials from environment variables
        self.api_id = os.getenv('API_ID')
        self.api_hash = os.getenv('API_HASH')
        self.phone_number = os.getenv('PHONE_NUMBER')
        self.source_chat_id = int(os.getenv('SOURCE_CHAT_ID', '0'))
        self.destination_chat_id = int(os.getenv('DESTINATION_CHAT_ID', '0'))
        self.keywords = os.getenv('KEYWORDS', '').split(',') if os.getenv('KEYWORDS') else []
        
        # Initialize client
        self.client = TelegramClient('session_file', self.api_id, self.api_hash)

    async def start_forwarding(self):
        await self.client.connect()

        # Ensure you're authorized
        if not await self.client.is_user_authorized():
            await self.client.send_code_request(self.phone_number)
            verification_code = os.getenv('VERIFICATION_CODE')
            if verification_code:
                await self.client.sign_in(self.phone_number, verification_code)
            else:
                print("Please set the VERIFICATION_CODE environment variable")
                return

        last_message_id = (await self.client.get_messages(self.source_chat_id, limit=1))[0].id

        while True:
            print("Checking for messages and forwarding them...")
            messages = await self.client.get_messages(
                self.source_chat_id, 
                min_id=last_message_id, 
                limit=None
            )

            for message in reversed(messages):
                if message.text:
                    if not self.keywords or any(keyword.strip().lower() in message.text.lower() for keyword in self.keywords):
                        print(f"Forwarding message: {message.text[:50]}...")
                        await self.client.send_message(self.destination_chat_id, message.text)
                        print("Message forwarded successfully")

                last_message_id = max(last_message_id, message.id)

            await asyncio.sleep(5)

async def main():
    forwarder = TelegramForwarder()
    await forwarder.start_forwarding()

if __name__ == "__main__":
    asyncio.run(main())
