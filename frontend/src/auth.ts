import { PublicClientApplication } from "@azure/msal-browser";

const clientId = import.meta.env.VITE_ENTRA_CLIENT_ID;
const tenantId = import.meta.env.VITE_ENTRA_TENANT_ID || "common";
const redirectUri = import.meta.env.VITE_ENTRA_REDIRECT_URI || window.location.origin;
const scopes = ["User.Read", "Mail.Read", "Calendars.Read"];

let msalInstance: PublicClientApplication | null = null;

function getInstance() {
  if (!clientId) {
    throw new Error("Missing VITE_ENTRA_CLIENT_ID. Configure frontend Entra settings to use Microsoft login.");
  }

  if (!msalInstance) {
    msalInstance = new PublicClientApplication({
      auth: {
        clientId,
        authority: `https://login.microsoftonline.com/${tenantId}`,
        redirectUri,
      },
      cache: {
        cacheLocation: "sessionStorage",
      },
    });
  }

  return msalInstance;
}

export function hasMicrosoftLoginConfig() {
  return Boolean(clientId);
}

export async function loginAndAcquireGraphToken() {
  const instance = getInstance();
  await instance.initialize();

  let account = instance.getActiveAccount() ?? instance.getAllAccounts()[0] ?? null;
  if (!account) {
    const loginResult = await instance.loginPopup({ scopes });
    account = loginResult.account;
  }

  if (!account) {
    throw new Error("Microsoft sign-in did not return an account.");
  }

  instance.setActiveAccount(account);

  try {
    const tokenResult = await instance.acquireTokenSilent({ account, scopes });
    return {
      accessToken: tokenResult.accessToken,
      accountName: account.name || account.username,
    };
  } catch {
    const tokenResult = await instance.acquireTokenPopup({ account, scopes });
    return {
      accessToken: tokenResult.accessToken,
      accountName: account.name || account.username,
    };
  }
}
