<!-- Repo  
https://github.com/degu0055/25S_CST8919_Assignment_1  
to push git push azure main:master -->

# Flask Auth0 Azure Monitoring Setup

## Setup Steps

### Auth0
- Create an Auth0 tenant and configure an application.
- Set allowed callback URLs and logout URLs to your Azure Web App URLs.
- Get your Auth0 Domain, Client ID, and Client Secret.

### Azure
- Deploy your Flask app to Azure App Service.
- Configure Azure Log Analytics workspace.
- Connect your App Service logs to the Log Analytics workspace.

### .env File
Create a `.env` file with the following environment variables:

```
APP_SECRET_KEY=your_flask_secret_key
AUTH0_CLIENT_ID=your_auth0_client_id
AUTH0_CLIENT_SECRET=your_auth0_client_secret
AUTH0_DOMAIN=your_auth0_domain
APP_SECRET_KEY=your_secret
```

---

## Logging and Detection Logic

- The Flask app logs user login events and accesses to the `/protected` route.
- Logs include user ID, name, IP address, and timestamp.
- Azure Monitor captures these logs through AppServiceConsoleLogs.
- We use a Kusto Query Language (KQL) query to detect users accessing `/protected` more than 10 times in 15 minutes.

---

## KQL Query

```kql
AppServiceConsoleLogs
| where TimeGenerated > ago(15m)
| where ResultDescription has "event=authorized_access" and ResultDescription has "path=/protected"
| extend user_id = extract(@"user_id=([^\s,]+)", 1, ResultDescription)
| extend name = extract(@"name=\"([^\"]+)\"", 1, ResultDescription)
| extend timestamp = extract(@"timestamp=([^\s,]+)", 1, ResultDescription)
| summarize access_count = count(), latest_timestamp = max(timestamp) by user_id, name
| where access_count > 10
| project user_id, name, latest_timestamp, access_count
| order by access_count desc
```

---

## Alert Logic

- Azure Monitor Alert triggers when any user accesses `/protected` more than 10 times in 15 minutes.
- Alert severity is set to 3 (Low).
- **Note:** Action Group email notification was skipped due to restrictions on creating Action Groups.

---

## Demo

This is the demo:  
**https://drive.google.com/file/d/1VpM_rDh9D0fv5iK5f2TEbrNQntZdFh-m/view?usp=sharing**

**Important Note:**  
Since I cannot create an Action Group, the email notification is **not shown** in the video.

---

This setup helps monitor user access patterns and detect possible abuse or suspicious behavior in your Flask Auth0 app hosted on Azure.
