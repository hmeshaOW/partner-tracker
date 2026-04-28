# Entra App Registration Setup

Automated app registration was attempted from Azure CLI but blocked by tenant policy:

- Error: `Insufficient privileges to complete the operation`
- Current signed-in tenant: `duboischemicals.com`

## Required App Registration

Create a Microsoft Entra **Single-page application (SPA)** with these values:

- Name: `partner-tracker-spa`
- Supported account types: `Accounts in any organizational directory (Multitenant)`
- Redirect URI type: `Single-page application (SPA)`
- Redirect URI: `http://localhost:5173`

## Required Microsoft Graph Delegated Permissions

- `User.Read`
- `Mail.Read`
- `Calendars.Read`

Grant user/admin consent as required by your tenant policy.

## Azure CLI Commands

If app registrations are enabled for your account, these commands are the intended flow:

```bash
az ad app create \
  --display-name partner-tracker-spa \
  --sign-in-audience AzureADMultipleOrgs \
  --web-redirect-uris http://localhost:5173

az ad app permission add \
  --id <APP_ID> \
  --api 00000003-0000-0000-c000-000000000000 \
  --api-permissions \
  e1fe6dd8-ba31-4d61-89e7-88639da4683d=Scope \
  570282fd-fa5c-430d-a7fd-fc8dc98a9dca=Scope \
  465a38f9-76ea-45b9-9f34-9e8b0d4b0b42=Scope
```

Permission IDs used above:

- `User.Read`: `e1fe6dd8-ba31-4d61-89e7-88639da4683d`
- `Mail.Read`: `570282fd-fa5c-430d-a7fd-fc8dc98a9dca`
- `Calendars.Read`: `465a38f9-76ea-45b9-9f34-9e8b0d4b0b42`

## Frontend Env

After registration, set these values in `frontend/.env`:

```bash
VITE_API_BASE_URL=http://localhost:8000
VITE_ENTRA_CLIENT_ID=<APP_ID>
VITE_ENTRA_TENANT_ID=common
VITE_ENTRA_REDIRECT_URI=http://localhost:5173
```
