import { PublicClientApplication } from "@azure/msal-browser";

const envClientId = import.meta.env.VITE_ENTRA_CLIENT_ID;
const envTenantId = import.meta.env.VITE_ENTRA_TENANT_ID || "common";
const envRedirectUri = import.meta.env.VITE_ENTRA_REDIRECT_URI || window.location.origin;
const scopes = ["User.Read", "Mail.Read", "Calendars.Read"];

let msalInstance: PublicClientApplication | null = null;
let msalConfigFingerprint = "";

export interface MicrosoftAuthRuntimeConfig {
  clientId: string;
  tenantId?: string;
  redirectUri?: string;
}

function resolveConfig(runtimeConfig?: MicrosoftAuthRuntimeConfig) {
  const clientId = (runtimeConfig?.clientId || envClientId || "").trim();
  const tenantId = (runtimeConfig?.tenantId || envTenantId || "common").trim();
  const redirectUri = (runtimeConfig?.redirectUri || envRedirectUri || window.location.origin).trim();
  return { clientId, tenantId, redirectUri };
}

function getInstance(runtimeConfig?: MicrosoftAuthRuntimeConfig) {
  const { clientId, tenantId, redirectUri } = resolveConfig(runtimeConfig);
  if (!clientId) {
    throw new Error("Missing Microsoft Client ID. Provide Entra app settings in the runtime login prompt.");
  }

  const fingerprint = `${clientId}|${tenantId}|${redirectUri}`;
  if (!msalInstance || msalConfigFingerprint !== fingerprint) {
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
    msalConfigFingerprint = fingerprint;
  }

  return msalInstance;
}

export function hasMicrosoftLoginConfig(runtimeConfig?: MicrosoftAuthRuntimeConfig) {
  return Boolean(resolveConfig(runtimeConfig).clientId);
}

export async function loginAndAcquireGraphToken(runtimeConfig?: MicrosoftAuthRuntimeConfig) {
  const instance = getInstance(runtimeConfig);
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
