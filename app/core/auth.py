import requests
from dotenv import load_dotenv
import msal
from app.core.credentials import get_client_id

load_dotenv()


class MicrosoftAuth:
    AUTHORITY = "https://login.microsoftonline.com/consumers"
    SCOPE = ["XboxLive.signin", "XboxLive.offline_access"]
    
    def __init__(self):
        self.client_id = get_client_id()
        if not self.client_id:
            raise ValueError("Microsoft login not available - CLIENT_ID not configured")
        self.app = msal.PublicClientApplication(client_id=self.client_id, authority=self.AUTHORITY)
        self.session = requests.Session()

    def start_device_flow(self):
        flow = self.app.initiate_device_flow(scopes=self.SCOPE)
        if "user_code" not in flow:
            raise Exception(f"Failed: {flow.get('error_description', 'Unknown')}")
        return flow

    def complete_device_flow(self, flow):
        result = self.app.acquire_token_by_device_flow(flow)
        if "access_token" not in result:
            raise Exception(f"Failed: {result.get('error_description', result.get('error', 'Unknown'))}")
        return result

    def authenticate_xbox_live(self, access_token):
        resp = self.session.post(
            "https://user.auth.xboxlive.com/user/authenticate",
            json={
                "Properties": {"AuthMethod": "RPS", "SiteName": "user.auth.xboxlive.com", "RpsTicket": f"d={access_token}"},
                "RelyingParty": "http://auth.xboxlive.com",
                "TokenType": "JWT"
            },
            headers={"Content-Type": "application/json"}
        )
        if resp.status_code != 200:
            raise Exception(f"XBL failed: {resp.text}")
        data = resp.json()
        return data["Token"], data["DisplayClaims"]["xui"][0]["uhs"]

    def authenticate_xsts(self, xbl_token):
        resp = self.session.post(
            "https://xsts.auth.xboxlive.com/xsts/authorize",
            json={
                "Properties": {"SandboxId": "RETAIL", "UserTokens": [xbl_token]},
                "RelyingParty": "rp://api.minecraftservices.com/",
                "TokenType": "JWT"
            },
            headers={"Content-Type": "application/json"}
        )
        if resp.status_code == 401:
            xerr = resp.json().get("XErr", 0)
            errors = {
                2148916233: "No Xbox account",
                2148916235: "Region blocked",
                2148916238: "Under 18 - needs Family group"
            }
            raise Exception(errors.get(xerr, f"XSTS failed: {resp.text}"))
        if resp.status_code != 200:
            raise Exception(f"XSTS failed: {resp.text}")
        return resp.json()["Token"]

    def authenticate_minecraft(self, user_hash, xsts_token):
        resp = self.session.post(
            "https://api.minecraftservices.com/authentication/login_with_xbox",
            json={"identityToken": f"XBL3.0 x={user_hash};{xsts_token}"}
        )
        if resp.status_code != 200:
            raise Exception(f"MC auth failed: {resp.text}")
        return resp.json()["access_token"]

    def get_profile(self, mc_token):
        resp = self.session.get(
            "https://api.minecraftservices.com/minecraft/profile",
            headers={"Authorization": f"Bearer {mc_token}"}
        )
        if resp.status_code == 404:
            raise Exception("Account doesn't own Minecraft Java")
        if resp.status_code != 200:
            raise Exception(f"Profile failed: {resp.text}")
        return resp.json()

    def complete_auth(self, ms_token):
        xbl_token, user_hash = self.authenticate_xbox_live(ms_token)
        xsts_token = self.authenticate_xsts(xbl_token)
        mc_token = self.authenticate_minecraft(user_hash, xsts_token)
        profile = self.get_profile(mc_token)
        profile["access_token"] = mc_token
        return profile
