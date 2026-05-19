/**
 * Microsoft Entra ID (Azure AD) MSAL configuration.
 *
 * Values come from Vite env vars — set them in your .env file:
 *   VITE_AZURE_CLIENT_ID  → Application (Client) ID from the App Registration
 *   VITE_AZURE_TENANT_ID  → Directory (Tenant) ID from the App Registration
 */

import { PublicClientApplication, type Configuration } from "@azure/msal-browser";

const clientId = import.meta.env.VITE_AZURE_CLIENT_ID as string | undefined;
const tenantId = import.meta.env.VITE_AZURE_TENANT_ID as string | undefined;

if (!clientId || !tenantId) {
  console.warn(
    "[MSAL] VITE_AZURE_CLIENT_ID or VITE_AZURE_TENANT_ID is not set. " +
      "SSO login will not work until these are configured."
  );
}

const msalConfig: Configuration = {
  auth: {
    clientId: clientId ?? "",
    authority: `https://login.microsoftonline.com/${tenantId ?? "common"}`,
    redirectUri: window.location.origin,
  },
  cache: {
    cacheLocation: "sessionStorage",
  },
};

/** Singleton MSAL instance — import this everywhere you need SSO. */
export const msalInstance = new PublicClientApplication(msalConfig);

/** Scopes requested during SSO — minimum needed to get email + name. */
export const loginRequest = {
  scopes: ["openid", "profile", "email"],
};
