
from datetime import datetime
from discord_webhook import AsyncDiscordWebhook, DiscordEmbed
from Utils.Tools import SingletonClass


class NotifyDiscord(metaclass = SingletonClass):
    def __init__(self) -> None:
        self.basic_data = {
            "link": "https://www.alphacast.io/",
            "imagen": "https://pbs.twimg.com/profile_images/1625214683765415946/oc2EQE_B_400x400.jpg",
            "footer": " | AlphaCast By Campos Nicolas",
            "color": "EC0E5F"
        }

# ---------- Control Notifys ----------
    # --- Error Logs ---
    async def webhook_control_error(self,
        company:dict[str, str], 
        problem_logs:str,
        URL_Webhook:str = None
    ):
        webhook = AsyncDiscordWebhook(
            url = URL_Webhook if URL_Webhook else company['url_webhook_error'],
            avatar_url = self.basic_data["imagen"],
            username = company['name'].capitalize(),
            rate_limit_retry = True
        )
        embed = DiscordEmbed(
            title = f'Error Fatal: {company["name"]}',
            url = company["link"],
            color = self.basic_data["color"]
        )
        embed.set_author(
            name = self.basic_data['link'],
            icon_url = self.basic_data["imagen"],
        )
        embed.set_footer(
            text = company['name'].capitalize() + self.basic_data["footer"],
            icon_url = self.basic_data["imagen"]
        )
        embed.set_timestamp()

        embed.set_thumbnail(
            url = self.basic_data["imagen"]
        )
        embed.add_embed_field(
            name = 'Info. Log:', 
            value = f'```{problem_logs}```',
            inline = False
        )
        try:
            webhook.add_embed(embed)
            await webhook.execute()
            return True, f'Error Webhook Was Send Successfully | Message: {problem_logs}'
        
        except Exception as err:
            return False, f'Error Webhook Reporting Failures, Could Not Deliver Embed | Message: {problem_logs} | Error: {err}'


    # --- Success Logs ---
    async def webhook_control_success(self,
        company:dict[str, str], 
        dataset_data:dict[str, any],
        URL_Webhook:str = None
    ):
        webhook = AsyncDiscordWebhook(
            url = URL_Webhook if URL_Webhook else company['url_webhook_success'],
            avatar_url = self.basic_data["imagen"],
            username = company['name'].capitalize(),
            rate_limit_retry = True
        )
        embed = DiscordEmbed(
            title = f'New Dataset Successfully Loaded',
            description = f'New dataset added to repository, check details below...',
            url = dataset_data["dataset_link"],
            color = self.basic_data["color"]
        )
        embed.set_author(
            name = self.basic_data['link'],
            icon_url = self.basic_data["imagen"],
        )
        embed.set_footer(
            text = company['name'].capitalize() + self.basic_data["footer"],
            icon_url = self.basic_data["imagen"]
        )
        embed.set_timestamp()

        embed.set_thumbnail(
            url = self.basic_data["imagen"]
        )

        embed.add_embed_field(
            name = 'DataSet ID: ', 
            value = f"`{dataset_data["dataset_id"]}`"
        )
        embed.add_embed_field(
            name = 'WebSite: ', 
            value = f'[{company["name"]}]({company["link"]})'
        )
        embed.add_embed_field(
            name = 'API Response: ', 
            value = f'```{dataset_data["api_response"]}```',
            inline = False
        )

        try:
            webhook.add_embed(embed)
            await webhook.execute()
            return True, f'New Dataset Notification Sent Successfully'
        
        except Exception as err:
            return False, f'Error Reporting a New Dataset, Webhook Not Be Delivered... | Error: {err}'